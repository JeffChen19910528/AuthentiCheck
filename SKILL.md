You are a senior software engineer specializing in NLP, information retrieval, and academic plagiarism detection systems.

Your task is to build a **Turnitin-like plagiarism detection system** that analyzes uploaded academic documents and produces a professional similarity and plagiarism risk report.

---

# 🎯 Core Objective

Build a system that:

* Calculates similarity score
* Detects paraphrased plagiarism
* Identifies citation misuse
* Provides human-readable plagiarism risk analysis
* Supports multilingual UI and report output (English, Traditional Chinese, Japanese)

---

# 🧠 Key Design Principles

DO NOT treat plagiarism as a simple percentage.

Instead, implement:

1. Similarity Detection
2. Contextual Analysis
3. Citation Awareness
4. Risk Classification
5. Multilingual Output

---

# 🧩 System Modules

## 1. Document Ingestion

* Input: PDF, DOCX
* Extract structured text:

  * Title
  * Abstract
  * Body
  * References (separate this!)
* Libraries:

  * PyMuPDF
  * python-docx

---

## 2. Smart Preprocessing

* Remove:

  * References section
  * Bibliography
* Normalize:

  * Lowercase
  * Remove stopwords (optional)
* Detect citation patterns:

  * (Author, Year)
  * [1], [2]

---

## 3. Chunking Strategy

* Split text into:

  * Sentences + paragraphs
* Keep semantic coherence
* Each chunk must be traceable to original location

---

## 4. Source Retrieval (Critical)

### Sources:

* Semantic Scholar API
* arXiv API
* CrossRef API

### Process:

* Extract keywords (KeyBERT)
* Query top 5 related papers per chunk
* Retrieve abstracts or snippets

---

## 5. Dual Similarity Engine

### (A) Lexical Similarity

* TF-IDF + cosine similarity
* N-gram overlap (3-gram or 5-gram)

### (B) Semantic Similarity

* Sentence embeddings:

  * SentenceTransformers (all-MiniLM-L6-v2)
* Detect paraphrased plagiarism

---

## 6. Citation Awareness Engine

If:

* High similarity AND proper citation exists → reduce risk

If:

* High similarity WITHOUT citation → increase risk

---

## 7. Scoring Model

Instead of a single score, compute:

### 📊 Metrics

* Overall Similarity %
* High Similarity Ratio
* Uncited Similarity Ratio
* Paraphrase Similarity Score

---

## 8. Risk Classification

Define:

* 🟢 Low Risk:

  * Mostly cited or common knowledge

* 🟡 Medium Risk:

  * Some uncited similarity

* 🔴 High Risk:

  * Large uncited + paraphrased similarity

---

## 9. Report Generator (IMPORTANT)

Generate a Turnitin-style report in the user's selected language:

### 1. Overall Similarity

* e.g. 27%

### 2. Matched Sources — Per-Paragraph Detail

Each match card shows:

* **Location**: which paragraph in the uploaded paper (Paragraph #N)
* **Source**: title, URL, match percentage, citation status
* **Problematic Passage**: the full text of the suspicious paragraph from the paper
* **Analysis**: interpretation (cited / common phrasing / overlap / rewriting)
* **Action Required** (colour-coded):
  * 📌 Red — Add citation (high lexical match, no citation)
  * ✏️ Orange — Rewrite recommended (high semantic similarity, no citation)
  * ✅ Green — Properly cited, no action needed

### 3. Final Verdict

DO NOT say "plagiarized"
Instead say:

* "High likelihood of plagiarism risk"
* "Moderate similarity with acceptable citation usage"

All labels, analysis strings, and verdict text must use the language selected by the user.

### Action Logic

```
has_citation=True  → action = "ok"
semantic > 0.65 and no citation → action = "rewrite"
otherwise no citation → action = "add_citation"
```

---

## 10. Internationalization (i18n)

All user-facing strings are centralized in `i18n/translations.py`.

### Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `zh-TW` | 繁體中文 (Traditional Chinese) |
| `ja` | 日本語 (Japanese) |

### Translation Coverage

* Web UI labels, buttons, options, and error messages
* Server-side progress step messages (streamed via SSE)
* Report section headings and metric labels
* Per-match analysis strings (cited / rewriting / overlap / moderate)
* Risk level display values
* Final verdict and risk explanation paragraphs
* Citation tags (cited / uncited)

### Helper Function

```python
from i18n.translations import t

# Basic usage
t("zh-TW", "btn_analyze")           # → "分析文件"

# With format placeholders
t("ja", "step_retrieve_n", i=3, n=10)  # → "ソースを検索中… (3/10)"
t("en", "verdict_high", pct=55.0)      # → "Final Assessment: High likelihood..."
```

### Adding a New Language

1. Add a new entry to `TRANSLATIONS` in `i18n/translations.py` with all keys present in `"en"`
2. Add the language option to the `<select id="lang-select">` in `templates/index.html`
3. Add the corresponding JS translation object to the `T` constant in `index.html`
4. Add the `html lang` attribute mapping to `_LANG_HTML_ATTR` in `report/generator.py`

### How Language Flows Through the System

```
User selects language in browser
        ↓
Hidden <input name="lang"> submitted with form
        ↓
POST /analyze — Flask reads lang, validates against SUPPORTED_LANGS
        ↓
run_analysis(lang=...) — progress step strings use t(lang, ...)
        ↓
build_report(..., lang=lang) — analysis, verdict, explanation translated
        ↓
render_html(report) / render_text(report) — all labels translated
        ↓
HTML report has correct lang attribute + CJK font stack
```

Language preference is persisted in browser `localStorage` and restored on next visit.

---

## 🖥️ UI Design

### Web Interface (Flask — primary)

* One-click launcher (`start.py` / `start.bat` / `start.sh`)

  * Kills any existing instance on port 5000 before starting
  * Auto-opens browser after server is ready
  * Works on Windows, macOS, Linux
* Language selector at the top of the upload card (English / 繁體中文 / 日本語)

  * Instant client-side text swap via JavaScript
  * Selection persisted in `localStorage`
  * Selected language sent to server with each analysis request
* Upload PDF or DOCX via browser
* Real-time progress bar (SSE streaming)

  * 7-step indicator: Parsing → Preprocessing → Chunking → Retrieving → Similarity → Citation → Report
  * Per-step status: pending / active (blue) / done (green)
  * Live step description in selected language (e.g. "正在檢索來源…（3/12）")
* Analysis runs in background thread — UI stays responsive
* HTML report displayed in browser; plain-text report downloaded

### CLI (secondary)

* Auto-detects file from `input/` when no argument given
* If multiple files exist, shows numbered selection menu

---

## ⚠️ Constraints

* Never claim legal plagiarism detection
* Avoid false positives:

  * Ignore standard academic phrases
* Clearly explain uncertainty
* i18n: never hardcode user-facing strings outside `i18n/translations.py` (web + report layer)

---

## 🚀 Bonus (Advanced Features)

* Build local database:

  * Store previously checked documents
* Cross-document comparison (like Turnitin)
* Section-based analysis (Method vs Introduction)
* Add more languages by extending `TRANSLATIONS` in `i18n/translations.py`

---

## 📦 Deliverables

* Modular Python project
* CLI + optional UI
* Multilingual report output (HTML + plain text)
* Sample report output
* Documentation

---

Think like a real-world plagiarism detection system designer.
Focus on accuracy, explainability, usability, and internationalization.
