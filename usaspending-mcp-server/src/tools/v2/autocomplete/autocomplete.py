from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

# Maps the tool's "type" argument to the USAspending autocomplete endpoint.
# All of these accept a simple {"search_text": ...} (plus optional limit) payload.
TYPE_TO_ENDPOINT = {
    "naics": "/api/v2/autocomplete/naics/",
    "psc": "/api/v2/autocomplete/psc/",
    "cfda": "/api/v2/autocomplete/cfda/",
    "awarding_agency": "/api/v2/autocomplete/awarding_agency/",
    "funding_agency": "/api/v2/autocomplete/funding_agency/",
    "recipient": "/api/v2/autocomplete/recipient/",
    "glossary": "/api/v2/autocomplete/glossary/",
}

input_schema = {
    "type": "object",
    "required": ["type", "search_text"],
    "additionalProperties": False,
    "properties": {
        "type": {
            "type": "string",
            "enum": sorted(TYPE_TO_ENDPOINT.keys()),
            "description": "Which reference set to search.",
        },
        "search_text": {
            "type": "string",
            "description": "Plain-language text to match, e.g. 'cybersecurity', 'Navy'.",
        },
        "limit": {"type": "integer", "default": 10},
    },
}

tool_autocomplete = Tool(
    name="autocomplete",
    description=(
        "Resolves plain-language text into the codes/identifiers the spending filters "
        "require - NAICS, PSC, CFDA, awarding/funding agency, or recipient (and "
        "glossary terms). Call this first when you only know a name, not a code."
    ),
    inputSchema=input_schema,
    title="Autocomplete / Code Lookup",
)


async def call_tool_autocomplete(arguments: dict[str, Any]):
    type_ = arguments.get("type")
    search_text = arguments.get("search_text")

    if type_ not in TYPE_TO_ENDPOINT:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"type must be one of {sorted(TYPE_TO_ENDPOINT.keys())}.",
            )
        )
    if not search_text:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="search_text must be provided.")
        )

    payload: dict[str, Any] = {"search_text": search_text}
    if arguments.get("limit") is not None:
        payload["limit"] = arguments["limit"]

    post_client = HttpClient(
        endpoint=TYPE_TO_ENDPOINT[type_],
        method="POST",
        payload=payload,
        output_schema=None,
    )
    return await post_client.send()
