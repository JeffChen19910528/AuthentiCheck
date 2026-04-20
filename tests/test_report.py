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
    assert "Matched Sources" in text
    assert "Final Verdict" in text
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
    report = build_report("Paper", _metrics("High", 65.0), sims, adjs, lang="en")
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


# --- New: location, action, full text ---

def test_match_has_chunk_index():
    sims = [_sim(3)]
    adjs = [_adj(3)]
    report = build_report("Paper", _metrics(), sims, adjs)
    assert report.matches[0].chunk_index == 3


def test_uncited_match_action_is_add_citation():
    sims = [_sim(0, score=0.6, semantic=0.3)]
    adjs = [_adj(0, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs)
    assert report.matches[0].action == "add_citation"


def test_high_semantic_uncited_action_is_rewrite():
    sims = [_sim(0, score=0.6, semantic=0.8)]
    adjs = [_adj(0, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs)
    assert report.matches[0].action == "rewrite"


def test_cited_match_action_is_ok():
    sims = [_sim(0, score=0.6, semantic=0.4)]
    adjs = [_adj(0, cited=True)]
    report = build_report("Paper", _metrics(), sims, adjs)
    assert report.matches[0].action == "ok"


def test_match_chunk_text_is_full_not_truncated():
    long_text = "Word " * 200
    sim = SimilarityResult(
        chunk_text=long_text,
        source_title="Source",
        source_url="https://example.com",
        source_abstract="abstract",
        lexical_score=0.6,
        ngram_score=0.6,
        semantic_score=0.4,
        combined_score=0.6,
        chunk_index=0,
    )
    adjs = [_adj(0)]
    report = build_report("Paper", _metrics(), [sim], adjs)
    assert len(report.matches[0].chunk_text) == len(long_text)


def test_render_text_shows_location_and_action():
    sims = [_sim(2)]
    adjs = [_adj(2, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs)
    text = render_text(report)
    assert "Paragraph #3" in text
    assert "Action Required" in text


def test_render_html_shows_action_css_class():
    sims = [_sim(0, score=0.6, semantic=0.3)]
    adjs = [_adj(0, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs)
    html = render_html(report)
    assert "action-cite" in html


def test_render_html_shows_rewrite_css_class():
    sims = [_sim(0, score=0.6, semantic=0.8)]
    adjs = [_adj(0, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs)
    html = render_html(report)
    assert "action-rewrite" in html


def test_render_html_shows_ok_css_class():
    sims = [_sim(0, score=0.6, semantic=0.4)]
    adjs = [_adj(0, cited=True)]
    report = build_report("Paper", _metrics(), sims, adjs)
    html = render_html(report)
    assert "action-ok" in html


def test_render_html_passage_contains_full_chunk():
    sims = [_sim(0)]
    adjs = [_adj(0)]
    report = build_report("Paper", _metrics(), sims, adjs)
    html = render_html(report)
    assert "chunk number 0" in html


def test_render_text_zh_tw_shows_location():
    sims = [_sim(1)]
    adjs = [_adj(1, cited=False)]
    report = build_report("Paper", _metrics(), sims, adjs, lang="zh-TW")
    text = render_text(report, lang="zh-TW")
    assert "第 2 段" in text
    assert "建議動作" in text
