from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["toptier_code"],
    "additionalProperties": False,
    "properties": {
        "toptier_code": {
            "type": "string",
            "description": (
                "The 3-4 digit CGAC/FREC toptier agency code (the 'toptier_code' "
                "returned by the toptier_agencies tool), e.g. '097' for DoD."
            ),
        },
        "fiscal_year": {
            "type": "integer",
            "description": "Fiscal year to summarize. Defaults to the latest available.",
        },
        "agency_type": {
            "type": "string",
            "enum": ["awarding", "funding"],
            "default": "awarding",
            "description": "Summarize awards where the agency is the awarder or the funder.",
        },
    },
}

tool_agency_awards = Tool(
    name="agency_awards",
    description=(
        "Returns a summary of an agency's award activity for a fiscal year - "
        "transaction count and total obligations. Use for agency targeting."
    ),
    inputSchema=input_schema,
    title="Agency Awards Summary",
)


async def call_tool_agency_awards(arguments: dict[str, Any]):
    toptier_code = arguments.get("toptier_code")
    if not toptier_code:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="toptier_code must be provided.")
        )

    params: dict[str, Any] = {}
    for key in ("fiscal_year", "agency_type"):
        if arguments.get(key) is not None:
            params[key] = arguments[key]

    endpoint = f"/api/v2/agency/{toptier_code}/awards/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=None
    )
    return await get_client.send()
