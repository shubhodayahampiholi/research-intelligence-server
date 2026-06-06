"""Tests for tool handlers."""

import json
import pytest
from research_server.primitives.tools import TOOL_DEFINITIONS, handle_tool_call
from research_server.observability.logging import configure_logging

configure_logging(level="WARNING")


class TestToolDefinitions:
    def test_tool_count(self):
        assert len(TOOL_DEFINITIONS) == 4

    def test_all_tools_have_descriptions(self):
        for tool in TOOL_DEFINITIONS:
            assert tool.description

    def test_all_tools_have_input_schema(self):
        for tool in TOOL_DEFINITIONS:
            assert tool.inputSchema

    def test_all_tools_have_output_schema(self):
        for tool in TOOL_DEFINITIONS:
            assert tool.outputSchema

    def test_compare_papers_schema_constraints(self):
        """minItems/maxItems must be in schema so model learns them at discovery time."""
        tool = next(t for t in TOOL_DEFINITIONS if t.name == "compare_papers")
        schema = tool.inputSchema["properties"]["paper_ids"]
        assert schema["minItems"] == 2
        assert schema["maxItems"] == 4

    def test_citation_network_depth_bounds(self):
        tool = next(t for t in TOOL_DEFINITIONS if t.name == "get_citation_network")
        schema = tool.inputSchema["properties"]["depth"]
        assert schema["minimum"] == 1
        assert schema["maximum"] == 3

    def test_direction_is_enum_not_boolean(self):
        """Semantic values must use enums, not booleans."""
        tool = next(t for t in TOOL_DEFINITIONS if t.name == "get_citation_network")
        schema = tool.inputSchema["properties"]["direction"]
        assert "enum" in schema
        assert set(schema["enum"]) == {"references", "cited_by", "both"}


class TestSearchPapers:
    def test_basic_search(self):
        content, is_error = handle_tool_call("search_papers", {"query": "transformer"})
        assert not is_error
        result = json.loads(content[0].text)
        assert result["total_count"] > 0

    def test_domain_filter(self):
        content, is_error = handle_tool_call(
            "search_papers", {"query": "attention", "domain": "machine-learning"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        for paper in result["papers"]:
            assert paper["domain"] == "machine-learning"

    def test_year_range_filter(self):
        content, is_error = handle_tool_call(
            "search_papers", {"query": "language models", "year_from": 2020, "year_to": 2022}
        )
        assert not is_error
        result = json.loads(content[0].text)
        for paper in result["papers"]:
            assert 2020 <= paper["year"] <= 2022

    def test_min_citations_filter(self):
        content, is_error = handle_tool_call(
            "search_papers", {"query": "deep learning", "min_citations": 10000}
        )
        assert not is_error
        result = json.loads(content[0].text)
        for paper in result["papers"]:
            assert paper["citation_count"] >= 10000

    def test_no_results_is_not_error(self):
        content, is_error = handle_tool_call(
            "search_papers", {"query": "quantum blockchain xyzzy"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert result["total_count"] == 0

    def test_results_have_no_full_text(self):
        content, is_error = handle_tool_call("search_papers", {"query": "transformer"})
        assert not is_error
        result = json.loads(content[0].text)
        for paper in result["papers"]:
            assert "full_text" not in paper


class TestGetCitationNetwork:
    def test_basic_network(self):
        content, is_error = handle_tool_call(
            "get_citation_network", {"paper_id": "paper-002", "depth": 1, "direction": "both"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert "entry_point" in result
        assert "nodes" in result
        assert "edges" in result

    def test_entry_point_matches_request(self):
        content, is_error = handle_tool_call("get_citation_network", {"paper_id": "paper-001"})
        assert not is_error
        result = json.loads(content[0].text)
        assert result["entry_point"]["id"] == "paper-001"

    def test_references_direction(self):
        content, is_error = handle_tool_call(
            "get_citation_network", {"paper_id": "paper-002", "depth": 1, "direction": "references"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        node_ids = {n["paper"]["id"] for n in result["nodes"]}
        assert "paper-001" in node_ids

    def test_invalid_paper_returns_is_error(self):
        content, is_error = handle_tool_call(
            "get_citation_network", {"paper_id": "paper-999"}
        )
        assert is_error
        result = json.loads(content[0].text)
        assert "error" in result

    def test_no_duplicate_edges(self):
        content, is_error = handle_tool_call(
            "get_citation_network", {"paper_id": "paper-002", "depth": 2, "direction": "both"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        edge_keys = [(e["from_paper_id"], e["to_paper_id"]) for e in result["edges"]]
        assert len(edge_keys) == len(set(edge_keys))


class TestComparePapers:
    def test_basic_comparison(self):
        content, is_error = handle_tool_call(
            "compare_papers",
            {"paper_ids": ["paper-001", "paper-002"], "dimensions": ["year", "citations"]}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert "matrix" in result
        assert "commonalities" in result
        assert "differences" in result

    def test_matrix_cell_count(self):
        """3 papers x 3 dimensions = 9 cells."""
        content, is_error = handle_tool_call(
            "compare_papers",
            {"paper_ids": ["paper-001", "paper-002", "paper-003"], "dimensions": ["year", "citations", "domain"]}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert len(result["matrix"]) == 9

    def test_invalid_paper_returns_is_error(self):
        content, is_error = handle_tool_call(
            "compare_papers",
            {"paper_ids": ["paper-001", "paper-999"], "dimensions": ["year"]}
        )
        assert is_error

    def test_single_paper_returns_is_error(self):
        content, is_error = handle_tool_call(
            "compare_papers",
            {"paper_ids": ["paper-001"], "dimensions": ["year"]}
        )
        assert is_error


class TestGetDomainStatistics:
    def test_basic_statistics(self):
        content, is_error = handle_tool_call(
            "get_domain_statistics", {"domain": "machine-learning"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert result["paper_count"] == 4
        assert "avg_citations" in result
        assert "most_cited" in result

    def test_trends_absent_by_default(self):
        content, is_error = handle_tool_call(
            "get_domain_statistics", {"domain": "machine-learning"}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert result.get("trends") is None

    def test_trends_present_when_requested(self):
        content, is_error = handle_tool_call(
            "get_domain_statistics", {"domain": "machine-learning", "include_trends": True}
        )
        assert not is_error
        result = json.loads(content[0].text)
        assert result["trends"] is not None
        assert len(result["trends"]) > 0


class TestUnknownTool:
    def test_returns_is_error(self):
        content, is_error = handle_tool_call("nonexistent_tool", {})
        assert is_error