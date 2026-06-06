"""Prompts for the Research Intelligence Server."""

import mcp.types as types
from research_server.observability.logging import get_logger

logger = get_logger(__name__)

PROMPT_DEFINITIONS = [
    types.Prompt(
        name="literature_review",
        description="Set up a structured literature review on a topic or domain.",
        arguments=[
            types.PromptArgument(name="topic", description="Subject of the review", required=True),
            types.PromptArgument(
                name="domain",
                description="Constrain to: machine-learning, distributed-systems, natural-language-processing, computer-vision",
                required=False,
            ),
            types.PromptArgument(name="max_papers", description="Max papers to review (default: 5)", required=False),
        ],
    ),
    types.Prompt(
        name="paper_critique",
        description="Set up a rigorous academic critique of a specific paper.",
        arguments=[
            types.PromptArgument(name="paper_id", description="ID of the paper to critique", required=True),
            types.PromptArgument(
                name="focus",
                description="methodology | novelty | reproducibility | full (default: full)",
                required=False,
            ),
        ],
    ),
    types.Prompt(
        name="research_gap_analysis",
        description="Set up a research gap analysis for a domain.",
        arguments=[
            types.PromptArgument(
                name="domain",
                description="One of: machine-learning, distributed-systems, natural-language-processing, computer-vision",
                required=True,
            ),
            types.PromptArgument(name="context", description="Optional additional context or constraints", required=False),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Handlers — each builds and returns a message sequence
# ---------------------------------------------------------------------------

def _literature_review(arguments: dict[str, str]) -> types.GetPromptResult:
    topic = arguments.get("topic", "")
    if not topic:
        raise ValueError("'topic' is required")

    domain = arguments.get("domain")
    max_papers = arguments.get("max_papers", "5")
    domain_instruction = f" Focus on the **{domain}** domain." if domain else ""
    domain_filter = f' Filter by domain="{domain}".' if domain else ""

    text = f"""You are conducting a structured literature review.

**Topic:** {topic}{domain_instruction}
**Papers to review:** Up to {max_papers}

**Step 1 — Discovery**
Use `search_papers` to find relevant papers.{domain_filter}

**Step 2 — Selection**
Select the {max_papers} most relevant papers by relevance, citation impact, and recency.

**Step 3 — Deep Reading**
Read each selected paper via `research://papers/{{paper_id}}`.

**Step 4 — Analysis**
For each paper assess: core contribution, methodology, key findings.
Use `get_citation_network` to understand relationships between papers.

**Step 5 — Synthesis**
Structure your review with:
1. Overview of the field
2. Key methodologies
3. Major contributions
4. Connections between papers
5. Research gaps

Begin with Step 1."""

    logger.info("Prompt: literature_review", extra={"topic": topic, "domain": domain})
    return types.GetPromptResult(
        description=f"Literature review on: {topic}",
        messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))],
    )


def _paper_critique(arguments: dict[str, str]) -> types.GetPromptResult:
    paper_id = arguments.get("paper_id", "")
    if not paper_id:
        raise ValueError("'paper_id' is required")

    focus = arguments.get("focus", "full")

    criteria = {
        "methodology": (
            "Evaluate research design and validity:\n"
            "- Is the research question clearly stated?\n"
            "- Are methodology and baselines rigorous?\n"
            "- Are results statistically sound?\n"
            "- What are the limitations?"
        ),
        "novelty": (
            "Evaluate contribution and originality:\n"
            "- What is the core novelty claim?\n"
            "- Does it sufficiently differentiate from prior work?\n"
            "- Is the contribution incremental or transformative?"
        ),
        "reproducibility": (
            "Evaluate clarity and replicability:\n"
            "- Are methods described in sufficient detail?\n"
            "- Is code or data released?\n"
            "- Are hyperparameters and compute requirements reported?"
        ),
        "full": (
            "Evaluate across all dimensions:\n"
            "**Methodology:** Research design, experimental rigour, validation\n"
            "**Novelty:** Originality, differentiation, significance\n"
            "**Reproducibility:** Clarity, completeness, replication feasibility"
        ),
    }.get(focus, "Evaluate the paper across all dimensions.")

    text = f"""You are conducting a rigorous academic critique.

**Paper ID:** {paper_id}
**Focus:** {focus}

**Step 1 — Read**
Read the full paper: `research://papers/{paper_id}`
Check citation context: `research://papers/{paper_id}/citations`

**Step 2 — Context**
Read the most relevant cited papers to understand positioning.

**Step 3 — Evaluate**
{criteria}

**Step 4 — Verdict**
- **Strengths** (2-3 specific, evidenced points)
- **Weaknesses** (2-3 specific, evidenced points)
- **Overall Assessment** (one paragraph, direct and honest)

Begin with Step 1."""

    logger.info("Prompt: paper_critique", extra={"paper_id": paper_id, "focus": focus})
    return types.GetPromptResult(
        description=f"Critique of {paper_id} — focus: {focus}",
        messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))],
    )


def _research_gap_analysis(arguments: dict[str, str]) -> types.GetPromptResult:
    domain = arguments.get("domain", "")
    if not domain:
        raise ValueError("'domain' is required")

    context = arguments.get("context")
    context_block = f"\n**Additional Context:** {context}\n" if context else ""

    text = f"""You are conducting a research gap analysis.

**Domain:** {domain}{context_block}

**Step 1 — Landscape**
Read the domain overview: `research://domains`
Get domain statistics: `get_domain_statistics` with domain="{domain}" and include_trends=true.

**Step 2 — Inventory**
Use `search_papers` to find all papers in {domain}.
Note each paper's year, citations, methodology, and problem addressed.

**Step 3 — Citation Analysis**
For the 2-3 most cited papers use `get_citation_network` with direction="both" and depth=2.
Identify which ideas are heavily built upon and which are underexplored.

**Step 4 — Gap Identification**
Look for:
- **Temporal gaps:** Active topics with recent sparse publication
- **Methodological gaps:** Approaches mentioned but never deeply explored
- **Cross-domain gaps:** Underexplored connections to other domains
- **Scale gaps:** Problems validated at small scale but not large
- **Application gaps:** Strong theory without practice, or vice versa

**Step 5 — Directions**
For the 3 most promising gaps:
- The specific gap (precise, not vague)
- Why it matters
- What prior work provides a foundation
- A concrete research question that would address it

Begin with Step 1."""

    logger.info("Prompt: research_gap_analysis", extra={"domain": domain})
    return types.GetPromptResult(
        description=f"Research gap analysis for: {domain}",
        messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))],
    )


_HANDLERS = {
    "literature_review": _literature_review,
    "paper_critique": _paper_critique,
    "research_gap_analysis": _research_gap_analysis,
}


def handle_prompt_get(name: str, arguments: dict[str, str]) -> types.GetPromptResult:
    """
    Dispatch a prompts/get request.
    Unlike tools, failures raise exceptions — a prompt failure is a configuration
    error, not something the model should reason about.
    """
    handler = _HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown prompt: '{name}'")
    return handler(arguments or {})