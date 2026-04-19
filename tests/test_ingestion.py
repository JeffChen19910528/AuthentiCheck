import sys
from unittest.mock import patch, MagicMock
from ingestion.document_parser import (
    _split_references,
    _extract_abstract,
    parse_pdf,
    parse_docx,
    parse,
    ParsedDocument,
)


SAMPLE_BODY = """Introduction to Machine Learning

Abstract
This paper presents a comprehensive overview of machine learning techniques.
We discuss supervised, unsupervised, and reinforcement learning paradigms.

Introduction
Machine learning has become a cornerstone of artificial intelligence.
Modern systems rely heavily on deep neural networks.

Methods
We employ gradient descent optimization in our approach.
The loss function is minimized iteratively.

References
[1] LeCun, Y. (1998). Gradient-based learning applied to document recognition.
[2] Vapnik, V. (1995). The Nature of Statistical Learning Theory.
"""


def test_split_references_separates_body_and_refs():
    body, refs = _split_references(SAMPLE_BODY)
    assert "References" not in body
    assert "LeCun" in refs


def test_split_references_no_refs_section():
    text = "Just some body text without any references section."
    body, refs = _split_references(text)
    assert body == text
    assert refs == ""


def test_extract_abstract_finds_abstract():
    abstract, _ = _extract_abstract(SAMPLE_BODY)
    assert "machine learning" in abstract.lower()


def test_extract_abstract_missing():
    text = "Just a body without abstract keyword."
    abstract, _ = _extract_abstract(text)
    assert abstract == ""


def test_parse_pdf_returns_parsed_document():
    page_mock = MagicMock()
    page_mock.get_text.return_value = SAMPLE_BODY
    doc_mock = MagicMock()
    doc_mock.__iter__ = MagicMock(return_value=iter([page_mock]))
    doc_mock.__len__ = MagicMock(return_value=1)
    fitz_mock = MagicMock()
    fitz_mock.open.return_value = doc_mock

    with patch.dict(sys.modules, {"fitz": fitz_mock}):
        result = parse_pdf("fake.pdf")

    assert isinstance(result, ParsedDocument)
    assert result.references != ""
    assert result.source_path == "fake.pdf"


def test_parse_docx_returns_parsed_document():
    para_mock = MagicMock()
    para_mock.text = "Introduction to Machine Learning"
    para_mock.style.name = "Title"

    body_para = MagicMock()
    body_para.text = SAMPLE_BODY
    body_para.style.name = "Normal"

    docx_module = MagicMock()
    docx_module.Document.return_value.paragraphs = [para_mock, body_para]

    with patch.dict(sys.modules, {"docx": docx_module}):
        result = parse_docx("fake.docx")

    assert isinstance(result, ParsedDocument)
    assert result.title == "Introduction to Machine Learning"


def test_parse_unsupported_extension():
    import pytest
    with pytest.raises(ValueError, match="Unsupported"):
        parse("file.txt")
