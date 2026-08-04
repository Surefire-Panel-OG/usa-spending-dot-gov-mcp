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
            "description": "Generated or surrogate award id of the IDV (contract vehicle).",
        },
        "idv": {
            "type": "boolean",
            "default": True,
            "description": "True if award_id refers to an IDV rather than a single award.",
        },
        "type": {
            "type": "string",
            "enum": ["child_idvs", "child_awards", "grandchild_awards"],
            "default": "child_awards",
            "description": "Which related awards under the vehicle to return.",
        },
        "limit": {"type": "integer", "default": 10},
        "page": {"type": "integer", "default": 1},
        "sort": {"type": "string", "description": "Field to sort by, e.g. obligated_amount."},
        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
    },
}

tool_idv_awards = Tool(
    name="idv_awards",
    description=(
        "Lists the task/delivery orders and child IDVs issued under an Indefinite "
        "Delivery Vehicle (IDIQ, GWAC, BPA). Use to see who is winning work on a "
        "specific contract vehicle."
    ),
    inputSchema=input_schema,
    title="IDV Awards",
)

endpoint = "/api/v2/idvs/awards/"


async def call_tool_idv_awards(arguments: dict[str, Any]):
    award_id = arguments.get("award_id")
    if not award_id:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="award_id must be provided.")
        )

    payload = {"award_id": award_id}
    for key in ("idv", "type", "limit", "page", "sort", "order"):
        if arguments.get(key) is not None:
            payload[key] = arguments[key]

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
