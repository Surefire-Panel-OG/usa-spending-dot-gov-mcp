# Tools
from tools.v2.agency.agency_awards import (
    call_tool_agency_awards,
    tool_agency_awards,
)
from tools.v2.agency.agency_obligations_by_award_category import (
    call_tool_agency_obligations_by_award_category,
    tool_agency_obligations_by_award_category,
)
from tools.v2.agency.agency_sub_agency import (
    call_tool_agency_sub_agency,
    tool_agency_sub_agency,
)
from tools.v2.autocomplete.autocomplete import (
    call_tool_autocomplete,
    tool_autocomplete,
)
from tools.v2.awards.award import (
    call_tool_award,
    tool_award,
)
from tools.v2.budget_functions.list_budget_functions import (
    call_tool_list_budget_functions,
    tool_list_budget_functions,
)
from tools.v2.federal_accounts.federal_accounts import (
    call_tool_federal_accounts,
    tool_federal_accounts,
)
from tools.v2.financial_spending.major_object_class import (
    call_tool_major_object_class,
    tool_major_object_class,
)
from tools.v2.idvs.idv_activity import (
    call_tool_idv_activity,
    tool_idv_activity,
)
from tools.v2.idvs.idv_awards import (
    call_tool_idv_awards,
    tool_idv_awards,
)
from tools.v2.idvs.idv_funding_rollup import (
    call_tool_idv_funding_rollup,
    tool_idv_funding_rollup,
)
from tools.v2.recipient.recipient import (
    call_tool_recipient,
    tool_recipient,
)
from tools.v2.references.naics.references_naics import (
    call_tool_references_naics,
    tool_references_naics,
)
from tools.v2.references.psc.references_psc import (
    call_tool_references_psc,
    tool_references_psc,
)
from tools.v2.references.toptier_agencies.toptier_agencies import (
    call_tool_toptier_agencies,
    tool_toptier_agencies,
)
from tools.v2.references.total_budgetary_resources.total_budgetary_resources import (
    call_tool_total_budgetary_resources,
    tool_total_budgetary_resources,
)
from tools.v2.search.new_awards_over_time.new_awards_over_time import (
    call_tool_new_awards_over_time,
    tool_new_awards_over_time,
)
from tools.v2.search.spending_by_award.spending_by_award import (
    call_tool_spending_by_award,
    tool_spending_by_award,
)
from tools.v2.search.spending_by_category.spending_by_category import (
    call_tool_spending_by_category,
    tool_spending_by_category,
)
from tools.v2.search.spending_by_geography.spending_by_geography import (
    call_tool_spending_by_geography,
    tool_spending_by_geography,
)
from tools.v2.search.spending_by_subaward_grouped.spending_by_subaward_grouped import (
    call_tool_spending_by_subaward_grouped,
    tool_spending_by_subaward_grouped,
)
from tools.v2.search.spending_over_time.spending_over_time import (
    call_tool_spending_over_time,
    tool_spending_over_time,
)
from tools.v2.spending.spending import (
    call_tool_spending,
    tool_spending,
)
from tools.v2.subawards.subawards import (
    call_tool_subawards,
    tool_subawards,
)

__all__ = [
    "call_tool_award",
    "tool_award",
    "call_tool_spending_by_category",
    "tool_spending_by_category",
    "call_tool_idv_awards",
    "tool_idv_awards",
    "call_tool_idv_activity",
    "tool_idv_activity",
    "call_tool_idv_funding_rollup",
    "tool_idv_funding_rollup",
    "call_tool_autocomplete",
    "tool_autocomplete",
    "call_tool_spending_by_subaward_grouped",
    "tool_spending_by_subaward_grouped",
    "call_tool_new_awards_over_time",
    "tool_new_awards_over_time",
    "call_tool_spending_by_geography",
    "tool_spending_by_geography",
    "call_tool_agency_awards",
    "tool_agency_awards",
    "call_tool_agency_obligations_by_award_category",
    "tool_agency_obligations_by_award_category",
    "call_tool_agency_sub_agency",
    "tool_agency_sub_agency",
    "call_tool_references_naics",
    "tool_references_naics",
    "call_tool_references_psc",
    "tool_references_psc",
    "call_tool_list_budget_functions",
    "tool_list_budget_functions",
    "call_tool_federal_accounts",
    "tool_federal_accounts",
    "call_tool_major_object_class",
    "tool_major_object_class",
    "call_tool_recipient",
    "tool_recipient",
    "call_tool_toptier_agencies",
    "tool_toptier_agencies",
    "call_tool_total_budgetary_resources",
    "tool_total_budgetary_resources",
    "call_tool_spending_by_award",
    "tool_spending_by_award",
    "call_tool_spending_over_time",
    "tool_spending_over_time",
    "call_tool_spending",
    "tool_spending",
    "call_tool_subawards",
    "tool_subawards",
    "TOOLS",
]

# Single source of truth for tool registration: (Tool definition, handler).
# server.py derives BOTH list_tools() and the call dispatch from this list, so
# the advertised set and the dispatchable set can never drift out of sync.
TOOLS = [
    (tool_federal_accounts, call_tool_federal_accounts),
    (tool_list_budget_functions, lambda arguments: call_tool_list_budget_functions()),
    (tool_major_object_class, call_tool_major_object_class),
    (tool_recipient, call_tool_recipient),
    (tool_spending, call_tool_spending),
    (tool_spending_by_award, call_tool_spending_by_award),
    (tool_spending_over_time, call_tool_spending_over_time),
    (tool_subawards, call_tool_subawards),
    (tool_total_budgetary_resources, call_tool_total_budgetary_resources),
    (tool_toptier_agencies, call_tool_toptier_agencies),
    # BD expansion: Tier 1
    (tool_award, call_tool_award),
    (tool_spending_by_category, call_tool_spending_by_category),
    (tool_idv_awards, call_tool_idv_awards),
    (tool_idv_activity, call_tool_idv_activity),
    (tool_idv_funding_rollup, call_tool_idv_funding_rollup),
    (tool_autocomplete, call_tool_autocomplete),
    # BD expansion: Tier 2
    (tool_spending_by_subaward_grouped, call_tool_spending_by_subaward_grouped),
    (tool_new_awards_over_time, call_tool_new_awards_over_time),
    (tool_spending_by_geography, call_tool_spending_by_geography),
    (tool_agency_awards, call_tool_agency_awards),
    (tool_agency_obligations_by_award_category, call_tool_agency_obligations_by_award_category),
    (tool_agency_sub_agency, call_tool_agency_sub_agency),
    # BD expansion: Tier 3
    (tool_references_naics, call_tool_references_naics),
    (tool_references_psc, call_tool_references_psc),
]
