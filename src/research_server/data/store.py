"""
Data access layer for the Research Intelligence Server.

All queries against the static dataset go through this module.
Primitives (resources, tools, prompts) never import from data.papers directly.

This separation matters for two reasons:
1. If the data source changes (static -> database -> API), only this module changes.
2. Query logic belongs here, not scattered across primitive handlers.
"""

from research_server.data.papers import PAPERS, PAPERS_BY_ID
from research_server.models.domain import (
    CitationDirection,
    CitationEdge,
    CitationNode,
    Domain,
    Paper,
    PaperSummary,
)


class PaperNotFoundError(Exception):
    """Raised when a paper ID does not exist in the dataset."""
    def __init__(self, paper_id: str):
        self.paper_id = paper_id
        super().__init__(f"Paper not found: '{paper_id}'")


class DataStore:
    """
    In-memory data access layer over the static paper dataset.

    Methods raise PaperNotFoundError for invalid IDs rather than returning
    None. Callers handle the specific error, not a None check. This produces
    cleaner error propagation through the MCP protocol layer.
    """

    # -----------------------------------------------------------------------
    # Basic lookups
    # -----------------------------------------------------------------------

    def get_all_papers(self) -> list[Paper]:
        return PAPERS

    def get_paper_by_id(self, paper_id: str) -> Paper:
        paper = PAPERS_BY_ID.get(paper_id)
        if paper is None:
            raise PaperNotFoundError(paper_id)
        return paper

    def get_papers_by_domain(self, domain: Domain) -> list[Paper]:
        return [p for p in PAPERS if p.domain == domain]

    # -----------------------------------------------------------------------
    # Search
    # -----------------------------------------------------------------------

    def search_papers(
        self,
        query: str,
        domain: Domain | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_citations: int | None = None,
    ) -> list[Paper]:
        """
        Search papers by free-text query with optional filters.
        Query matches against title, tags, and abstract.
        All filters are AND-combined.
        Results are sorted: title matches first, then by citation count descending.
        """
        query_lower = query.lower()
        results = []

        for paper in PAPERS:
            title_match = query_lower in paper.title.lower()
            tag_match = any(query_lower in tag.lower() for tag in paper.tags)
            abstract_match = query_lower in paper.abstract.lower()

            if not (title_match or tag_match or abstract_match):
                continue

            if domain is not None and paper.domain != domain:
                continue
            if year_from is not None and paper.year < year_from:
                continue
            if year_to is not None and paper.year > year_to:
                continue
            if min_citations is not None and paper.citation_count < min_citations:
                continue

            results.append(paper)

        def sort_key(p: Paper) -> tuple:
            return (
                0 if query_lower in p.title.lower() else 1,
                -p.citation_count,
            )

        results.sort(key=sort_key)
        return results

    # -----------------------------------------------------------------------
    # Citation graph
    # -----------------------------------------------------------------------

    def get_citation_network(
        self,
        paper_id: str,
        depth: int,
        direction: CitationDirection,
    ) -> tuple[Paper, list[CitationNode], list[CitationEdge]]:
        """
        Traverse the citation graph from an entry point paper.

        Returns:
            entry_point: the paper at paper_id
            nodes: all discovered papers with depth and direction
            edges: all citation relationships discovered

        Raises PaperNotFoundError if paper_id does not exist.
        """
        entry_point = self.get_paper_by_id(paper_id)

        visited: set[str] = set()
        nodes: list[CitationNode] = []
        edges: list[CitationEdge] = []

        def traverse(current_id: str, current_depth: int, edge_direction: CitationDirection):
            if current_depth > depth or current_id in visited:
                return
            visited.add(current_id)

            try:
                current_paper = self.get_paper_by_id(current_id)
            except PaperNotFoundError:
                return

            if current_id != paper_id:
                nodes.append(CitationNode(
                    paper=PaperSummary.from_paper(current_paper),
                    depth=current_depth,
                    direction=edge_direction,
                ))

            if direction in (CitationDirection.REFERENCES, CitationDirection.BOTH):
                for ref_id in current_paper.references:
                    edges.append(CitationEdge(
                        from_paper_id=current_id,
                        to_paper_id=ref_id,
                    ))
                    traverse(ref_id, current_depth + 1, CitationDirection.REFERENCES)

            if direction in (CitationDirection.CITED_BY, CitationDirection.BOTH):
                for citer_id in current_paper.cited_by:
                    edges.append(CitationEdge(
                        from_paper_id=citer_id,
                        to_paper_id=current_id,
                    ))
                    traverse(citer_id, current_depth + 1, CitationDirection.CITED_BY)

        traverse(paper_id, 0, direction)

        # Deduplicate edges — bidirectional traversal can produce duplicates
        seen_edges: set[tuple] = set()
        unique_edges = []
        for edge in edges:
            key = (edge.from_paper_id, edge.to_paper_id)
            if key not in seen_edges:
                seen_edges.add(key)
                unique_edges.append(edge)

        return entry_point, nodes, unique_edges

    # -----------------------------------------------------------------------
    # Domain statistics
    # -----------------------------------------------------------------------

    def get_domain_statistics(self, domain: Domain) -> dict:
        domain_papers = self.get_papers_by_domain(domain)

        if not domain_papers:
            return {
                "paper_count": 0,
                "avg_citations": 0.0,
                "top_tags": [],
                "most_cited": None,
                "year_distribution": {},
                "domain_papers": [],
            }

        avg_citations = sum(p.citation_count for p in domain_papers) / len(domain_papers)
        most_cited = max(domain_papers, key=lambda p: p.citation_count)

        tag_freq: dict[str, int] = {}
        for paper in domain_papers:
            for tag in paper.tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
        top_tags = sorted(tag_freq, key=lambda t: -tag_freq[t])[:5]

        year_dist: dict[int, int] = {}
        for paper in domain_papers:
            year_dist[paper.year] = year_dist.get(paper.year, 0) + 1

        return {
            "paper_count": len(domain_papers),
            "avg_citations": round(avg_citations, 2),
            "top_tags": top_tags,
            "most_cited": most_cited,
            "year_distribution": year_dist,
            "domain_papers": domain_papers,
        }


# Module-level singleton — the entire server shares one DataStore instance
store = DataStore()