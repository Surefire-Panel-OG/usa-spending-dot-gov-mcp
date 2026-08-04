from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["award_id"],
    "additionalProperties": False,
    "properties": {
        "award_id": {
            "type": "string",
            "description": "Generated or surrogate award id of the IDV.",
        },
        "limit": {"type": "integer", "default": 10},
        "page": {"type": "integer", "default": 1},
    },
}

tool_idv_activity = Tool(
    name="idv_activity",
    description=(
        "Returns the funding/obligation activity of the child and grandchild awards "
        "under an IDV over time - a signal of how actively a contract vehicle is "
        "being used."
    ),
    inputSchema=input_schema,
    title="IDV Activity",
)

endpoint = "/api/v2/idvs/activity/"


async def call_tool_idv_activity(arguments: dict[str, Any]):
    award_id = arguments.get("award_id")
    if not award_id:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="award_id must be provided.")
        )

    payload = {"award_id": award_id}
    for key in ("limit", "page"):
        if arguments.get(key) is not None:
            payload[key] = arguments[key]

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
