import re
from dataclasses import dataclass
from typing import List


_CITATION_APA = re.compile(r"\(([A-Z][a-zA-Z\-]+(?:\s+et\s+al\.)?),?\s+\d{4}[a-z]?\)")
_CITATION_NUM = re.compile(r"\[(\d+(?:,\s*\d+)*)\]")
_COMMON_ACADEMIC = re.compile(
    r"\b(in this (paper|study|work|article)|as shown in|it is (well[- ]known|widely|commonly)|"
    r"for example|for instance|such as|in order to|due to|as a result|in conclusion|"
    r"this paper (presents|proposes|introduces)|we (propose|present|introduce|show|demonstrate))\b",
    re.IGNORECASE,
)


@dataclass
class CleanedText:
    cleaned: str
    citation_spans: List[dict]  # [{start, end, raw, type}]
    common_phrase_spans: List[dict]


def find_citations(text: str) -> List[dict]:
    spans = []
    for m in _CITATION_APA.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "raw": m.group(), "type": "apa"})
    for m in _CITATION_NUM.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "raw": m.group(), "type": "numeric"})
    spans.sort(key=lambda x: x["start"])
    return spans


def find_common_phrases(text: str) -> List[dict]:
    return [
        {"start": m.start(), "end": m.end(), "raw": m.group()}
        for m in _COMMON_ACADEMIC.finditer(text)
    ]


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = text.strip()
    return text


def clean(body_text: str) -> CleanedText:
    citation_spans = find_citations(body_text)
    common_spans = find_common_phrases(body_text)
    cleaned = normalize(body_text)
    return CleanedText(
        cleaned=cleaned,
        citation_spans=citation_spans,
        common_phrase_spans=common_spans,
    )
