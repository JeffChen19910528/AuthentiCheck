import argparse
import sys
from pathlib import Path


def run(input_path: str, output: str, fmt: str, no_semantic: bool, chunk_strategy: str):
    from ingestion.document_parser import parse
    from preprocessing.text_cleaner import clean
    from chunking.chunker import chunk
    from retrieval.source_retriever import retrieve_sources
    from similarity.engine import compute_similarity
    from citation.citation_checker import adjust_for_citations
    from scoring.scorer import compute_metrics
    from report.generator import build_report, render_text, render_html

    print(f"[1/7] Parsing document: {input_path}")
    doc = parse(input_path)

    print("[2/7] Preprocessing text...")
    cleaned = clean(doc.body)

    print(f"[3/7] Chunking ({chunk_strategy})...")
    chunks = chunk(cleaned.cleaned, strategy=chunk_strategy)
    print(f"      → {len(chunks)} chunks")

    print("[4/7] Retrieving candidate sources (API queries)...")
    sources_per_chunk = []
    for i, c in enumerate(chunks):
        sys.stdout.write(f"\r      chunk {i+1}/{len(chunks)}")
        sys.stdout.flush()
        sources = retrieve_sources(c.text, top_n=5)
        sources_per_chunk.append(sources)
    print()

    print("[5/7] Computing similarity scores...")
    sim_results = compute_similarity(chunks, sources_per_chunk, semantic=not no_semantic)

    print("[6/7] Applying citation awareness...")
    adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)

    print("[7/7] Scoring and generating report...")
    metrics = compute_metrics(sim_results, adj)
    report = build_report(doc.title or Path(input_path).stem, metrics, sim_results, adj)

    if fmt == "html":
        content = render_html(report)
        ext = ".html"
    else:
        content = render_text(report)
        ext = ".txt"

    if output:
        out_path = output
    else:
        out_path = str(Path(input_path).stem) + "_report" + ext

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    if fmt == "text":
        print("\n" + content)

    print(f"\nReport saved → {out_path}")


def auto_detect_input() -> str:
    input_dir = Path("input")
    if not input_dir.exists():
        return ""
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in {".pdf", ".docx"}]
    if not files:
        return ""
    if len(files) == 1:
        print(f"Auto-detected: {files[0]}")
        return str(files[0])
    print("Multiple files found in input/:")
    for i, f in enumerate(files, 1):
        print(f"  [{i}] {f.name}")
    while True:
        choice = input("Select file number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return str(files[int(choice) - 1])


def main():
    parser = argparse.ArgumentParser(
        description="AuthentiCheck — Academic plagiarism risk detector"
    )
    parser.add_argument("input", nargs="?", default="",
                        help="Path to PDF or DOCX file (auto-detects from input/ if omitted)")
    parser.add_argument("-o", "--output", default="", help="Output file path")
    parser.add_argument(
        "--format", choices=["text", "html"], default="text", dest="fmt",
        help="Report output format (default: text)"
    )
    parser.add_argument(
        "--no-semantic", action="store_true",
        help="Skip semantic (SentenceTransformer) similarity — faster but less accurate"
    )
    parser.add_argument(
        "--chunk", choices=["sentences", "paragraphs"], default="sentences",
        dest="chunk_strategy", help="Chunking strategy (default: sentences)"
    )
    args = parser.parse_args()

    input_path = args.input or auto_detect_input()
    if not input_path:
        print("Error: no input file specified and none found in input/", file=sys.stderr)
        sys.exit(1)
    if not Path(input_path).exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    run(input_path, args.output, args.fmt, args.no_semantic, args.chunk_strategy)


if __name__ == "__main__":
    main()
