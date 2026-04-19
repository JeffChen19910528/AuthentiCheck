from dataclasses import dataclass
from typing import List, Tuple
import re


@dataclass
class SimilarityResult:
    chunk_text: str
    source_title: str
    source_url: str
    source_abstract: str
    lexical_score: float     # TF-IDF cosine similarity
    ngram_score: float       # n-gram overlap
    semantic_score: float    # sentence-transformer cosine
    combined_score: float
    chunk_index: int


def _get_ngrams(text: str, n: int) -> set:
    tokens = re.findall(r"\b\w+\b", text.lower())
    return set(zip(*[tokens[i:] for i in range(n)])) if len(tokens) >= n else set()


def _ngram_overlap(a: str, b: str, n: int = 3) -> float:
    grams_a = _get_ngrams(a, n)
    grams_b = _get_ngrams(b, n)
    if not grams_a or not grams_b:
        return 0.0
    return len(grams_a & grams_b) / max(len(grams_a), len(grams_b))


def _tfidf_cosine(texts: List[str]) -> List[List[float]]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform(texts)
    return cosine_similarity(matrix).tolist()


def _semantic_cosine(texts: List[str]) -> List[List[float]]:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, convert_to_numpy=True)
    return cosine_similarity(embeddings).tolist()


def compute_similarity(
    chunks: List[object],
    sources_per_chunk: List[List[object]],
    semantic: bool = True,
) -> List[SimilarityResult]:
    results: List[SimilarityResult] = []

    all_texts: List[str] = []
    pairs: List[Tuple[int, int, object, object]] = []

    for ci, (chunk, sources) in enumerate(zip(chunks, sources_per_chunk)):
        for source in sources:
            candidate = source.abstract or source.title
            if not candidate.strip():
                continue
            all_texts.append(chunk.text)
            all_texts.append(candidate)
            pairs.append((ci, len(all_texts) - 2, chunk, source))

    if not all_texts:
        return results

    tfidf_matrix = _tfidf_cosine(all_texts)

    if semantic:
        sem_matrix = _semantic_cosine(all_texts)
    else:
        sem_matrix = [[0.0] * len(all_texts)] * len(all_texts)

    for ci, idx_a, chunk, source in pairs:
        idx_b = idx_a + 1
        lex = float(tfidf_matrix[idx_a][idx_b])
        ngram = _ngram_overlap(chunk.text, all_texts[idx_b])
        sem = float(sem_matrix[idx_a][idx_b]) if semantic else 0.0
        combined = 0.4 * lex + 0.2 * ngram + 0.4 * sem

        results.append(SimilarityResult(
            chunk_text=chunk.text,
            source_title=source.title,
            source_url=source.url,
            source_abstract=source.abstract,
            lexical_score=round(lex, 4),
            ngram_score=round(ngram, 4),
            semantic_score=round(sem, 4),
            combined_score=round(combined, 4),
            chunk_index=ci,
        ))

    results.sort(key=lambda r: r.combined_score, reverse=True)
    return results
