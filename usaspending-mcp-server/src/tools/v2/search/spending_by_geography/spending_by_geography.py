from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import advanced_filter_object
from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["scope", "geo_layer", "filters"],
    "additionalProperties": False,
    "properties": {
        "scope": {
            "type": "string",
            "enum": ["place_of_performance", "recipient_location"],
            "description": "Whether to map by where work is performed or where recipients are.",
        },
        "geo_layer": {
            "type": "string",
            "enum": ["state", "county", "district", "country"],
            "description": "Geographic granularity of the aggregation.",
        },
        "filters": advanced_filter_object,
        "geo_layer_filters": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional list of geo codes to restrict results to.",
        },
        "spending_level": {
            "type": "string",
            "enum": ["transactions", "awards", "subawards"],
            "default": "transactions",
        },
    },
}

tool_spending_by_geography = Tool(
    name="spending_by_geography",
    description=(
        "Aggregates filtered spending by geography (state, county, congressional "
        "district, or country), by place of performance or recipient location. Use "
        "for regional targeting and footprint analysis."
    ),
    inputSchema=input_schema,
    title="Spending by Geography",
)

endpoint = "/api/v2/search/spending_by_geography/"


async def call_tool_spending_by_geography(arguments: dict[str, Any]):
    scope = arguments.get("scope")
    geo_layer = arguments.get("geo_layer")
    filters = arguments.get("filters")

    if not scope:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="scope must be provided."))
    if not geo_layer:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="geo_layer must be provided.")
        )
    if not bool(filters):
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="filters must be provided.")
        )

    payload = {"scope": scope, "geo_layer": geo_layer, "filters": filters}
    for key in ("geo_layer_filters", "spending_level"):
        if arguments.get(key) is not None:
            payload[key] = arguments[key]

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
