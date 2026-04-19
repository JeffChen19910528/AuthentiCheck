from chunking.chunker import chunk, chunk_by_sentences, chunk_by_paragraphs, Chunk


SAMPLE = (
    "Deep learning has revolutionized natural language processing. "
    "Transformer architectures enable powerful sequence modeling. "
    "Attention mechanisms allow models to focus on relevant tokens. "
    "Pre-training on large corpora improves downstream task performance. "
    "Fine-tuning adapts these models to specific applications."
)

MULTI_PARA = "First paragraph has more than fifty characters of content here.\n\nSecond paragraph also has sufficient content here.\n\nThird paragraph is the last one and it is long enough."


def test_sentence_chunks_returns_list_of_chunk():
    chunks = chunk_by_sentences(SAMPLE)
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)


def test_chunk_text_is_nonempty():
    chunks = chunk_by_sentences(SAMPLE)
    assert all(len(c.text) > 0 for c in chunks)


def test_chunk_index_increments():
    chunks = chunk_by_sentences(SAMPLE)
    for i, c in enumerate(chunks):
        assert c.chunk_index == i


def test_char_positions_in_range():
    chunks = chunk_by_sentences(SAMPLE)
    for c in chunks:
        assert c.char_start >= 0
        assert c.char_end <= len(SAMPLE)
        assert c.char_start < c.char_end


def test_paragraph_chunking():
    chunks = chunk_by_paragraphs(MULTI_PARA)
    assert len(chunks) == 3


def test_strategy_sentences():
    chunks = chunk(SAMPLE, strategy="sentences")
    assert len(chunks) > 0


def test_strategy_paragraphs():
    chunks = chunk(MULTI_PARA, strategy="paragraphs")
    assert len(chunks) == 3


def test_short_text_still_returns_chunk():
    short = "Just one sentence here."
    chunks = chunk_by_sentences(short)
    assert len(chunks) >= 1
