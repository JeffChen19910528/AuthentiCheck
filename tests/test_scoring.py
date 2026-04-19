from scoring.scorer import compute_metrics, ScoreMetrics
from similarity.engine import SimilarityResult
from citation.citation_checker import CitationAdjustment


def _sim(idx, score, semantic=0.3):
    return SimilarityResult(
        chunk_text=f"chunk {idx}",
        source_title="Source",
        source_url="https://example.com",
        source_abstract="abstract",
        lexical_score=score,
        ngram_score=score,
        semantic_score=semantic,
        combined_score=score,
        chunk_index=idx,
    )


def _adj(idx, has_citation, modifier):
    return CitationAdjustment(
        chunk_index=idx,
        has_citation=has_citation,
        risk_modifier=modifier,
        reason="test",
    )


def test_empty_input_returns_low_risk():
    result = compute_metrics([], [])
    assert result.risk_level == "Low"
    assert result.overall_similarity_pct == 0.0


def test_high_risk_classification():
    sims = [_sim(i, 0.8, semantic=0.7) for i in range(5)]
    adjs = [_adj(i, False, 0.15) for i in range(5)]
    result = compute_metrics(sims, adjs)
    assert result.risk_level == "High"
    assert result.overall_similarity_pct > 40


def test_low_risk_classification():
    sims = [_sim(i, 0.1, semantic=0.1) for i in range(5)]
    adjs = [_adj(i, True, -0.15) for i in range(5)]
    result = compute_metrics(sims, adjs)
    assert result.risk_level == "Low"


def test_medium_risk_classification():
    sims = [_sim(i, 0.3, semantic=0.35) for i in range(5)]
    adjs = [_adj(i, False, 0.1) for i in range(5)]
    result = compute_metrics(sims, adjs)
    assert result.risk_level in ("Medium", "High")


def test_metrics_fields_populated():
    sims = [_sim(0, 0.6)]
    adjs = [_adj(0, False, 0.1)]
    result = compute_metrics(sims, adjs)
    assert isinstance(result, ScoreMetrics)
    assert 0 <= result.high_similarity_ratio <= 1
    assert 0 <= result.uncited_similarity_ratio <= 1
    assert 0 <= result.paraphrase_similarity_score <= 1
    assert result.risk_explanation


def test_cited_chunks_lower_uncited_ratio():
    sims = [_sim(i, 0.7) for i in range(4)]
    adjs_cited = [_adj(i, True, -0.15) for i in range(4)]
    adjs_uncited = [_adj(i, False, 0.15) for i in range(4)]
    r_cited = compute_metrics(sims, adjs_cited)
    r_uncited = compute_metrics(sims, adjs_uncited)
    assert r_cited.uncited_similarity_ratio <= r_uncited.uncited_similarity_ratio
