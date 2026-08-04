from typing import Any

from mcp.types import Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "depth": {
            "type": "integer",
            "default": 2,
            "description": "How many levels of the PSC tree to return.",
        },
        "filter": {
            "type": "string",
            "description": "Optional text to filter PSC nodes by.",
        },
    },
}

tool_references_psc = Tool(
    name="references_psc",
    description=(
        "Browses the Product & Service Code (PSC) hierarchy used to classify what the "
        "government buys. Use to find the right PSC(s) for spending filters."
    ),
    inputSchema=input_schema,
    title="PSC Reference Tree",
)

endpoint = "/api/v2/references/filter_tree/psc/?"


async def call_tool_references_psc(arguments: dict[str, Any]):
    params: dict[str, Any] = {}
    for key in ("depth", "filter"):
        if arguments.get(key) is not None:
            params[key] = arguments[key]

    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=None
    )
    return await get_client.send()
