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
    },
}

tool_idv_funding_rollup = Tool(
    name="idv_funding_rollup",
    description=(
        "Returns aggregated funding metrics for an IDV: total transaction obligated "
        "amount and the count of awarding agencies, funding agencies, and federal "
        "accounts funding work under the vehicle."
    ),
    inputSchema=input_schema,
    title="IDV Funding Rollup",
)

endpoint = "/api/v2/idvs/funding_rollup/"


async def call_tool_idv_funding_rollup(arguments: dict[str, Any]):
    award_id = arguments.get("award_id")
    if not award_id:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="award_id must be provided.")
        )

    payload = {"award_id": award_id}
    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
