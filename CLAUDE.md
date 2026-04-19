# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AuthentiCheck** is a Turnitin-style academic plagiarism detection system built in Python. It analyzes uploaded documents (PDF, DOCX) and produces a professional similarity and plagiarism risk report — not just a percentage, but a multi-dimensional risk assessment with citation awareness.

## Planned Commands

Once the project is scaffolded, expected commands will follow this pattern:

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI analysis
python main.py --input paper.pdf

# Launch desktop/web UI
python app.py

# Run tests
pytest tests/
pytest tests/test_similarity.py  # single module
```

## Architecture

The system is composed of these sequential pipeline modules (see `SKILL.md` for full spec):

### Pipeline Modules

1. **Document Ingestion** (`ingestion/`) — Parses PDF (PyMuPDF) and DOCX (python-docx) into structured sections: title, abstract, body, references.

2. **Smart Preprocessing** (`preprocessing/`) — Strips the references section before analysis, normalizes text, and detects citation patterns (`(Author, Year)` or `[1]` style).

3. **Chunking** (`chunking/`) — Splits body text into sentence/paragraph chunks while preserving traceability to original document location.

4. **Source Retrieval** (`retrieval/`) — Uses KeyBERT to extract keywords per chunk, then queries Semantic Scholar, arXiv, and CrossRef APIs (top 5 papers per chunk) to retrieve candidate matching sources.

5. **Dual Similarity Engine** (`similarity/`)
   - **Lexical**: TF-IDF cosine similarity + N-gram overlap (3-gram or 5-gram)
   - **Semantic**: SentenceTransformers (`all-MiniLM-L6-v2`) for paraphrase detection

6. **Citation Awareness Engine** (`citation/`) — Modifies risk score: high similarity + proper citation → lower risk; high similarity without citation → higher risk.

7. **Scoring Model** (`scoring/`) — Produces four metrics: Overall Similarity %, High Similarity Ratio, Uncited Similarity Ratio, Paraphrase Similarity Score.

8. **Risk Classifier** (`scoring/`) — Maps metrics to: Low / Medium / High risk with explanation.

9. **Report Generator** (`report/`) — Outputs a structured report with: overall similarity, matched sources (title + URL + match %), highlighted overlapping text, per-match analysis (citation vs. paraphrase vs. common phrasing), and a final verdict using hedged language ("High likelihood of plagiarism risk", never "plagiarized").

### UI Layer

- Primary: Desktop GUI (tkinter or PyQt)
- Optional: Web interface via Flask or FastAPI

### Key Design Constraint

The analysis pipeline **must exclude the References/Bibliography section** from similarity scoring — only the body text is analyzed. Citations found in the body are used to contextualize (not penalize) similarity.

## External APIs

| API | Purpose |
|-----|---------|
| Semantic Scholar | Retrieve related paper abstracts |
| arXiv | Open-access paper retrieval |
| CrossRef | DOI/metadata lookup |

## Core Dependencies

| Library | Role |
|---------|------|
| PyMuPDF (`fitz`) | PDF text extraction |
| python-docx | DOCX parsing |
| KeyBERT | Keyword extraction for source queries |
| sentence-transformers | Semantic embeddings (`all-MiniLM-L6-v2`) |
| scikit-learn | TF-IDF + cosine similarity |
| nltk / spacy | Sentence tokenization, stopword removal |
