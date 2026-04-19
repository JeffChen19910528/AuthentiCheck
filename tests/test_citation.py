from citation.citation_checker import adjust_for_citations, _has_nearby_citation
from chunking.chunker import Chunk
from similarity.engine import SimilarityResult


def _make_sim(chunk_index, score):
    return SimilarityResult(
        chunk_text="some text",
        source_title="Test Source",
        source_url="https://example.com",
        source_abstract="abstract",
        lexical_score=score,
        ngram_score=score,
        semantic_score=score,
        combined_score=score,
        chunk_index=chunk_index,
    )


def _make_chunk(index, start, end):
    return Chunk(text="some text", char_start=start, char_end=end, chunk_index=index)


def test_cited_high_similarity_reduces_risk():
    body = "The method described here [1] shows high performance."
    chunks = [_make_chunk(0, 0, 30)]
    sim = [_make_sim(0, 0.8)]
    adjs = adjust_for_citations(sim, body, chunks)
    assert len(adjs) == 1
    assert adjs[0].has_citation is True
    assert adjs[0].risk_modifier < 0


def test_uncited_high_similarity_increases_risk():
    body = "The method described here shows high performance without any citation."
    chunks = [_make_chunk(0, 0, 30)]
    sim = [_make_sim(0, 0.8)]
    adjs = adjust_for_citations(sim, body, chunks)
    assert adjs[0].has_citation is False
    assert adjs[0].risk_modifier > 0


def test_below_threshold_no_adjustment():
    body = "Low similarity text here."
    chunks = [_make_chunk(0, 0, 25)]
    sim = [_make_sim(0, 0.1)]
    adjs = adjust_for_citations(sim, body, chunks)
    assert adjs[0].risk_modifier == 0.0


def test_has_nearby_citation_apa():
    body = "This was shown (Smith, 2020) in earlier work."
    assert _has_nearby_citation(body, 10, 20) is True


def test_has_nearby_citation_numeric():
    body = "As confirmed [3] in several studies."
    assert _has_nearby_citation(body, 5, 15) is True


def test_no_nearby_citation():
    body = "Plain text with no citation marks at all."
    assert _has_nearby_citation(body, 0, 10) is False
