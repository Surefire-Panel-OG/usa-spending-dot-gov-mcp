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
            "description": (
                "The unique award identifier. Prefer the generated natural award id "
                "(the 'generated_internal_id' / 'Award ID' returned by spending_by_award), "
                "e.g. CONT_AWD_...; a numeric surrogate id is also accepted."
            ),
        },
    },
}

tool_award = Tool(
    name="award",
    description=(
        "Returns detailed information about a single prime award (contract, grant, "
        "loan, IDV, etc.): recipient, awarding/funding agencies, NAICS/PSC, dollar "
        "amounts, and the period of performance including the potential end date - "
        "useful for recompete timing."
    ),
    inputSchema=input_schema,
    title="Award Detail",
)


async def call_tool_award(arguments: dict[str, Any]):
    award_id = arguments.get("award_id")
    if not award_id:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="award_id must be provided.",
                data="Use the generated award id returned by spending_by_award.",
            )
        )

    endpoint = f"/api/v2/awards/{award_id}/"
    get_client = HttpClient(endpoint=endpoint, method="GET", output_schema=None)
    return await get_client.send()
