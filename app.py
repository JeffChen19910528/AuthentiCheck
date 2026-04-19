import os
import uuid
import json
import time
import threading
from pathlib import Path
from flask import Flask, request, render_template, send_file, Response, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = Path("uploads")
REPORT_FOLDER = Path("reports")
UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORT_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

jobs = {}  # job_id -> { status, progress, step, ... }


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def run_analysis(job_id, upload_path, filename, fmt, no_semantic, chunk_strategy):
    def update(progress: int, step: str):
        jobs[job_id].update({"progress": progress, "step": step})

    try:
        update(5, "Parsing document…")
        from ingestion.document_parser import parse
        doc = parse(str(upload_path))

        update(15, "Preprocessing text…")
        from preprocessing.text_cleaner import clean
        cleaned = clean(doc.body)

        update(22, "Chunking text…")
        from chunking.chunker import chunk
        chunks = chunk(cleaned.cleaned, strategy=chunk_strategy)

        from retrieval.source_retriever import retrieve_sources
        sources_per_chunk = []
        n = len(chunks)
        for i, c in enumerate(chunks):
            pct = 25 + int(50 * i / max(n, 1))
            update(pct, f"Retrieving sources… ({i + 1}/{n})")
            sources = retrieve_sources(c.text, top_n=5)
            sources_per_chunk.append(sources)

        update(78, "Computing similarity scores…")
        from similarity.engine import compute_similarity
        sim_results = compute_similarity(chunks, sources_per_chunk, semantic=not no_semantic)

        update(88, "Applying citation awareness…")
        from citation.citation_checker import adjust_for_citations
        adj = adjust_for_citations(sim_results, cleaned.cleaned, chunks)

        update(95, "Generating report…")
        from scoring.scorer import compute_metrics
        from report.generator import build_report, render_html, render_text
        metrics = compute_metrics(sim_results, adj)
        report = build_report(doc.title or Path(filename).stem, metrics, sim_results, adj)

        if fmt == "html":
            content = render_html(report)
            ext = ".html"
        else:
            content = render_text(report)
            ext = ".txt"

        report_path = REPORT_FOLDER / f"{job_id}_report{ext}"
        report_path.write_text(content, encoding="utf-8")

        jobs[job_id].update({
            "status": "done",
            "progress": 100,
            "step": "Analysis complete!",
            "fmt": fmt,
            "report_path": str(report_path),
            "html_content": content if fmt == "html" else None,
        })

    except Exception as e:
        jobs[job_id].update({"status": "error", "step": f"Error: {e}", "progress": 0})
    finally:
        if Path(upload_path).exists():
            Path(upload_path).unlink()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("document")
    if not file or not file.filename:
        return jsonify({"error": "Please upload a PDF or DOCX file."}), 400
    if not _allowed(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported."}), 400

    job_id = str(uuid.uuid4())[:8]
    suffix = Path(file.filename).suffix.lower()
    upload_path = UPLOAD_FOLDER / f"{job_id}{suffix}"
    file.save(str(upload_path))

    fmt = request.form.get("format", "html")
    no_semantic = "no_semantic" in request.form
    chunk_strategy = request.form.get("chunk_strategy", "sentences")

    jobs[job_id] = {"status": "running", "progress": 0, "step": "Starting…"}
    threading.Thread(
        target=run_analysis,
        args=(job_id, upload_path, file.filename, fmt, no_semantic, chunk_strategy),
        daemon=True,
    ).start()

    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def progress(job_id):
    def stream():
        while True:
            job = jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'status': 'error', 'step': 'Job not found'})}\n\n"
                break
            yield f"data: {json.dumps(job)}\n\n"
            if job["status"] in ("done", "error"):
                break
            time.sleep(0.4)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/result/<job_id>")
def result(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return "Result not ready.", 404
    if job.get("html_content"):
        return job["html_content"], 200, {"Content-Type": "text/html; charset=utf-8"}
    return send_file(
        job["report_path"], mimetype="text/plain", as_attachment=True,
        download_name=f"report_{job_id}.txt",
    )


if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, use_reloader=False, port=5000)
