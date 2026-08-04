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
                "The toptier agency code (from the toptier_agencies tool), e.g. '097'."
            ),
        },
        "fiscal_year": {
            "type": "integer",
            "description": "Fiscal year. Defaults to the latest available.",
        },
        "limit": {"type": "integer", "default": 10},
        "page": {"type": "integer", "default": 1},
    },
}

tool_agency_sub_agency = Tool(
    name="agency_sub_agency",
    description=(
        "Lists an agency's sub-agencies with their obligated amounts and award/"
        "transaction counts for a fiscal year - identifies which offices within a "
        "department hold the buying power."
    ),
    inputSchema=input_schema,
    title="Agency Sub-Agencies",
)


async def call_tool_agency_sub_agency(arguments: dict[str, Any]):
    toptier_code = arguments.get("toptier_code")
    if not toptier_code:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="toptier_code must be provided.")
        )

    params: dict[str, Any] = {}
    for key in ("fiscal_year", "limit", "page"):
        if arguments.get(key) is not None:
            params[key] = arguments[key]

    endpoint = f"/api/v2/agency/{toptier_code}/sub_agency/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=None
    )
    return await get_client.send()
