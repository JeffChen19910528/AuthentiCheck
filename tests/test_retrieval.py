import sys
from unittest.mock import patch, MagicMock
from retrieval.source_retriever import (
    _query_semantic_scholar,
    _query_arxiv,
    _query_crossref,
    _extract_keywords,
    retrieve_sources,
    SourceResult,
)


def _mock_response(json_data=None, text_data=None, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    if json_data is not None:
        resp.json.return_value = json_data
    if text_data is not None:
        resp.text = text_data
    return resp


SS_RESPONSE = {
    "data": [
        {
            "paperId": "abc123",
            "title": "Deep Learning for NLP",
            "abstract": "We study neural approaches.",
            "authors": [{"name": "Alice"}],
            "year": 2023,
            "externalIds": {"DOI": "10.1234/test"},
        }
    ]
}

ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Attention Is All You Need</title>
    <summary>We propose a new architecture.</summary>
    <id>https://arxiv.org/abs/1706.03762</id>
  </entry>
</feed>"""

CROSSREF_RESPONSE = {
    "message": {
        "items": [
            {
                "title": ["Transformer Models"],
                "abstract": "Abstract here.",
                "author": [{"given": "Bob", "family": "Jones"}],
                "DOI": "10.5678/cr",
                "published": {"date-parts": [[2022]]},
            }
        ]
    }
}


@patch("retrieval.source_retriever.requests.get")
def test_semantic_scholar_returns_results(mock_get):
    mock_get.return_value = _mock_response(json_data=SS_RESPONSE)
    results = _query_semantic_scholar("deep learning", limit=5)
    assert len(results) == 1
    assert results[0].title == "Deep Learning for NLP"
    assert results[0].source_api == "SemanticScholar"
    assert "doi.org" in results[0].url


@patch("retrieval.source_retriever.requests.get")
def test_arxiv_returns_results(mock_get):
    mock_get.return_value = _mock_response(text_data=ARXIV_RESPONSE)
    results = _query_arxiv("attention", limit=5)
    assert len(results) == 1
    assert results[0].title == "Attention Is All You Need"
    assert results[0].source_api == "arXiv"


@patch("retrieval.source_retriever.requests.get")
def test_crossref_returns_results(mock_get):
    mock_get.return_value = _mock_response(json_data=CROSSREF_RESPONSE)
    results = _query_crossref("transformer", limit=5)
    assert len(results) == 1
    assert results[0].title == "Transformer Models"
    assert results[0].year == 2022
    assert results[0].source_api == "CrossRef"


@patch("retrieval.source_retriever.requests.get", side_effect=Exception("network error"))
def test_api_failure_returns_empty(mock_get):
    assert _query_semantic_scholar("test") == []
    assert _query_arxiv("test") == []
    assert _query_crossref("test") == []


@patch("retrieval.source_retriever._query_semantic_scholar")
@patch("retrieval.source_retriever._query_arxiv")
@patch("retrieval.source_retriever._query_crossref")
def test_retrieve_sources_deduplicates(mock_cr, mock_ax, mock_ss):
    shared = SourceResult(title="Same Paper", abstract="abc", url="https://x.com", source_api="SS")
    mock_ss.return_value = [shared]
    mock_ax.return_value = [shared]
    mock_cr.return_value = [shared]
    results = retrieve_sources("some query", top_n=5)
    titles = [r.title for r in results]
    assert titles.count("Same Paper") == 1


def test_extract_keywords_fallback():
    # keybert is imported inside _extract_keywords; force ImportError via sys.modules
    with patch.dict(sys.modules, {"keybert": None}):
        keywords = _extract_keywords("deep learning transformer attention mechanism", top_n=3)
    assert len(keywords) <= 3
    assert all(isinstance(k, str) for k in keywords)
