import contextlib
import logging
import os
import time
from collections.abc import AsyncIterator
from typing import Any

import mcp.types as types
import uvicorn
from dotenv import load_dotenv
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

# Import prompts
from prompts.award_type_codes import (
    prompt_award_type_codes_guide,
    prompt_message_award_type_codes_guide,
)
from prompts.general_guidance import (
    prompt_general_guidance,
    prompt_message_general_guidance,
)

# Import resources
from resources.award_type_codes import (
    award_type_groups,
    resource_award_type_codes,
)
from resources.award_type_codes import (
    resource_name as resource_name_award_type_codes,
)
from resources.toptier_agencies import (
    get_toptier_agencies,
    resource_toptier_agencies,
)
from resources.toptier_agencies import (
    resource_name as resource_name_toptier_agencies,
)

# Import tools
from tools.config import TOOLS

load_dotenv()
logger = logging.getLogger(__name__)
HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Deployment hardening configuration. Defaults are safe for local use;
# override via environment for a hosted (e.g. AWS Lightsail) deployment.
DEBUG = os.getenv("MCP_SERVER_DEBUG", "false").lower() in ("1", "true", "yes")
# Comma-separated list of allowed CORS origins, or "*" for any.
CORS_ALLOW_ORIGINS = [
    o.strip() for o in os.getenv("MCP_SERVER_CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()
]
# Per-client requests/minute cap. Set to 0 to disable rate limiting.
RATE_LIMIT_PER_MINUTE = int(os.getenv("MCP_SERVER_RATE_LIMIT_PER_MINUTE", "120"))


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Server("usa-spending-mcp-server")

# Derive the name -> handler dispatch map from the single TOOLS registry.
_HANDLERS = {tool.name: handler for tool, handler in TOOLS}


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    handler = _HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [tool for tool, _ in TOOLS]


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [prompt_award_type_codes_guide, prompt_general_guidance]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    valid_prompt_names = ["award_type_codes_guide", "general_guidance"]
    if name not in valid_prompt_names:
        raise ValueError(f"Unknown prompt: {name}. Valid prompt names are {valid_prompt_names}.")

    if name == "award_type_codes_guide":
        return types.GetPromptResult(
            messages=prompt_message_award_type_codes_guide(),
            description="A Guide to using award_type_codes.",
        )

    if name == "general_guidance":
        return types.GetPromptResult(
            messages=prompt_message_general_guidance(),
            description="A general guide to using the USA spending MCP server.",
        )


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        resource_award_type_codes,
        resource_toptier_agencies,
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl):
    if uri.path is None:
        raise ValueError(f"Invalid resource path: {uri}")
    name = uri.path.replace(".json", "").lstrip("/")

    valid_resource_names = [resource_name_award_type_codes, resource_name_toptier_agencies]

    if name not in valid_resource_names:
        raise ValueError(
            f"Unknown resource: {uri}.Valid resource names are {','.join(valid_resource_names)}"
        )

    if name == resource_name_award_type_codes:
        return [ReadResourceContents(content=f"{award_type_groups}", mime_type="application/json")]

    if name == resource_name_toptier_agencies:
        return [
            ReadResourceContents(content=f"{get_toptier_agencies()}", mime_type="application/json")
        ]


# Create the session manager with true stateless mode
session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    stateless=True,
)


async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    await session_manager.handle_request(scope, receive, send)


async def health(request):
    """Liveness/readiness probe for load balancers (e.g. Lightsail health check)."""
    return JSONResponse({"status": "ok"})


class RateLimitMiddleware:
    """Dependency-free per-client fixed-window rate limiter.

    Sized for a single-container deployment (in-memory counters). Keys on the
    first hop of X-Forwarded-For (set by the Lightsail/ALB proxy), falling back
    to the socket peer. Disabled when limit <= 0. The /healthz probe is exempt.
    """

    def __init__(self, app, limit_per_minute: int):
        self.app = app
        self.limit = limit_per_minute
        self._hits: dict[str, tuple[int, int]] = {}

    def _client(self, scope) -> str:
        # The container only receives traffic through the Lightsail-managed load
        # balancer, which appends the real client IP as the LAST X-Forwarded-For
        # hop. Take the right-most entry: a remote client can prepend/spoof earlier
        # hops but cannot forge the value the trusted proxy appends, so this can't
        # be gamed to mint unlimited rate-limit buckets. Fall back to the socket peer.
        for name, value in scope.get("headers") or []:
            if name == b"x-forwarded-for" and value:
                return value.decode().split(",")[-1].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    async def __call__(self, scope, receive, send):
        if self.limit <= 0 or scope.get("type") != "http" or scope.get("path") == "/healthz":
            await self.app(scope, receive, send)
            return

        window = int(time.time() // 60)
        # Bound memory growth from unique clients over time.
        if len(self._hits) > 10000:
            self._hits = {k: v for k, v in self._hits.items() if v[1] == window}

        key = self._client(scope)
        count, w = self._hits.get(key, (0, window))
        if w != window:
            count, w = 0, window
        count += 1
        self._hits[key] = (count, w)

        if count > self.limit:
            body = b'{"error":"rate limit exceeded"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"retry-after", b"60"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Context manager for session manager."""
    async with session_manager.run():
        logger.info("Application started with StreamableHTTP session manager!")
        try:
            yield
        finally:
            logger.info("Application shutting down...")


# Create an ASGI application using the transport
starlette_app = Starlette(
    debug=DEBUG,
    routes=[
        Route("/healthz", health, methods=["GET"]),
        Mount("/mcp", app=handle_streamable_http),
    ],
    lifespan=lifespan,
)

# Wrap ASGI application with CORS middleware to expose Mcp-Session-Id header
# for browser-based clients (ensures 500 errors get proper CORS headers)
starlette_app = CORSMiddleware(
    starlette_app,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],  # MCP streamable HTTP methods
    expose_headers=["Mcp-Session-Id"],
)

# Outermost layer: lightweight per-client rate limiting (disabled when <= 0).
starlette_app = RateLimitMiddleware(starlette_app, RATE_LIMIT_PER_MINUTE)


def main():
    # Trust X-Forwarded-Proto/For from any upstream proxy. Behind Lightsail's
    # load balancer the container only ever sees the LB, so this is safe, and
    # without it Starlette's "/mcp" -> "/mcp/" redirect is emitted with an
    # http:// Location, which strict MCP clients (e.g. ChatGPT) refuse to
    # follow from an https:// origin.
    uvicorn.run(
        starlette_app,
        host=HOST,
        port=PORT,
        proxy_headers=True,
        forwarded_allow_ips=os.getenv("MCP_SERVER_FORWARDED_ALLOW_IPS", "*"),
    )
    return 0


if __name__ == "__main__":
    main()
