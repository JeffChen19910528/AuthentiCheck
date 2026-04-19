import re
from dataclasses import dataclass
from typing import List


_WINDOW = 300  # characters around a chunk to search for citations

_CITATION_APA = re.compile(r"\(([A-Z][a-zA-Z\-]+(?:\s+et\s+al\.)?),?\s+\d{4}[a-z]?\)")
_CITATION_NUM = re.compile(r"\[(\d+(?:,\s*\d+)*)\]")


@dataclass
class CitationAdjustment:
    chunk_index: int
    has_citation: bool
    risk_modifier: float  # negative = lower risk, positive = higher risk
    reason: str


def _has_nearby_citation(body_text: str, char_start: int, char_end: int) -> bool:
    window_start = max(0, char_start - _WINDOW)
    window_end = min(len(body_text), char_end + _WINDOW)
    window = body_text[window_start:window_end]
    return bool(_CITATION_APA.search(window) or _CITATION_NUM.search(window))


def adjust_for_citations(
    similarity_results: List[object],
    body_text: str,
    chunks: List[object],
    high_threshold: float = 0.45,
) -> List[CitationAdjustment]:
    chunk_map = {c.chunk_index: c for c in chunks}
    adjustments: List[CitationAdjustment] = []

    for res in similarity_results:
        if res.combined_score < high_threshold:
            adjustments.append(CitationAdjustment(
                chunk_index=res.chunk_index,
                has_citation=False,
                risk_modifier=0.0,
                reason="similarity below threshold, no adjustment",
            ))
            continue

        chunk = chunk_map.get(res.chunk_index)
        if chunk is None:
            continue

        cited = _has_nearby_citation(body_text, chunk.char_start, chunk.char_end)

        if cited:
            modifier = -0.15
            reason = "high similarity but citation found nearby — risk reduced"
        else:
            modifier = +0.15
            reason = "high similarity with no citation — risk increased"

        adjustments.append(CitationAdjustment(
            chunk_index=res.chunk_index,
            has_citation=cited,
            risk_modifier=modifier,
            reason=reason,
        ))

    return adjustments
