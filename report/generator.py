import textwrap
from dataclasses import dataclass
from typing import List, Optional


_RISK_EMOJI = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
_TOP_MATCHES = 10


@dataclass
class ReportMatch:
    chunk_text: str
    source_title: str
    source_url: str
    match_pct: float
    has_citation: bool
    analysis: str


@dataclass
class Report:
    document_title: str
    overall_similarity_pct: float
    risk_level: str
    risk_explanation: str
    high_similarity_ratio: float
    uncited_similarity_ratio: float
    paraphrase_score: float
    matches: List[ReportMatch]
    final_verdict: str


def _analyze_match(match_pct: float, has_citation: bool, semantic_score: float) -> str:
    if has_citation:
        return "Properly cited reference — similarity is expected and acceptable."
    if semantic_score > 0.65:
        return "Suspicious rewriting detected — the passage is semantically close to the source without a citation."
    if match_pct > 60:
        return "High textual overlap without citation — possible direct copying or close paraphrase."
    return "Moderate similarity; may reflect common academic phrasing or shared methodology."


def _build_verdict(risk_level: str, overall: float) -> str:
    if risk_level == "High":
        return (
            f"Final Assessment: High likelihood of plagiarism risk "
            f"(overall similarity {overall:.1f}%). "
            "A substantial portion of the submitted text closely matches external sources "
            "without proper attribution. Independent review is strongly recommended."
        )
    elif risk_level == "Medium":
        return (
            f"Final Assessment: Moderate similarity with partially acceptable citation usage "
            f"(overall similarity {overall:.1f}%). "
            "Some passages require clearer attribution or rephrasing."
        )
    else:
        return (
            f"Final Assessment: Low similarity risk detected "
            f"(overall similarity {overall:.1f}%). "
            "The document appears to be largely original with appropriate citation practices."
        )


def build_report(
    document_title: str,
    metrics: object,
    similarity_results: List[object],
    citation_adjustments: List[object],
) -> Report:
    adj_map = {a.chunk_index: a for a in citation_adjustments}

    seen_sources = set()
    matches: List[ReportMatch] = []

    for res in similarity_results[:_TOP_MATCHES]:
        key = res.source_title.lower().strip()
        if key in seen_sources:
            continue
        seen_sources.add(key)

        adj = adj_map.get(res.chunk_index)
        has_citation = adj.has_citation if adj else False
        analysis = _analyze_match(res.combined_score * 100, has_citation, res.semantic_score)

        matches.append(ReportMatch(
            chunk_text=res.chunk_text[:300] + ("..." if len(res.chunk_text) > 300 else ""),
            source_title=res.source_title,
            source_url=res.source_url,
            match_pct=round(res.combined_score * 100, 1),
            has_citation=has_citation,
            analysis=analysis,
        ))

    verdict = _build_verdict(metrics.risk_level, metrics.overall_similarity_pct)

    return Report(
        document_title=document_title,
        overall_similarity_pct=metrics.overall_similarity_pct,
        risk_level=metrics.risk_level,
        risk_explanation=metrics.risk_explanation,
        high_similarity_ratio=metrics.high_similarity_ratio,
        uncited_similarity_ratio=metrics.uncited_similarity_ratio,
        paraphrase_score=metrics.paraphrase_similarity_score,
        matches=matches,
        final_verdict=verdict,
    )


def render_text(report: Report) -> str:
    emoji = _RISK_EMOJI.get(report.risk_level, "")
    lines = [
        "=" * 70,
        "  AuthentiCheck — Plagiarism Risk Report",
        "=" * 70,
        f"  Document : {report.document_title}",
        f"  Overall Similarity : {report.overall_similarity_pct:.1f}%",
        f"  Risk Level         : {emoji} {report.risk_level}",
        "-" * 70,
        "  METRICS",
        f"    High Similarity Ratio   : {report.high_similarity_ratio * 100:.1f}%",
        f"    Uncited Similarity Ratio: {report.uncited_similarity_ratio * 100:.1f}%",
        f"    Paraphrase Score        : {report.paraphrase_score * 100:.1f}%",
        "-" * 70,
        "  MATCHED SOURCES",
    ]

    for i, m in enumerate(report.matches, 1):
        cited_tag = "[cited]" if m.has_citation else "[uncited]"
        lines += [
            f"  {i}. {m.source_title} {cited_tag}",
            f"     Match: {m.match_pct:.1f}%  |  {m.source_url}",
            f"     Excerpt: {m.chunk_text[:150]}...",
            f"     Analysis: {m.analysis}",
            "",
        ]

    lines += [
        "-" * 70,
        "  RISK EXPLANATION",
        textwrap.fill(report.risk_explanation, width=68, initial_indent="  ", subsequent_indent="  "),
        "-" * 70,
        "  FINAL VERDICT",
        textwrap.fill(report.final_verdict, width=68, initial_indent="  ", subsequent_indent="  "),
        "=" * 70,
    ]
    return "\n".join(lines)


def render_html(report: Report) -> str:
    emoji = _RISK_EMOJI.get(report.risk_level, "")
    match_rows = ""
    for i, m in enumerate(report.matches, 1):
        cited = "✅ Cited" if m.has_citation else "⚠️ Uncited"
        match_rows += f"""
        <tr>
          <td>{i}</td>
          <td><a href="{m.source_url}" target="_blank">{m.source_title}</a></td>
          <td>{m.match_pct:.1f}%</td>
          <td>{cited}</td>
          <td>{m.analysis}</td>
        </tr>
        <tr><td colspan="5" class="excerpt"><em>{m.chunk_text[:200]}...</em></td></tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AuthentiCheck Report</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
  h1 {{ color: #1a1a2e; }}
  .summary {{ background: #f4f4f4; padding: 16px; border-radius: 8px; margin-bottom: 24px; }}
  .risk-High {{ color: #c0392b; font-weight: bold; }}
  .risk-Medium {{ color: #e67e22; font-weight: bold; }}
  .risk-Low {{ color: #27ae60; font-weight: bold; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
  th {{ background: #1a1a2e; color: white; }}
  .excerpt {{ font-size: 0.85em; background: #fafafa; color: #555; }}
  .verdict {{ background: #fff3cd; padding: 16px; border-left: 4px solid #ffc107; margin-top: 24px; }}
</style>
</head>
<body>
<h1>AuthentiCheck — Plagiarism Risk Report</h1>
<div class="summary">
  <p><strong>Document:</strong> {report.document_title}</p>
  <p><strong>Overall Similarity:</strong> {report.overall_similarity_pct:.1f}%</p>
  <p><strong>Risk Level:</strong> <span class="risk-{report.risk_level}">{emoji} {report.risk_level}</span></p>
  <p><strong>High Similarity Ratio:</strong> {report.high_similarity_ratio * 100:.1f}%</p>
  <p><strong>Uncited Similarity Ratio:</strong> {report.uncited_similarity_ratio * 100:.1f}%</p>
  <p><strong>Paraphrase Score:</strong> {report.paraphrase_score * 100:.1f}%</p>
</div>
<h2>Matched Sources</h2>
<table>
  <tr><th>#</th><th>Source</th><th>Match %</th><th>Citation</th><th>Analysis</th></tr>
  {match_rows}
</table>
<div class="verdict">
  <h3>Risk Explanation</h3>
  <p>{report.risk_explanation}</p>
  <h3>Final Verdict</h3>
  <p>{report.final_verdict}</p>
</div>
</body>
</html>"""
