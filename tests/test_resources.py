"""Tests for resource handlers."""

import json
import pytest
from research_server.data.store import PaperNotFoundError
from research_server.primitives.resources import (
    RESOURCE_TEMPLATES,
    STATIC_RESOURCES,
    handle_resource_read,
)
from research_server.observability.logging import configure_logging

configure_logging(level="WARNING")


class TestResourceDefinitions:
    def test_static_resource_count(self):
        assert len(STATIC_RESOURCES) == 2

    def test_static_resource_uris(self):
        uris = {str(r.uri) for r in STATIC_RESOURCES}
        assert "research://papers" in uris
        assert "research://domains" in uris

    def test_template_count(self):
        assert len(RESOURCE_TEMPLATES) == 2

    def test_template_uri_patterns(self):
        templates = {t.uriTemplate for t in RESOURCE_TEMPLATES}
        assert "research://papers/{paper_id}" in templates
        assert "research://papers/{paper_id}/citations" in templates

    def test_all_resources_have_descriptions(self):
        for r in STATIC_RESOURCES:
            assert r.description

    def test_all_templates_have_descriptions(self):
        for t in RESOURCE_TEMPLATES:
            assert t.description


class TestPapersIndex:
    def test_returns_all_papers(self):
        result = handle_resource_read("research://papers")
        data = json.loads(result[0].text)
        assert data["total"] == 12
        assert len(data["papers"]) == 12

    def test_no_full_text_in_index(self):
        result = handle_resource_read("research://papers")
        data = json.loads(result[0].text)
        for paper in data["papers"]:
            assert "full_text" not in paper

    def test_papers_have_required_fields(self):
        result = handle_resource_read("research://papers")
        data = json.loads(result[0].text)
        required = {"id", "title", "authors", "year", "domain", "tags", "citation_count"}
        for paper in data["papers"]:
            assert not required - set(paper.keys())

    def test_mime_type(self):
        result = handle_resource_read("research://papers")
        assert result[0].mimeType == "application/json"


class TestDomainsIndex:
    def test_returns_four_domains(self):
        result = handle_resource_read("research://domains")
        data = json.loads(result[0].text)
        assert len(data["domains"]) == 4

    def test_domain_paper_counts(self):
        result = handle_resource_read("research://domains")
        data = json.loads(result[0].text)
        counts = {d["domain"]: d["paper_count"] for d in data["domains"]}
        assert counts["machine-learning"] == 4
        assert counts["natural-language-processing"] == 3
        assert counts["distributed-systems"] == 3
        assert counts["computer-vision"] == 2

    def test_domain_has_top_tags(self):
        result = handle_resource_read("research://domains")
        data = json.loads(result[0].text)
        for domain in data["domains"]:
            assert "top_tags" in domain


class TestIndividualPaper:
    def test_valid_paper_has_full_text(self):
        result = handle_resource_read("research://papers/paper-001")
        data = json.loads(result[0].text)
        assert data["id"] == "paper-001"
        assert "full_text" in data
        assert "abstract" in data

    def test_invalid_paper_raises_error(self):
        with pytest.raises(PaperNotFoundError):
            handle_resource_read("research://papers/paper-999")

    def test_all_papers_readable(self):
        from research_server.data.papers import PAPERS
        for paper in PAPERS:
            result = handle_resource_read(f"research://papers/{paper.id}")
            data = json.loads(result[0].text)
            assert data["id"] == paper.id


class TestPaperCitations:
    def test_returns_citation_structure(self):
        result = handle_resource_read("research://papers/paper-001/citations")
        data = json.loads(result[0].text)
        assert "references" in data
        assert "cited_by" in data
        assert "total_references" in data
        assert "total_cited_by" in data

    def test_paper_001_has_no_references(self):
        result = handle_resource_read("research://papers/paper-001/citations")
        data = json.loads(result[0].text)
        assert data["total_references"] == 0

    def test_paper_001_has_cited_by(self):
        result = handle_resource_read("research://papers/paper-001/citations")
        data = json.loads(result[0].text)
        assert data["total_cited_by"] > 0

    def test_no_full_text_in_citations(self):
        result = handle_resource_read("research://papers/paper-002/citations")
        data = json.loads(result[0].text)
        for paper in data["references"] + data["cited_by"]:
            assert "full_text" not in paper

    def test_invalid_paper_raises_error(self):
        with pytest.raises(PaperNotFoundError):
            handle_resource_read("research://papers/paper-999/citations")


class TestUnknownURI:
    def test_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown resource URI"):
            handle_resource_read("research://unknown/path")