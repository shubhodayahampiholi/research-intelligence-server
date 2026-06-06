"""Tools for the Research Intelligence Server."""

import json
from typing import Any

import mcp.types as types

from research_server.data.store import PaperNotFoundError, store
from research_server.models.domain import (
    CitationDirection,
    ComparisonDimension,
    ComparePapersInput,
    GetCitationNetworkInput,
    GetDomainStatisticsInput,
    PaperSummary,
    SearchPapersInput,
    YearTrend,
)
from research_server.observability.logging import get_logger

logger = get_logger(__name__)

_PAPER_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "year": {"type": "integer"},
        "domain": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "citation_count": {"type": "integer"},
    },
    "required": ["id", "title", "authors", "year", "domain", "tags", "citation_count"],
}

TOOL_DEFINITIONS = [
    types.Tool(
        name="search_papers",
        description=(
            "Search papers by topic, domain, year range, or citation threshold. "
            "Returns metadata only. Use research://papers/{id} to read full content."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Free-text search against title, abstract, and tags"},
                "domain": {
                    "type": "string",
                    "enum": ["machine-learning", "distributed-systems", "natural-language-processing", "computer-vision"],
                    "description": "Constrain results to a specific domain",
                },
                "year_from": {"type": "integer", "description": "Published this year or later"},
                "year_to": {"type": "integer", "description": "Published this year or earlier"},
                "min_citations": {"type": "integer", "minimum": 0, "description": "Minimum citation count"},
            },
            "required": ["query"],
        }
    ),
    types.Tool(
        name="get_citation_network",
        description=(
            "Traverse the citation graph from a paper to a given depth. "
            "Use direction='references' to see what it builds on, "
            "'cited_by' for its influence, 'both' for the full neighbourhood."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "Entry point paper ID"},
                "depth": {"type": "integer", "minimum": 1, "maximum": 3, "default": 1, "description": "Traversal depth. Max 3."},
                "direction": {"type": "string", "enum": ["references", "cited_by", "both"], "default": "both", "description": "Direction of traversal"},
            },
            "required": ["paper_id"],
        }
    ),
    types.Tool(
        name="compare_papers",
        description="Structured comparison of 2 to 4 papers across specified dimensions.",
        inputSchema={
            "type": "object",
            "properties": {
                "paper_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 4,
                    "description": "IDs of papers to compare",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["methodology", "domain", "citations", "year", "authors"]},
                    "minItems": 1,
                    "description": "Dimensions along which to compare",
                },
            },
            "required": ["paper_ids", "dimensions"],
        }
    ),
    types.Tool(
        name="get_domain_statistics",
        description=(
            "Statistics for a domain: paper count, average citations, top tags, "
            "most cited paper, year distribution. Set include_trends=true for year-over-year data."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "enum": ["machine-learning", "distributed-systems", "natural-language-processing", "computer-vision"],
                    "description": "Domain to analyse",
                },
                "include_trends": {"type": "boolean", "default": False, "description": "Include year-over-year trends"},
            },
            "required": ["domain"],
        }
    ),
]


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _search_papers(arguments: dict[str, Any]) -> dict[str, Any]:
    inp = SearchPapersInput(**arguments)
    logger.info("Tool: search_papers", extra={"query": inp.query, "domain": inp.domain})
    papers = store.search_papers(
        query=inp.query,
        domain=inp.domain,
        year_from=inp.year_from,
        year_to=inp.year_to,
        min_citations=inp.min_citations,
    )
    return {
        "papers": [PaperSummary.from_paper(p).model_dump() for p in papers],
        "total_count": len(papers),
    }


def _get_citation_network(arguments: dict[str, Any]) -> dict[str, Any]:
    inp = GetCitationNetworkInput(**arguments)
    logger.info("Tool: get_citation_network", extra={"paper_id": inp.paper_id, "depth": inp.depth})
    entry_point, nodes, edges = store.get_citation_network(
        paper_id=inp.paper_id,
        depth=inp.depth,
        direction=inp.direction,
    )
    return {
        "entry_point": PaperSummary.from_paper(entry_point).model_dump(),
        "nodes": [n.model_dump() for n in nodes],
        "edges": [e.model_dump() for e in edges],
        "total_nodes": len(nodes),
    }


def _compare_papers(arguments: dict[str, Any]) -> dict[str, Any]:
    inp = ComparePapersInput(**arguments)
    logger.info("Tool: compare_papers", extra={"paper_ids": inp.paper_ids})
    papers = [store.get_paper_by_id(pid) for pid in inp.paper_ids]
    summaries = [PaperSummary.from_paper(p) for p in papers]

    matrix = []
    for paper in papers:
        for dimension in inp.dimensions:
            if dimension == ComparisonDimension.METHODOLOGY:
                value = ", ".join(paper.tags[:3])
            elif dimension == ComparisonDimension.DOMAIN:
                value = paper.domain.value
            elif dimension == ComparisonDimension.CITATIONS:
                value = f"{paper.citation_count:,}"
            elif dimension == ComparisonDimension.YEAR:
                value = str(paper.year)
            elif dimension == ComparisonDimension.AUTHORS:
                value = ", ".join(paper.authors[:2])
                if len(paper.authors) > 2:
                    value += f" et al. ({len(paper.authors)} total)"
            else:
                value = "N/A"
            matrix.append({"paper_id": paper.id, "dimension": dimension.value, "value": value})

    all_tags = [set(p.tags) for p in papers]
    shared_tags = set.intersection(*all_tags) if all_tags else set()
    domains = {p.domain.value for p in papers}
    years = {p.year for p in papers}
    citation_counts = [p.citation_count for p in papers]

    commonalities = []
    if len(domains) == 1:
        commonalities.append(f"All papers are in the {domains.pop()} domain")
    if shared_tags:
        commonalities.append(f"Shared tags: {', '.join(sorted(shared_tags))}")

    differences = []
    if len(domains) > 1:
        differences.append(f"Spans multiple domains: {', '.join(sorted(domains))}")
    if len(years) > 1:
        differences.append(f"Publication years range from {min(years)} to {max(years)}")
    if max(citation_counts) > min(citation_counts) * 2:
        differences.append(f"Citation impact varies: {min(citation_counts):,} to {max(citation_counts):,}")

    return {
        "papers": [s.model_dump() for s in summaries],
        "matrix": matrix,
        "commonalities": commonalities,
        "differences": differences,
    }


def _get_domain_statistics(arguments: dict[str, Any]) -> dict[str, Any]:
    inp = GetDomainStatisticsInput(**arguments)
    logger.info("Tool: get_domain_statistics", extra={"domain": inp.domain})
    stats = store.get_domain_statistics(inp.domain)

    result: dict[str, Any] = {
        "domain": inp.domain.value,
        "paper_count": stats["paper_count"],
        "avg_citations": stats["avg_citations"],
        "top_tags": stats["top_tags"],
        "most_cited": PaperSummary.from_paper(stats["most_cited"]).model_dump() if stats["most_cited"] else None,
        "year_distribution": stats["year_distribution"],
    }

    if inp.include_trends:
        result["trends"] = [
            YearTrend(
                year=year,
                paper_count=count,
                total_citations=sum(p.citation_count for p in stats["domain_papers"] if p.year == year),
            ).model_dump()
            for year, count in sorted(stats["year_distribution"].items())
        ]

    return result


_HANDLERS = {
    "search_papers": _search_papers,
        "get_citation_network": _get_citation_network,
    "compare_papers": _compare_papers,
    "get_domain_statistics": _get_domain_statistics,
}


def handle_tool_call(name: str, arguments: dict[str, Any]) -> tuple[list[types.TextContent], bool]:
    """
    Dispatch a tool call. Returns (content, is_error).
    Application errors return is_error=True — the model reads and reasons about them.
    Both structuredContent (raw dict) and text (serialised JSON) are returned per spec.
    """
    handler = _HANDLERS.get(name)
    if handler is None:
        return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: '{name}'"}, indent=2))], True

    try:
        result = handler(arguments)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))], False

    except PaperNotFoundError as e:
        logger.warning("Tool: paper not found", extra={"tool": name, "paper_id": e.paper_id})
        return [types.TextContent(type="text", text=json.dumps({"error": str(e), "paper_id": e.paper_id}, indent=2))], True

    except (ValueError, TypeError) as e:
        logger.warning("Tool: invalid input", extra={"tool": name, "error": str(e)})
        return [types.TextContent(type="text", text=json.dumps({"error": f"Invalid input: {str(e)}"}, indent=2))], True

    except Exception as e:
        logger.error("Tool: unexpected error", extra={"tool": name, "error": str(e)}, exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"error": "Internal server error"}, indent=2))], True