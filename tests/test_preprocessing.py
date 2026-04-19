from preprocessing.text_cleaner import find_citations, find_common_phrases, normalize, clean


def test_find_apa_citations():
    text = "This method was described by (Smith, 2020) and later expanded (Jones et al., 2022)."
    results = find_citations(text)
    types = [r["type"] for r in results]
    assert "apa" in types
    assert len(results) == 2


def test_find_numeric_citations():
    text = "As shown in previous work [1] and also confirmed in [2, 3]."
    results = find_citations(text)
    types = [r["type"] for r in results]
    assert "numeric" in types
    assert len(results) == 2


def test_no_citations():
    text = "This sentence has no citations at all."
    assert find_citations(text) == []


def test_normalize_whitespace():
    text = "  Hello   world\n  here  "
    assert normalize(text) == "Hello world here"


def test_normalize_removes_non_ascii():
    text = "Hello \u4e16\u754c world"
    result = normalize(text)
    assert "\u4e16\u754c" not in result
    assert "Hello" in result
    assert "world" in result


def test_find_common_phrases():
    text = "In this paper we propose a new method. For example, it works well."
    spans = find_common_phrases(text)
    assert len(spans) >= 2


def test_clean_returns_dataclass():
    text = "We propose a method [1]. The results (Smith, 2020) confirm our hypothesis."
    result = clean(text)
    assert result.cleaned
    assert isinstance(result.citation_spans, list)
    assert isinstance(result.common_phrase_spans, list)
    assert len(result.citation_spans) == 2
