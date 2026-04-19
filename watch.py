"""
Hot-folder watcher for AuthentiCheck.

Usage:
    python watch.py

Drop any PDF or DOCX into the  input/  folder.
Reports are saved to  output/  and the original file moves to  processed/
"""

import sys
import time
import shutil
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
PROCESSED_DIR = Path("processed")
SUPPORTED = {".pdf", ".docx"}


def _setup_dirs():
    for d in (INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR):
        d.mkdir(exist_ok=True)


def analyze(file_path: Path):
    from ingestion.document_parser import parse
    from preprocessing.text_cleaner import clean
    from chunking.chunker import chunk
    from retrieval.source_retriever import retrieve_sources
    from similarity.engine import compute_similarity
    from citation.citation_checker import adjust_for_citations
    from scoring.scorer import compute_metrics
    from report.generator import build_report, render_html

    print(f"\n{'='*60}")
    print(f"  新檔案偵測到：{file_path.name}")
    print(f"{'='*60}")

    try:
        print("  [1/7] 解析文件...")
        doc = parse(str(file_path))

        print("  [2/7] 前處理文字...")
        cleaned = clean(doc.body)

        print("  [3/7] 切分段落...")
        chunks = chunk(cleaned.cleaned, strategy="sentences")
        print(f"        → {len(chunks)} chunks")

        print("  [4/7] 查詢學術資料庫...")
        sources_per_chunk = []
        for i, c in enumerate(chunks):
            sys.stdout.write(f"\r        chunk {i+1}/{len(chunks)}")
            sys.stdout.flush()
            sources_per_chunk.append(retrieve_sources(c.text, top_n=5))
        print()

        print("  [5/7] 計算相似度...")
        sim_results = compute_similarity(chunks, sources_per_chunk, semantic=True)

        print("  [6/7] 引用意識分析...")
        adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)

        print("  [7/7] 產出報告...")
        metrics = compute_metrics(sim_results, adj)
        report = build_report(doc.title or file_path.stem, metrics, sim_results, adj)

        html_content = render_html(report)
        out_path = OUTPUT_DIR / f"{file_path.stem}_report.html"
        out_path.write_text(html_content, encoding="utf-8")

        dest = PROCESSED_DIR / file_path.name
        shutil.move(str(file_path), str(dest))

        risk_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(report.risk_level, "")
        print(f"\n  完成！")
        print(f"  風險等級  : {risk_icon} {report.risk_level}")
        print(f"  整體相似度: {report.overall_similarity_pct:.1f}%")
        print(f"  報告位置  : {out_path}")
        print(f"  原始檔案  : 已移至 {dest}")

    except Exception as e:
        print(f"\n  [錯誤] 分析失敗：{e}")
        import traceback
        traceback.print_exc()


class _Handler(FileSystemEventHandler):
    def __init__(self):
        self._processing = set()

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED:
            return
        if path in self._processing:
            return
        self._processing.add(path)
        # brief delay to ensure the file is fully written
        time.sleep(1.5)
        if path.exists():
            analyze(path)
        self._processing.discard(path)

    def on_moved(self, event):
        # also handle files moved/copied into the folder
        if event.is_directory:
            return
        path = Path(event.dest_path)
        if path.suffix.lower() not in SUPPORTED:
            return
        if path in self._processing:
            return
        self._processing.add(path)
        time.sleep(1.5)
        if path.exists():
            analyze(path)
        self._processing.discard(path)


def main():
    _setup_dirs()
    print("AuthentiCheck — 熱資料夾監控模式")
    print(f"  監控資料夾 : {INPUT_DIR.resolve()}")
    print(f"  報告輸出   : {OUTPUT_DIR.resolve()}")
    print(f"  已處理檔案 : {PROCESSED_DIR.resolve()}")
    print("\n將 PDF 或 DOCX 檔案丟入 input/ 資料夾，程式將自動分析。")
    print("按 Ctrl+C 停止。\n")

    # process any files already in input/ on startup
    existing = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in SUPPORTED]
    if existing:
        print(f"  偵測到 {len(existing)} 個已存在的檔案，開始處理...\n")
        for f in existing:
            analyze(f)

    handler = _Handler()
    observer = Observer()
    observer.schedule(handler, str(INPUT_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n監控已停止。")
    observer.join()


if __name__ == "__main__":
    main()
