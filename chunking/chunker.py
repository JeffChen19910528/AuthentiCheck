import re
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    text: str
    char_start: int
    char_end: int
    chunk_index: int


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _sentence_split(text: str) -> List[str]:
    parts = _SENTENCE_END.split(text)
    return [p.strip() for p in parts if p.strip()]


def chunk_by_sentences(text: str, window: int = 3, step: int = 1) -> List[Chunk]:
    sentences = _sentence_split(text)
    chunks: List[Chunk] = []
    offset = 0
    sent_positions = []

    for s in sentences:
        idx = text.find(s, offset)
        sent_positions.append((idx, idx + len(s)))
        offset = idx + len(s)

    for i in range(0, len(sentences) - window + 1, step):
        group = sentences[i : i + window]
        chunk_text = " ".join(group)
        start = sent_positions[i][0]
        end = sent_positions[min(i + window - 1, len(sent_positions) - 1)][1]
        chunks.append(Chunk(text=chunk_text, char_start=start, char_end=end, chunk_index=len(chunks)))

    if not chunks and sentences:
        chunk_text = " ".join(sentences)
        chunks.append(Chunk(text=chunk_text, char_start=0, char_end=len(text), chunk_index=0))

    return chunks


def chunk_by_paragraphs(text: str) -> List[Chunk]:
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: List[Chunk] = []
    offset = 0
    for para in paragraphs:
        para = para.strip()
        if len(para) < 50:
            offset = text.find(para, offset) + len(para)
            continue
        start = text.find(para, offset)
        end = start + len(para)
        chunks.append(Chunk(text=para, char_start=start, char_end=end, chunk_index=len(chunks)))
        offset = end
    return chunks


def chunk(text: str, strategy: str = "sentences") -> List[Chunk]:
    if strategy == "paragraphs":
        return chunk_by_paragraphs(text)
    return chunk_by_sentences(text)
