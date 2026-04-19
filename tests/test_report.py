from report.generator import build_report, render_text, render_html, Report
from similarity.engine import SimilarityResult
from citation.citation_checker import CitationAdjustment
from scoring.scorer import ScoreMetrics


def _metrics(risk="Medium", overall=30.0):
    return ScoreMetrics(
        overall_similarity_pct=overall,
        high_similarity_ratio=0.3,
        uncited_similarity_ratio=0.4,
        paraphrase_similarity_score=0.35,
        risk_level=risk,
        risk_explanation="Test explanation.",
    )


def _sim(idx, score=0.6, semantic=0.4):
    return SimilarityResult(
        chunk_text=f"This is chunk number {idx} with some academic content.",
        source_title=f"Paper Title {idx}",
        source_url=f"https://example.com/{idx}",
        source_abstract="Abstract text here.",
        lexical_score=score,
        ngram_score=score,
        semantic_score=semantic,
        combined_score=score,
        chunk_index=idx,
    )


def _adj(idx, cited=False):
    return CitationAdjustment(
        chunk_index=idx,
        has_citation=cited,
        risk_modifier=0.0,
        reason="test",
    )


def test_build_report_returns_report_object():
    sims = [_sim(i) for i in range(3)]
    adjs = [_adj(i) for i in range(3)]
    report = build_report("Test Paper", _metrics(), sims, adjs)
    assert isinstance(report, Report)
    assert report.document_title == "Test Paper"
    assert report.risk_level == "Medium"


def test_report_has_matches():
    sims = [_sim(i) for i in range(5)]
    adjs = [_adj(i) for i in range(5)]
    report = build_report("Test", _metrics(), sims, adjs)
    assert len(report.matches) > 0


def test_render_text_contains_key_sections():
    sims = [_sim(0)]
    adjs = [_adj(0)]
    report = build_report("My Paper", _metrics(), sims, adjs)
    text = render_text(report)
    assert "AuthentiCheck" in text
    assert "My Paper" in text
    assert "MATCHED SOURCES" in text
    assert "FINAL VERDICT" in text
    assert "30.0%" in text


def test_render_html_is_valid_html():
    sims = [_sim(0)]
    adjs = [_adj(0)]
    report = build_report("HTML Paper", _metrics("High", 55.0), sims, adjs)
    html = render_html(report)
    assert html.startswith("<!DOCTYPE html>")
    assert "HTML Paper" in html
    assert "55.0%" in html
    assert "High" in html


def test_high_risk_verdict_language():
    sims = [_sim(0, 0.9)]
    adjs = [_adj(0, False)]
    report = build_report("Paper", _metrics("High", 65.0), sims, adjs)
    assert "plagiarism risk" in report.final_verdict.lower()
    assert "plagiarized" not in report.final_verdict.lower()


def test_low_risk_verdict_language():
    sims = [_sim(0, 0.1)]
    adjs = [_adj(0, True)]
    report = build_report("Paper", _metrics("Low", 5.0), sims, adjs)
    assert "low" in report.final_verdict.lower()


def test_cited_match_shows_cited_tag():
    sims = [_sim(0)]
    adjs = [_adj(0, cited=True)]
    report = build_report("Paper", _metrics(), sims, adjs)
    assert report.matches[0].has_citation is True
