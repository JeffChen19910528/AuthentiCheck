# AuthentiCheck

AuthentiCheck 是一套仿 Turnitin 的學術論文抄襲風險偵測系統，以 Python 撰寫。它不只輸出一個百分比，而是透過多維度分析（語意相似、引用意識、詞彙重疊）產出一份完整的相似性風險報告，並支援**多語系介面與報告輸出**。

---

## 功能特色

- **雙重相似度引擎**：TF-IDF + N-gram（詞彙）× SentenceTransformers（語意，可偵測換句話說的抄襲）
- **引用意識**：偵測到附近有引用標記時自動降低風險評分
- **多來源查詢**：同時查詢 Semantic Scholar、arXiv、CrossRef 三大學術資料庫
- **四項評估指標**：整體相似度、高相似段落比例、未引用相似比例、改寫相似分數
- **三級風險分類**：🟢 低風險 / 🟡 中風險 / 🔴 高風險
- **多格式輸出**：純文字報告 或 HTML 互動報告
- **多語系支援**：介面與報告同步支援 English、繁體中文、日本語
- **熱資料夾模式**：將檔案丟入 `input/` 資料夾，程式自動偵測並分析，報告輸出至 `output/`
- **兩種進階介面**：CLI 命令列 + Flask 網頁介面

---

## 系統需求

- Python 3.10+
- 網路連線（API 查詢用）

---

## 安裝

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# 首次執行需下載 NLTK 資料
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

---

## 使用方式

### 熱資料夾模式（最直覺）

```bash
python watch.py
```

啟動後直接把 PDF 或 DOCX **丟入 `input/` 資料夾**，程式會：

1. 自動偵測新檔案
2. 執行完整分析流程
3. 將 HTML 報告存到 `output/`
4. 原始檔案移至 `processed/`

```
input/      ← 把論文丟這裡
output/     ← 報告自動產生在這裡
processed/  ← 已分析的原始檔案
```

啟動時 `input/` 內已有的檔案也會一併處理。按 `Ctrl+C` 停止監控。

---

### CLI 命令列

```bash
# 自動偵測 input/ 資料夾中的檔案（不需要指定檔名）
python main.py

# 指定檔案路徑
python main.py paper.pdf

# 指定輸出 HTML 報告
python main.py paper.pdf --format html -o report.html

# 分析 DOCX，使用段落切分（較快）
python main.py thesis.docx --chunk paragraphs

# 跳過語意分析（速度更快，精度略降）
python main.py paper.pdf --no-semantic

# 查看所有選項
python main.py --help
```

> `input/` 內只有一個檔案時自動執行；有多個檔案時會列出選單讓你選擇。

**CLI 參數說明：**

| 參數 | 說明 |
|------|------|
| `input` | 輸入檔案路徑（PDF 或 DOCX），省略時自動偵測 `input/` |
| `-o / --output` | 指定輸出報告路徑 |
| `--format` | 輸出格式：`text`（預設）或 `html` |
| `--no-semantic` | 跳過 SentenceTransformer 語意分析，加快速度 |
| `--chunk` | 切分策略：`sentences`（預設）或 `paragraphs` |

---

### 一鍵啟動網頁介面（推薦）

| 系統 | 操作 |
|------|------|
| **Windows** | 雙擊 `start.bat`，或執行 `python start.py` |
| **macOS / Linux** | `chmod +x start.sh && ./start.sh`，或 `python3 start.py` |

- 自動終止已佔用 port 5000 的舊實例，避免重複執行
- 伺服器就緒後自動開啟瀏覽器
- `Ctrl+C` 停止伺服器

上傳檔案後，網頁會顯示**即時進度條**：

```
[Parsing] → [Preprocessing] → [Chunking] → [Retrieving] → [Similarity] → [Citation] → [Report]
```

每個步驟有獨立狀態指示（灰 → 藍進行中 → 綠完成），分析完成後自動跳轉至報告頁面。

### Flask 網頁介面（手動）

```bash
python app.py
```

開啟瀏覽器前往 `http://localhost:5000`，上傳檔案後即可透過網頁查看互動式 HTML 報告。

---

## 多語系支援

網頁介面左上方提供語言選擇器，可即時切換介面語言，無需重新整理頁面：

| 語言選項 | 介面 | 報告 |
|----------|------|------|
| English | ✅ | ✅ |
| 繁體中文 | ✅ | ✅ |
| 日本語 | ✅ | ✅ |

**切換效果：**
- 所有 UI 文字（標籤、按鈕、進度步驟、錯誤訊息）即時更新
- 伺服器端進度訊息（Parsing / Chunking / …）以選定語言串流顯示
- 輸出的 HTML / 純文字報告完整翻譯，包含風險等級、引用標籤、比對分析與最終結論
- HTML 報告自動設定正確的 `lang` 屬性（`en` / `zh-TW` / `ja`）與 CJK 字型
- 語言偏好儲存於瀏覽器 `localStorage`，下次開啟自動套用

翻譯模組位於 `i18n/translations.py`，所有字串集中管理，方便日後擴充新語言。

---

## 報告內容

報告包含以下五個區塊：

1. **整體相似度** — 整體相似度百分比（已考慮引用調整）
2. **匹配來源（逐段對照）** — 每筆比對明確指出：
   - **位置**：您論文的第幾段（Paragraph #N）
   - **有問題的完整段落**：完整顯示您論文中有疑慮的原文
   - **比對來源**：相似文獻的標題 + URL + 比對百分比 + 是否已引用
3. **逐筆分析** — 每筆比對的說明（正常引用 / 方法共用 / 疑似改寫）
4. **建議動作**（每段都有，用顏色區分）：
   - 📌 **紅色**：請補充參考文獻（高相似但未引用）
   - ✏️ **橘色**：建議修改或改寫（語意相似度高，疑似換句話說）
   - ✅ **綠色**：已正確引用，無需修改
5. **最終結論** — 最終風險聲明（使用緩和語氣，不直接判定抄襲）

HTML 報告中，每張比對卡片以不同顏色背景標示風險程度，讓使用者快速定位需要修改的段落。

---

## 專案架構

```
AuthentiCheck/
├── start.py                       # 跨平台一鍵啟動腳本（殺舊實例 + 開瀏覽器）
├── start.bat                      # Windows 雙擊捷徑
├── start.sh                       # macOS / Linux 捷徑
├── watch.py                       # 熱資料夾監控（自動批次處理）
├── main.py                        # CLI 入口（支援自動偵測 input/）
├── app.py                         # Flask 網頁介面
├── requirements.txt
├── i18n/
│   ├── __init__.py
│   └── translations.py            # 多語系字串（en / zh-TW / ja）與 t() 輔助函式
├── input/                         # 將論文丟入此處
├── output/                        # HTML 報告自動存放於此
├── processed/                     # 已分析的原始檔案
├── ingestion/
│   └── document_parser.py         # PDF / DOCX 解析，抽取標題、摘要、本文、參考文獻
├── preprocessing/
│   └── text_cleaner.py            # 移除參考文獻節、正規化文字、偵測引用標記
├── chunking/
│   └── chunker.py                 # 將本文切成可追溯位置的句子/段落 chunks
├── retrieval/
│   └── source_retriever.py        # KeyBERT 抽關鍵字 → 查詢三大 API 取得候選來源
├── similarity/
│   └── engine.py                  # TF-IDF cosine + N-gram + SentenceTransformer 相似度
├── citation/
│   └── citation_checker.py        # 根據引用標記存在與否調整風險分數
├── scoring/
│   └── scorer.py                  # 計算四項指標 + 低/中/高風險分類
├── report/
│   └── generator.py               # 產出純文字或 HTML 格式報告（支援多語系）
├── templates/
│   └── index.html                 # Flask 上傳頁面（含語言選擇器）
├── tests/
│   ├── test_ingestion.py          # 文件解析單元測試（含 PDF/DOCX mock）
│   ├── test_preprocessing.py      # 正規化、引用偵測測試
│   ├── test_chunking.py           # 句子/段落切分測試
│   ├── test_retrieval.py          # API 查詢 mock 測試
│   ├── test_similarity.py         # N-gram + TF-IDF 相似度測試
│   ├── test_citation.py           # 引用意識風險調整測試
│   ├── test_scoring.py            # 評分與風險分類測試
│   ├── test_report.py             # 報告產生測試
│   ├── test_i18n.py               # 多語系翻譯與報告輸出測試
│   └── test_integration.py        # 完整流程整合測試
└── run_tests.py                   # 一鍵執行所有測試
```

---

## 重要設計原則

- **參考文獻節不計入分析**：系統會在分析前自動移除 References / Bibliography 節，避免誤判。
- **引用意識**：高相似段落若鄰近有引用標記（APA 或數字格式），風險分數會自動下調。
- **不直接判定「抄襲」**：報告採用緩和語氣，例如「高度剽竊風險」，而非直接判定。
- **多語系一致性**：UI 語言與報告輸出語言同步，所有文字均集中於 `i18n/translations.py` 管理。

---

## 測試

```bash
# 執行全部測試（不需要安裝任何 GPU 或下載模型）
python run_tests.py

# 或直接用 pytest
python -m pytest tests/ -v

# 只跑多語系測試
python -m pytest tests/test_i18n.py -v

# 只跑某個模組的測試
python -m pytest tests/test_similarity.py -v
```

所有外部依賴（PyMuPDF、SentenceTransformer、API）皆已 mock，測試可在離線環境中完整執行。

---

## 注意事項

- 本工具僅供**學術輔助參考**，不構成法律意義上的抄襲認定。
- API 查詢受限於各平台速率限制，文件越長分析時間越久。
- 語意分析首次執行會自動下載約 90MB 的 `all-MiniLM-L6-v2` 模型。
