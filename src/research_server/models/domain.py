"""
Domain models for the Research Intelligence Server.

These Pydantic models are the living architecture document.
Every primitive (resource, tool, prompt) is defined in terms of these models.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Domain(str, Enum):
    MACHINE_LEARNING = "machine-learning"
    DISTRIBUTED_SYSTEMS = "distributed-systems"
    NATURAL_LANGUAGE_PROCESSING = "natural-language-processing"
    COMPUTER_VISION = "computer-vision"


class CitationDirection(str, Enum):
    REFERENCES = "references"
    CITED_BY = "cited_by"
    BOTH = "both"


class ComparisonDimension(str, Enum):
    METHODOLOGY = "methodology"
    DOMAIN = "domain"
    CITATIONS = "citations"
    YEAR = "year"
    AUTHORS = "authors"


class ReviewFocus(str, Enum):
    METHODOLOGY = "methodology"
    NOVELTY = "novelty"
    REPRODUCIBILITY = "reproducibility"
    FULL = "full"


# ---------------------------------------------------------------------------
# Core domain entity
# ---------------------------------------------------------------------------

class Paper(BaseModel):
    id: str = Field(description="Unique identifier, e.g. 'paper-001'")
    title: str = Field(description="Full title of the paper")
    authors: list[str] = Field(description="Ordered list of author names")
    year: int = Field(description="Year of publication")
    domain: Domain = Field(description="Primary research domain")
    tags: list[str] = Field(description="Fine-grained topic tags")
    abstract: str = Field(description="Full abstract of the paper")
    citation_count: int = Field(description="Number of times this paper has been cited")
    references: list[str] = Field(description="Paper IDs this paper cites (outgoing edges)")
    cited_by: list[str] = Field(description="Paper IDs that cite this paper (incoming edges)")
    full_text: str = Field(description="Full body text, excluding abstract")


class PaperSummary(BaseModel):
    """
    Lightweight view of a paper used in list responses and search results.

    This is a deliberate design decision: anything that returns a collection
    returns PaperSummary, not Paper. The model navigates to the full resource
    research://papers/{id} only when it needs full text.

    Returning full text in collections would be wasteful — the model would
    receive thousands of tokens it didn't ask for.
    """
    id: str = Field(description="Unique identifier")
    title: str = Field(description="Full title of the paper")
    authors: list[str] = Field(description="Ordered list of author names")
    year: int = Field(description="Year of publication")
    domain: Domain = Field(description="Primary research domain")
    tags: list[str] = Field(description="Fine-grained topic tags")
    citation_count: int = Field(description="Number of times this paper has been cited")

    @classmethod
    def from_paper(cls, paper: "Paper") -> "PaperSummary":
        return cls(
            id=paper.id,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            domain=paper.domain,
            tags=paper.tags,
            citation_count=paper.citation_count,
        )


# ---------------------------------------------------------------------------
# Tool input models
# ---------------------------------------------------------------------------

class SearchPapersInput(BaseModel):
    query: str = Field(description="Free-text search against title, abstract, and tags")
    domain: Optional[Domain] = Field(default=None, description="Constrain to a specific domain")
    year_from: Optional[int] = Field(default=None, description="Published this year or later")
    year_to: Optional[int] = Field(default=None, description="Published this year or earlier")
    min_citations: Optional[int] = Field(default=None, description="Minimum citation count")


class GetCitationNetworkInput(BaseModel):
    paper_id: str = Field(description="Entry point paper ID for graph traversal")
    depth: int = Field(default=1, ge=1, le=3, description="Traversal depth. Max 3.")
    direction: CitationDirection = Field(
        default=CitationDirection.BOTH,
        description="Direction of traversal"
    )


class ComparePapersInput(BaseModel):
    paper_ids: list[str] = Field(
        min_length=2,
        max_length=4,
        description="IDs of papers to compare. Minimum 2, maximum 4."
    )
    dimensions: list[ComparisonDimension] = Field(
        description="Dimensions along which to compare"
    )


class GetDomainStatisticsInput(BaseModel):
    domain: Domain = Field(description="The research domain to analyse")
    include_trends: bool = Field(
        default=False,
        description="If true, include year-over-year trends"
    )


# ---------------------------------------------------------------------------
# Tool output models
# ---------------------------------------------------------------------------

class CitationNode(BaseModel):
    paper: PaperSummary = Field(description="The paper at this node")
    depth: int = Field(description="Depth from the entry point paper")
    direction: CitationDirection = Field(description="How this node was reached")


class CitationEdge(BaseModel):
    from_paper_id: str = Field(description="The citing paper")
    to_paper_id: str = Field(description="The cited paper")


class YearTrend(BaseModel):
    year: int
    paper_count: int
    total_citations: int