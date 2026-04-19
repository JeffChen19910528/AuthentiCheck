from dataclasses import dataclass
from typing import List


@dataclass
class ScoreMetrics:
    overall_similarity_pct: float       # weighted average combined score × 100
    high_similarity_ratio: float        # fraction of chunks above high_threshold
    uncited_similarity_ratio: float     # fraction of high-similarity chunks without citation
    paraphrase_similarity_score: float  # average semantic score across all chunks
    risk_level: str                     # "Low" | "Medium" | "High"
    risk_explanation: str


def compute_metrics(
    similarity_results: List[object],
    citation_adjustments: List[object],
    high_threshold: float = 0.45,
) -> ScoreMetrics:
    if not similarity_results:
        return ScoreMetrics(
            overall_similarity_pct=0.0,
            high_similarity_ratio=0.0,
            uncited_similarity_ratio=0.0,
            paraphrase_similarity_score=0.0,
            risk_level="Low",
            risk_explanation="No similarity data available.",
        )

    adj_map = {a.chunk_index: a for a in citation_adjustments}

    scores = [r.combined_score for r in similarity_results]
    adjusted_scores = []
    for r in similarity_results:
        adj = adj_map.get(r.chunk_index)
        mod = adj.risk_modifier if adj else 0.0
        adjusted_scores.append(min(1.0, max(0.0, r.combined_score + mod)))

    overall = sum(adjusted_scores) / len(adjusted_scores) * 100

    high_chunks = [r for r in similarity_results if r.combined_score >= high_threshold]
    high_ratio = len(high_chunks) / len(similarity_results) if similarity_results else 0.0

    uncited_high = [
        r for r in high_chunks
        if adj_map.get(r.chunk_index) and not adj_map[r.chunk_index].has_citation
    ]
    uncited_ratio = len(uncited_high) / len(high_chunks) if high_chunks else 0.0

    paraphrase_score = sum(r.semantic_score for r in similarity_results) / len(similarity_results)

    risk_level, risk_explanation = _classify(overall, high_ratio, uncited_ratio, paraphrase_score)

    return ScoreMetrics(
        overall_similarity_pct=round(overall, 1),
        high_similarity_ratio=round(high_ratio, 3),
        uncited_similarity_ratio=round(uncited_ratio, 3),
        paraphrase_similarity_score=round(paraphrase_score, 3),
        risk_level=risk_level,
        risk_explanation=risk_explanation,
    )


def _classify(
    overall: float,
    high_ratio: float,
    uncited_ratio: float,
    paraphrase: float,
) -> tuple:
    if overall >= 40 and (uncited_ratio >= 0.5 or paraphrase >= 0.6):
        return (
            "High",
            "A large proportion of the document contains uncited or paraphrased content "
            "that closely matches external sources, indicating a high likelihood of plagiarism risk.",
        )
    elif overall >= 20 or uncited_ratio >= 0.3 or paraphrase >= 0.4:
        return (
            "Medium",
            "Moderate similarity with some uncited passages detected. "
            "The document may contain paraphrased content that warrants further review.",
        )
    else:
        return (
            "Low",
            "Most similar passages appear to be properly cited or consist of common academic phrasing. "
            "Similarity levels are within acceptable range.",
        )
