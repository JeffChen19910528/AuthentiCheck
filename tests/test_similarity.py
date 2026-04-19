from unittest.mock import patch
import numpy as np
from similarity.engine import compute_similarity, _get_ngrams, _ngram_overlap, SimilarityResult
from chunking.chunker import Chunk
from retrieval.source_retriever import SourceResult


def _chunk(idx, text):
    return Chunk(text=text, char_start=0, char_end=len(text), chunk_index=idx)


def _source(title, abstract):
    return SourceResult(title=title, abstract=abstract, url="https://x.com", source_api="test")


CHUNK_A = _chunk(0, "Deep learning models use transformer architectures for sequence tasks.")
CHUNK_B = _chunk(1, "Attention mechanisms are fundamental to modern NLP systems.")
SOURCE_A = _source("Transformers Paper", "Transformer architectures enable powerful sequence modeling with attention.")
SOURCE_B = _source("NLP Survey", "Natural language processing uses deep neural networks.")


def _mock_semantic(texts):
    n = len(texts)
    mat = np.eye(n, dtype=float)
    for i in range(0, n - 1, 2):
        mat[i][i + 1] = 0.7
        mat[i + 1][i] = 0.7
    return mat.tolist()


def test_ngrams_basic():
    grams = _get_ngrams("the quick brown fox", 2)
    assert ("the", "quick") in grams
    assert ("quick", "brown") in grams


def test_ngrams_too_short():
    grams = _get_ngrams("hi", 3)
    assert grams == set()


def test_ngram_overlap_identical():
    assert _ngram_overlap("the quick brown fox", "the quick brown fox") == 1.0


def test_ngram_overlap_no_overlap():
    score = _ngram_overlap("hello world today", "apple orange banana")
    assert score == 0.0


def test_ngram_overlap_partial():
    # share "deep learning nlp" prefix tokens but differ in the rest
    score = _ngram_overlap(
        "deep learning nlp tasks are common in research",
        "deep learning nlp models are widely used now",
    )
    assert 0.0 < score < 1.0


@patch("similarity.engine._semantic_cosine")
def test_compute_similarity_returns_results(mock_sem):
    mock_sem.side_effect = _mock_semantic
    chunks = [CHUNK_A]
    sources = [[SOURCE_A]]
    results = compute_similarity(chunks, sources, semantic=True)
    assert len(results) > 0
    assert all(isinstance(r, SimilarityResult) for r in results)


@patch("similarity.engine._semantic_cosine")
def test_results_sorted_descending(mock_sem):
    mock_sem.side_effect = _mock_semantic
    chunks = [CHUNK_A, CHUNK_B]
    sources = [[SOURCE_A], [SOURCE_B]]
    results = compute_similarity(chunks, sources, semantic=True)
    scores = [r.combined_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_compute_similarity_no_semantic():
    chunks = [CHUNK_A]
    sources = [[SOURCE_A]]
    results = compute_similarity(chunks, sources, semantic=False)
    assert len(results) > 0
    assert all(r.semantic_score == 0.0 for r in results)


def test_empty_sources_returns_empty():
    chunks = [CHUNK_A]
    sources = [[]]
    results = compute_similarity(chunks, sources, semantic=False)
    assert results == []


def test_combined_score_in_range():
    chunks = [CHUNK_A]
    sources = [[SOURCE_A]]
    results = compute_similarity(chunks, sources, semantic=False)
    for r in results:
        assert 0.0 <= r.combined_score <= 1.0
