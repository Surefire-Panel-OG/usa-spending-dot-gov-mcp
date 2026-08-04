# usaspendingmcp

An MCP server for [USAspending.gov](https://www.usaspending.gov/) federal
spending data, packaged for use by a government-contracting business-development
team. It vendors and extends
[thsmale/usaspending-mcp-server](https://github.com/thsmale/usaspending-mcp-server)
(MIT).

The underlying USAspending API is fully public — **no API key or credentials**.

## Layout

- [`usaspending-mcp-server/`](usaspending-mcp-server/) — the MCP server (vendored + extended).
- [`deploy/`](deploy/) — AWS Lightsail deployment kit and the team connect guide.

## Tools (24)

**Core spending analysis (original):**
`toptier_agencies`, `list_budget_functions`, `major_object_class`,
`federal_accounts`, `recipient`, `spending`, `spending_by_award`,
`spending_over_time`, `subawards`, `total_budgetary_resources`.

**BD expansion — Tier 1 (opportunity & competitor intel):**
- `award` — full detail on one award incl. period-of-performance end date (recompete timing)
- `spending_by_category` — rank filtered spending by recipient / NAICS / PSC / agency / geography
- `idv_awards`, `idv_activity`, `idv_funding_rollup` — task-order and funding intel for contract vehicles (IDIQ/GWAC/BPA)
- `autocomplete` — resolve plain-language names into NAICS/PSC/CFDA/agency/recipient codes

**BD expansion — Tier 2 (teaming, momentum, targeting):**
- `spending_by_subaward_grouped` — teaming map (subs grouped by prime)
- `new_awards_over_time` — a recipient's new-award momentum
- `spending_by_geography` — spending by state/county/district/country
- `agency_awards`, `agency_obligations_by_award_category`, `agency_sub_agency` — agency profiles

**BD expansion — Tier 3 (reference):**
- `references_naics`, `references_psc` — browse the NAICS / PSC hierarchies

## Run locally

```bash
cd usaspending-mcp-server
uv run src/server.py        # serves http://127.0.0.1:8000/mcp
uv run pytest               # 129 tests
```

## Deploy for a team

See [`deploy/README.md`](deploy/README.md) (AWS Lightsail, ~$7/mo flat) and give
teammates [`deploy/CONNECT.md`](deploy/CONNECT.md) to add it in Claude Desktop.
