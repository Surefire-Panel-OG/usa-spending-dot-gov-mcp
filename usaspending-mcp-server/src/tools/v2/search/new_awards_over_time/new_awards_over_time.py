from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from tools.v2.search.config import filter_object_award_types, time_period_object
from utils.http import HttpClient

# This endpoint is recipient-scoped: the USAspending API requires
# filters.recipient_id, which the shared advanced_filter_object does not define,
# so this tool uses a purpose-built filter schema. The time_period and
# award_type_codes fragments are reused from search/config.py.
filters_schema = {
    "type": "object",
    "required": ["recipient_id", "time_period"],
    "additionalProperties": False,
    "properties": {
        "recipient_id": {
            "type": "string",
            "description": (
                "The recipient hash id (the 'recipient_id' returned by the recipient "
                "tool or by spending_by_award), e.g. '...-C' / '...-R'."
            ),
        },
        "time_period": time_period_object,
        "award_type_codes": filter_object_award_types,
    },
}

input_schema = {
    "type": "object",
    "required": ["group", "filters"],
    "additionalProperties": False,
    "properties": {
        "group": {
            "type": "string",
            "enum": ["fiscal_year", "quarter", "month"],
            "default": "fiscal_year",
            "description": "Time period to group new-award counts by.",
        },
        "filters": filters_schema,
    },
}

tool_new_awards_over_time = Tool(
    name="new_awards_over_time",
    description=(
        "Returns the count of NEW awards a specific recipient won per time period. "
        "Use for competitor momentum - is a given firm winning more work lately? "
        "Requires a recipient_id (get one from the recipient or spending_by_award tools)."
    ),
    inputSchema=input_schema,
    title="New Awards Over Time (by Recipient)",
)

endpoint = "/api/v2/search/new_awards_over_time/"


async def call_tool_new_awards_over_time(arguments: dict[str, Any]):
    group = arguments.get("group")
    filters = arguments.get("filters")

    if not group:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="group must be provided.")
        )
    if not bool(filters) or not filters.get("recipient_id"):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters with a recipient_id must be provided.",
            )
        )

    payload = {"group": group, "filters": filters}
    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=None
    )
    return await post_client.send()
