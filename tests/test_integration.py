"""
Full pipeline integration test — no real files, no real API calls, no GPU.
Mocks: document parser, source retrieval APIs, and SentenceTransformer.
"""
from unittest.mock import patch, MagicMock
import numpy as np

from ingestion.document_parser import ParsedDocument
from retrieval.source_retriever import SourceResult
from preprocessing.text_cleaner import clean
from chunking.chunker import chunk
from similarity.engine import compute_similarity
from citation.citation_checker import adjust_for_citations
from scoring.scorer import compute_metrics
from report.generator import build_report, render_text, render_html


FAKE_BODY = """
Deep learning has transformed natural language processing tasks significantly.
Transformer architectures rely on self-attention to capture long-range dependencies.
Pre-training on large corpora leads to improved performance on downstream benchmarks.
We propose a novel fine-tuning strategy that reduces the number of trainable parameters.
Experimental results on GLUE demonstrate state-of-the-art performance across tasks.
Our method outperforms existing baselines by a significant margin (Smith, 2022).
The approach requires minimal computational resources compared to full fine-tuning.
Citation-aware training helps the model learn better representations [1].
We evaluate on standard benchmarks to ensure reproducibility of our results.
The code and pretrained models will be released upon publication of this work.
"""

FAKE_DOC = ParsedDocument(
    title="Efficient Fine-Tuning of Language Models",
    abstract="We study efficient methods for adapting pretrained language models.",
    body=FAKE_BODY,
    references="[1] Smith, J. (2022). Efficient Transformers. ICML.",
    full_text=FAKE_BODY,
    source_path="test_paper.pdf",
)

FAKE_SOURCES = [
    SourceResult(
        title="Attention Is All You Need",
        abstract="Transformer architectures rely on self-attention mechanisms for sequence modeling tasks.",
        url="https://arxiv.org/abs/1706.03762",
        source_api="arXiv",
    ),
    SourceResult(
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        abstract="Pre-training on large corpora significantly improves downstream NLP performance.",
        url="https://arxiv.org/abs/1810.04805",
        source_api="arXiv",
    ),
]


def _fake_semantic_cosine(texts):
    n = len(texts)
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        mat[i][i] = 1.0
        if i + 1 < n:
            mat[i][i + 1] = 0.65
            mat[i + 1][i] = 0.65
    return mat


@patch("retrieval.source_retriever.retrieve_sources")
@patch("similarity.engine._semantic_cosine", side_effect=_fake_semantic_cosine)
def test_full_pipeline_produces_report(mock_sem, mock_retrieve):
    mock_retrieve.return_value = FAKE_SOURCES

    # 1. preprocess
    cleaned = clean(FAKE_DOC.body)
    assert cleaned.cleaned

    # 2. chunk
    chunks = chunk(cleaned.cleaned, strategy="sentences")
    assert len(chunks) > 0

    # 3. retrieve
    sources_per_chunk = [mock_retrieve(c.text) for c in chunks]
    assert all(isinstance(s, list) for s in sources_per_chunk)

    # 4. similarity
    sim_results = compute_similarity(chunks, sources_per_chunk, semantic=True)
    assert len(sim_results) > 0
    assert all(0.0 <= r.combined_score <= 1.0 for r in sim_results)

    # 5. citation adjustment
    adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)
    assert len(adj) == len(sim_results)

    # 6. score
    metrics = compute_metrics(sim_results, adj)
    assert metrics.risk_level in ("Low", "Medium", "High")
    assert 0.0 <= metrics.overall_similarity_pct <= 100.0
    assert metrics.risk_explanation

    # 7. report
    report = build_report(FAKE_DOC.title, metrics, sim_results, adj)
    assert report.document_title == FAKE_DOC.title
    assert len(report.matches) > 0
    assert report.final_verdict
    assert "plagiarized" not in report.final_verdict.lower()

    # 8. render text
    text_out = render_text(report)
    assert "AuthentiCheck" in text_out
    assert FAKE_DOC.title in text_out
    assert "FINAL VERDICT" in text_out

    # 9. render html
    html_out = render_html(report)
    assert "<!DOCTYPE html>" in html_out
    assert FAKE_DOC.title in html_out


@patch("retrieval.source_retriever.retrieve_sources")
def test_pipeline_with_no_semantic(mock_retrieve):
    mock_retrieve.return_value = FAKE_SOURCES
    cleaned = clean(FAKE_DOC.body)
    chunks = chunk(cleaned.cleaned, strategy="paragraphs")
    sources_per_chunk = [mock_retrieve(c.text) for c in chunks]
    sim_results = compute_similarity(chunks, sources_per_chunk, semantic=False)
    assert all(r.semantic_score == 0.0 for r in sim_results)
    adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)
    metrics = compute_metrics(sim_results, adj)
    report = build_report("No Semantic Test", metrics, sim_results, adj)
    assert report.risk_level in ("Low", "Medium", "High")


@patch("retrieval.source_retriever.retrieve_sources")
def test_pipeline_with_all_cited_chunks(mock_retrieve):
    """All high-similarity chunks that have citations should yield lower risk than uncited."""
    mock_retrieve.return_value = FAKE_SOURCES

    body_with_citations = FAKE_BODY + "\n(Brown, 2020) (Lee, 2021) [2] [3] [4]"
    body_no_citations = FAKE_BODY

    def run(body):
        cleaned = clean(body)
        chunks = chunk(cleaned.cleaned)
        sources_per_chunk = [mock_retrieve(c.text) for c in chunks]
        sim_results = compute_similarity(chunks, sources_per_chunk, semantic=False)
        adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)
        return compute_metrics(sim_results, adj)

    cited_metrics = run(body_with_citations)
    uncited_metrics = run(body_no_citations)

    assert cited_metrics.uncited_similarity_ratio <= uncited_metrics.uncited_similarity_ratio
