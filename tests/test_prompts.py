"""Tests for prompt handlers."""

import pytest
from mcp.types import GetPromptResult
from research_server.primitives.prompts import PROMPT_DEFINITIONS, handle_prompt_get
from research_server.observability.logging import configure_logging

configure_logging(level="WARNING")


class TestPromptDefinitions:
    def test_prompt_count(self):
        assert len(PROMPT_DEFINITIONS) == 3

    def test_prompt_names(self):
        names = {p.name for p in PROMPT_DEFINITIONS}
        assert names == {"literature_review", "paper_critique", "research_gap_analysis"}

    def test_all_prompts_have_descriptions(self):
        for p in PROMPT_DEFINITIONS:
            assert p.description

    def test_each_prompt_has_required_argument(self):
        for p in PROMPT_DEFINITIONS:
            assert any(a.required for a in p.arguments)

    def test_all_arguments_have_descriptions(self):
        for p in PROMPT_DEFINITIONS:
            for a in p.arguments:
                assert a.description


class TestLiteratureReview:
    def test_returns_get_prompt_result(self):
        result = handle_prompt_get("literature_review", {"topic": "transformers"})
        assert isinstance(result, GetPromptResult)

    def test_returns_messages_not_data(self):
        """A prompt returns a message sequence, not a content/data object."""
        result = handle_prompt_get("literature_review", {"topic": "transformers"})
        assert result.messages is not None
        assert len(result.messages) > 0

    def test_message_has_user_role(self):
        result = handle_prompt_get("literature_review", {"topic": "transformers"})
        assert result.messages[0].role == "user"

    def test_topic_in_message(self):
        result = handle_prompt_get("literature_review", {"topic": "attention mechanisms"})
        assert "attention mechanisms" in result.messages[0].content.text

    def test_domain_in_message_when_provided(self):
        result = handle_prompt_get(
            "literature_review", {"topic": "scaling", "domain": "machine-learning"}
        )
        assert "machine-learning" in result.messages[0].content.text

    def test_domain_absent_when_not_provided(self):
        result = handle_prompt_get("literature_review", {"topic": "scaling"})
        assert 'domain="' not in result.messages[0].content.text

    def test_missing_topic_raises_error(self):
        with pytest.raises(ValueError, match="topic"):
            handle_prompt_get("literature_review", {})

    def test_description_contains_topic(self):
        result = handle_prompt_get("literature_review", {"topic": "residual networks"})
        assert "residual networks" in result.description


class TestPaperCritique:
    def test_returns_message_sequence(self):
        result = handle_prompt_get("paper_critique", {"paper_id": "paper-001"})
        assert len(result.messages) > 0

    def test_paper_id_in_message(self):
        result = handle_prompt_get("paper_critique", {"paper_id": "paper-001"})
        assert "paper-001" in result.messages[0].content.text

    def test_default_focus_is_full(self):
        result = handle_prompt_get("paper_critique", {"paper_id": "paper-001"})
        assert "full" in result.messages[0].content.text.lower()

    def test_focus_in_message(self):
        result = handle_prompt_get("paper_critique", {"paper_id": "paper-001", "focus": "methodology"})
        assert "methodology" in result.messages[0].content.text.lower()

    def test_all_focus_values_valid(self):
        for focus in ["methodology", "novelty", "reproducibility", "full"]:
            result = handle_prompt_get("paper_critique", {"paper_id": "paper-001", "focus": focus})
            assert result.messages is not None

    def test_missing_paper_id_raises_error(self):
        with pytest.raises(ValueError, match="paper_id"):
            handle_prompt_get("paper_critique", {})


class TestResearchGapAnalysis:
    def test_returns_message_sequence(self):
        result = handle_prompt_get("research_gap_analysis", {"domain": "machine-learning"})
        assert len(result.messages) > 0

    def test_domain_in_message(self):
        result = handle_prompt_get("research_gap_analysis", {"domain": "distributed-systems"})
        assert "distributed-systems" in result.messages[0].content.text

    def test_optional_context_in_message(self):
        result = handle_prompt_get(
            "research_gap_analysis",
            {"domain": "machine-learning", "context": "focus on efficiency"}
        )
        assert "focus on efficiency" in result.messages[0].content.text

    def test_missing_domain_raises_error(self):
        with pytest.raises(ValueError, match="domain"):
            handle_prompt_get("research_gap_analysis", {})


class TestUnknownPrompt:
    def test_raises_value_error(self):
        with pytest.raises(ValueError, match="nonexistent"):
            handle_prompt_get("nonexistent_prompt", {})