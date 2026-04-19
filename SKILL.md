You are a senior software engineer specializing in NLP, information retrieval, and academic plagiarism detection systems.

Your task is to build a **Turnitin-like plagiarism detection system** that analyzes uploaded academic documents and produces a professional similarity and plagiarism risk report.

---

# 🎯 Core Objective

Build a system that:

* Calculates similarity score
* Detects paraphrased plagiarism
* Identifies citation misuse
* Provides human-readable plagiarism risk analysis

---

# 🧠 Key Design Principle

DO NOT treat plagiarism as a simple percentage.

Instead, implement:

1. Similarity Detection
2. Contextual Analysis
3. Citation Awareness
4. Risk Classification

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

Generate a Turnitin-style report:

### 1. Overall Similarity

* e.g. 27%

### 2. Matched Sources

* Source title
* URL
* Match percentage

### 3. Highlighted Text

* Show:

  * Original text
  * Matched text
  * Highlight overlaps

### 4. Analysis

Explain:

* Is this:

  * Proper citation?
  * Common method reuse?
  * Suspicious rewriting?

### 5. Final Verdict

DO NOT say "plagiarized"
Instead say:

* "High likelihood of plagiarism risk"
* "Moderate similarity with acceptable citation usage"

---

## 🖥️ UI Design

### Web Interface (Flask — primary)

* One-click launcher (`start.py` / `start.bat` / `start.sh`)

  * Kills any existing instance on port 5000 before starting
  * Auto-opens browser after server is ready
  * Works on Windows, macOS, Linux
* Upload PDF or DOCX via browser
* Real-time progress bar (SSE streaming)

  * 7-step indicator: Parsing → Preprocessing → Chunking → Retrieving → Similarity → Citation → Report
  * Per-step status: pending / active (blue) / done (green)
  * Live step description (e.g. "Retrieving sources… (3/12)")
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

---

## 🚀 Bonus (Advanced Features)

* Build local database:

  * Store previously checked documents
* Cross-document comparison (like Turnitin)
* Multi-language detection (EN + ZH)
* Section-based analysis (Method vs Introduction)

---

## 📦 Deliverables

* Modular Python project
* CLI + optional UI
* Sample report output
* Documentation

---

Think like a real-world plagiarism detection system designer.
Focus on accuracy, explainability, and usability.
