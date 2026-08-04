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
    },
}

tool_agency_obligations_by_award_category = Tool(
    name="agency_obligations_by_award_category",
    description=(
        "Breaks down an agency's obligations by award category (contracts, grants, "
        "loans, direct payments, etc.) for a fiscal year - shows how a target agency "
        "spends its money."
    ),
    inputSchema=input_schema,
    title="Agency Obligations by Award Category",
)


async def call_tool_agency_obligations_by_award_category(arguments: dict[str, Any]):
    toptier_code = arguments.get("toptier_code")
    if not toptier_code:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="toptier_code must be provided.")
        )

    params: dict[str, Any] = {}
    if arguments.get("fiscal_year") is not None:
        params["fiscal_year"] = arguments["fiscal_year"]

    endpoint = f"/api/v2/agency/{toptier_code}/obligations_by_award_category/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=None
    )
    return await get_client.send()
