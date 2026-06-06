"""
Resource handlers for the Research Intelligence Server.

WHAT THE PROTOCOL SAYS ABOUT RESOURCES
───────────────────────────────────────
A resource has:
  uri:         the address (e.g. "research://papers/paper-001")
  name:        human-readable name
  description: what this resource contains
  mimeType:    content type

When the client calls resources/read, the server returns:
  contents: list of ResourceContent
    Each content has: uri, mimeType, and text (str) or blob (bytes)

STATIC RESOURCES vs RESOURCE TEMPLATES
────────────────────────────────────────
Static resources have a fixed URI — research://papers, research://domains.
Resource templates use URI placeholders (RFC 6570):
  research://papers/{paper_id}
  research://papers/{paper_id}/citations

The client declares templates via resources/templates/list, expands them
with concrete values, then calls resources/read with the expanded URI.

WIRE FORMAT (what the SDK abstracts for us)
────────────────────────────────────────────
resources/list response:
{
  "resources": [
    {
      "uri": "research://papers",
      "name": "Paper Collection Index",
      "description": "...",
      "mimeType": "application/json"
    }
  ]
}

resources/read response:
{
  "contents": [
    {
      "uri": "research://papers",
      "mimeType": "application/json",
      "text": "{\"papers\": [...]}"
    }
  ]
}
"""

import json
from typing import Any

import mcp.types as types

from research_server.data.store import PaperNotFoundError, store
from research_server.models.domain import Domain, PaperSummary
from research_server.observability.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Resource and template definitions
# Returned by resources/list and resources/templates/list
# ---------------------------------------------------------------------------

STATIC_RESOURCES = [
    types.Resource(
        uri="research://papers",                        # type: ignore[arg-type]
        name="Paper Collection Index",
        description=(
            "Complete index of all research papers in the server. "
            "Returns metadata for all papers — title, authors, year, domain, "
            "tags, and citation count. Does not include full text. "
            "Use this to discover what papers exist before reading individual ones."
        ),
        mimeType="application/json",
    ),
    types.Resource(
        uri="research://domains",                       # type: ignore[arg-type]
        name="Domain Index",
        description=(
            "Overview of all research domains covered by this server. "
            "Returns each domain with paper count and most frequent tags. "
            "Use this to understand the knowledge landscape before searching."
        ),
        mimeType="application/json",
    ),
]

RESOURCE_TEMPLATES = [
    types.ResourceTemplate(
        uriTemplate="research://papers/{paper_id}",
        name="Individual Paper",
        description=(
            "Full content of a specific paper including abstract and full text. "
            "Use the Paper Collection Index (research://papers) to discover valid IDs. "
            "Example: research://papers/paper-001"
        ),
        mimeType="application/json",
    ),
    types.ResourceTemplate(
        uriTemplate="research://papers/{paper_id}/citations",
        name="Paper Citation List",
        description=(
            "Flat citation data for a paper: which papers it cites (references) "
            "and which papers cite it (cited_by). "
            "For deep graph traversal with depth and direction control, "
            "use the get_citation_network tool instead. "
            "Example: research://papers/paper-001/citations"
        ),
        mimeType="application/json",
    ),
]


# ---------------------------------------------------------------------------
# Resource read handlers
# ---------------------------------------------------------------------------

def _read_papers_index() -> dict[str, Any]:
    papers = store.get_all_papers()
    summaries = [PaperSummary.from_paper(p).model_dump() for p in papers]
    logger.info("Resource read: papers index", extra={"paper_count": len(summaries)})
    return {"papers": summaries, "total": len(summaries)}


def _read_domains_index() -> dict[str, Any]:
    domains_data = []
    for domain in Domain:
        papers = store.get_papers_by_domain(domain)
        tag_freq: dict[str, int] = {}
        for paper in papers:
            for tag in paper.tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
        top_tags = sorted(tag_freq, key=lambda t: -tag_freq[t])[:5]
        domains_data.append({
            "domain": domain.value,
            "paper_count": len(papers),
            "top_tags": top_tags,
        })
    logger.info("Resource read: domains index")
    return {"domains": domains_data}


def _read_individual_paper(paper_id: str) -> dict[str, Any]:
    paper = store.get_paper_by_id(paper_id)
    logger.info(
        "Resource read: individual paper",
        extra={"paper_id": paper_id, "title": paper.title}
    )
    return paper.model_dump()


def _read_paper_citations(paper_id: str) -> dict[str, Any]:
    paper = store.get_paper_by_id(paper_id)

    references = []
    for ref_id in paper.references:
        try:
            ref_paper = store.get_paper_by_id(ref_id)
            references.append(PaperSummary.from_paper(ref_paper).model_dump())
        except PaperNotFoundError:
            logger.warning(
                "Citation reference not found",
                extra={"paper_id": paper_id, "missing_ref_id": ref_id}
            )

    cited_by = []
    for citer_id in paper.cited_by:
        try:
            citer_paper = store.get_paper_by_id(citer_id)
            cited_by.append(PaperSummary.from_paper(citer_paper).model_dump())
        except PaperNotFoundError:
            logger.warning(
                "Citing paper not found",
                extra={"paper_id": paper_id, "missing_citer_id": citer_id}
            )

    logger.info(
        "Resource read: paper citations",
        extra={
            "paper_id": paper_id,
            "reference_count": len(references),
            "cited_by_count": len(cited_by),
        }
    )

    return {
        "paper_id": paper_id,
        "references": references,
        "cited_by": cited_by,
        "total_references": len(references),
        "total_cited_by": len(cited_by),
    }


# ---------------------------------------------------------------------------
# Unified read dispatcher
# ---------------------------------------------------------------------------

def handle_resource_read(uri: str) -> list[types.TextResourceContents]:
    """
    Dispatch a resources/read request to the correct handler based on URI.

    Parses the URI and routes to the appropriate handler. Returns a list
    because the protocol allows a single URI to return multiple content items
    (e.g. a multi-part document). In practice we return one item per URI.

    Raises:
        PaperNotFoundError: propagated to the server layer which converts
            it to a protocol-level error response.
        ValueError: for URIs that match no known pattern.
    """
    uri_str = str(uri)

    if uri_str == "research://papers":
        data = _read_papers_index()
    elif uri_str == "research://domains":
        data = _read_domains_index()
    elif uri_str.startswith("research://papers/"):
        path = uri_str.removeprefix("research://papers/")
        if path.endswith("/citations"):
            paper_id = path.removesuffix("/citations")
            data = _read_paper_citations(paper_id)
        else:
            data = _read_individual_paper(path)
    else:
        raise ValueError(f"Unknown resource URI: '{uri_str}'")

    return [
        types.TextResourceContents(
            uri=uri,            # type: ignore[arg-type]
            mimeType="application/json",
            text=json.dumps(data, indent=2),
        )
    ]