from typing import Any

from mcp.types import Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "naics_code": {
            "type": "string",
            "description": (
                "A NAICS code to expand. If given, returns that code and its children. "
                "If omitted, returns all tier-1 (2-digit) NAICS sectors."
            ),
        },
        "filter": {
            "type": "string",
            "description": (
                "Optional text to filter NAICS results by "
                "(ignored when naics_code is set)."
            ),
        },
    },
}

tool_references_naics = Tool(
    name="references_naics",
    description=(
        "Browses the NAICS industry-code hierarchy. Call without arguments for the "
        "top-level sectors, with a naics_code to drill into its children, or with a "
        "filter to search - helps pick the right code for spending filters."
    ),
    inputSchema=input_schema,
    title="NAICS Reference",
)


async def call_tool_references_naics(arguments: dict[str, Any]):
    naics_code = arguments.get("naics_code")

    if naics_code:
        endpoint = f"/api/v2/references/naics/{naics_code}/"
        get_client = HttpClient(endpoint=endpoint, method="GET", output_schema=None)
        return await get_client.send()

    params: dict[str, Any] = {}
    if arguments.get("filter"):
        params["filter"] = arguments["filter"]

    endpoint = "/api/v2/references/naics/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=None
    )
    return await get_client.send()
