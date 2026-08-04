"""Tests for the BD-expansion tools (Tiers 1-3)."""

from unittest.mock import patch

import pytest
from httpx import Response
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, Tool
from validation import Validation

from tools.config import (
    TOOLS,
    call_tool_agency_awards,
    call_tool_agency_obligations_by_award_category,
    call_tool_agency_sub_agency,
    call_tool_autocomplete,
    call_tool_award,
    call_tool_idv_activity,
    call_tool_idv_awards,
    call_tool_idv_funding_rollup,
    call_tool_new_awards_over_time,
    call_tool_references_naics,
    call_tool_references_psc,
    call_tool_spending_by_category,
    call_tool_spending_by_geography,
    call_tool_spending_by_subaward_grouped,
    tool_agency_awards,
    tool_agency_obligations_by_award_category,
    tool_agency_sub_agency,
    tool_autocomplete,
    tool_award,
    tool_idv_activity,
    tool_idv_awards,
    tool_idv_funding_rollup,
    tool_new_awards_over_time,
    tool_references_naics,
    tool_references_psc,
    tool_spending_by_category,
    tool_spending_by_geography,
    tool_spending_by_subaward_grouped,
)

BD_TOOLS = [
    tool_award,
    tool_spending_by_category,
    tool_idv_awards,
    tool_idv_activity,
    tool_idv_funding_rollup,
    tool_autocomplete,
    tool_spending_by_subaward_grouped,
    tool_new_awards_over_time,
    tool_spending_by_geography,
    tool_agency_awards,
    tool_agency_obligations_by_award_category,
    tool_agency_sub_agency,
    tool_references_naics,
    tool_references_psc,
]


class TestBdToolDefinitions:
    def test_all_tools_well_formed(self):
        names = set()
        for tool in BD_TOOLS:
            assert isinstance(tool, Tool)
            assert tool.name and tool.name not in names, f"duplicate/blank name: {tool.name}"
            names.add(tool.name)
            assert tool.description
            assert tool.inputSchema["type"] == "object"


class TestRegistry:
    def test_registry_names_unique_and_handlers_callable(self):
        names = [tool.name for tool, _ in TOOLS]
        assert len(names) == len(set(names)), "duplicate tool name in TOOLS registry"
        for _, handler in TOOLS:
            assert callable(handler)

    def test_every_bd_tool_is_registered(self):
        registered = {tool.name for tool, _ in TOOLS}
        for tool in BD_TOOLS:
            assert tool.name in registered, f"{tool.name} missing from TOOLS registry"


class TestRequiredArgs(Validation):
    @pytest.mark.asyncio
    async def test_award_requires_award_id(self):
        with pytest.raises(McpError) as err:
            await call_tool_award({})
        assert err.value.error.code == INVALID_PARAMS
        assert "award_id must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_spending_by_category_requires_category(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_by_category({"filters": {"a": 1}})
        assert "category must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_spending_by_category_requires_filters(self):
        with pytest.raises(McpError) as err:
            await call_tool_spending_by_category({"category": "recipient"})
        assert "filters must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_idv_tools_require_award_id(self):
        for handler in (
            call_tool_idv_awards,
            call_tool_idv_activity,
            call_tool_idv_funding_rollup,
        ):
            with pytest.raises(McpError) as err:
                await handler({})
            assert "award_id must be provided" in err.value.error.message

    @pytest.mark.asyncio
    async def test_autocomplete_requires_valid_type(self):
        with pytest.raises(McpError) as err:
            await call_tool_autocomplete({"type": "bogus", "search_text": "x"})
        assert err.value.error.code == INVALID_PARAMS

    @pytest.mark.asyncio
    async def test_new_awards_over_time_requires_recipient_id(self):
        with pytest.raises(McpError) as err:
            await call_tool_new_awards_over_time(
                {"group": "fiscal_year", "filters": {"time_period": []}}
            )
        assert "recipient_id" in err.value.error.message

    @pytest.mark.asyncio
    async def test_agency_tools_require_toptier_code(self):
        for handler in (
            call_tool_agency_awards,
            call_tool_agency_obligations_by_award_category,
            call_tool_agency_sub_agency,
        ):
            with pytest.raises(McpError) as err:
                await handler({})
            assert "toptier_code must be provided" in err.value.error.message


class TestHappyPaths(Validation):
    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_award_get(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_award({"award_id": "CONT_AWD_X"})
        mock_send.assert_called_once()
        # Path param is interpolated into the URL, no query string.
        assert "/api/v2/awards/CONT_AWD_X/" in str(mock_send.call_args)
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_spending_by_category_post(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending_by_category(
            {"category": "recipient", "filters": {"time_period": []}}
        )
        mock_send.assert_called_once()
        # Category must be a path segment.
        assert "/api/v2/search/spending_by_category/recipient/" in str(mock_send.call_args)
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_references_naics_with_and_without_code(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        await call_tool_references_naics({})
        await call_tool_references_naics({"naics_code": "54"})
        assert mock_send.call_count == 2

    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_references_psc(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_references_psc({"depth": 1})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_geography_post(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending_by_geography(
            {
                "scope": "place_of_performance",
                "geo_layer": "state",
                "filters": {"time_period": []},
            }
        )
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")

    @pytest.mark.asyncio
    @patch("utils.http.client.send")
    async def test_subaward_grouped_post(self, mock_send):
        mock_send.return_value = Response(status_code=200, json={})
        res = await call_tool_spending_by_subaward_grouped({"filters": {"time_period": []}})
        mock_send.assert_called_once()
        self.validate_text_content(res, text="{}")
