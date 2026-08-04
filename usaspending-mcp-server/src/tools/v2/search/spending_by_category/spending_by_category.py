from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import advanced_filter_object
from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["category", "filters"],
    "additionalProperties": False,
    "properties": {
        "category": {
            "type": "string",
            "enum": [
                "awarding_agency",
                "awarding_subagency",
                "funding_agency",
                "funding_subagency",
                "recipient",
                "recipient_duns",
                "cfda",
                "psc",
                "naics",
                "county",
                "district",
                "state_territory",
                "country",
                "federal_account",
                "defc",
            ],
            "description": "The dimension to rank/group the filtered spending by.",
        },
        "filters": advanced_filter_object,
        "limit": {
            "type": "integer",
            "default": 10,
            "description": "Number of ranked results to return per page.",
        },
        "page": {"type": "integer", "default": 1},
        "subawards": {
            "type": "boolean",
            "default": False,
            "description": "True to aggregate subawards instead of prime awards.",
        },
    },
}

tool_spending_by_category = Tool(
    name="spending_by_category",
    description=(
        "Ranks filtered spending grouped by a chosen dimension - e.g. top recipients "
        "(competitors) in a market, or spending broken out by NAICS/PSC, awarding "
        "agency, or geography. Ideal for market sizing and competitor analysis."
    ),
    inputSchema=input_schema,
    title="Spending by Category",
)

async def call_tool_spending_by_category(arguments: dict[str, Any]):
    category = arguments.get("category")
    filters = arguments.get("filters")

    if not category:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="category must be provided.")
        )
    if not bool(filters):
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="filters must be provided.")
        )

    # The category is a path segment, not a body field.
    endpoint = f"/api/v2/search/spending_by_category/{category}/"
    payload = {"filters": filters}
    for key in ("limit", "page", "subawards"):
        if arguments.get(key) is not None:
            payload[key] = arguments[key]

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
