from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import advanced_filter_object
from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["filters"],
    "additionalProperties": False,
    "properties": {
        "filters": advanced_filter_object,
        "limit": {"type": "integer", "default": 10},
        "page": {"type": "integer", "default": 1},
        "sort": {"type": "string"},
        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
    },
}

tool_spending_by_subaward_grouped = Tool(
    name="spending_by_subaward_grouped",
    description=(
        "Returns subaward counts and amounts grouped by their prime award. Use to map "
        "teaming relationships - which primes subcontract work and where your firm "
        "could position as a sub."
    ),
    inputSchema=input_schema,
    title="Spending by Subaward (Grouped)",
)

endpoint = "/api/v2/search/spending_by_subaward_grouped/"


async def call_tool_spending_by_subaward_grouped(arguments: dict[str, Any]):
    filters = arguments.get("filters")
    if not bool(filters):
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="filters must be provided.")
        )

    payload = {"filters": filters}
    for key in ("limit", "page", "sort", "order"):
        if arguments.get(key) is not None:
            payload[key] = arguments[key]

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
