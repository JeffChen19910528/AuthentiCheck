import textwrap
from dataclasses import dataclass, field
from typing import List

from i18n.translations import t, risk_explanation_key


_RISK_EMOJI = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
_TOP_MATCHES = 10
_LANG_HTML_ATTR = {"en": "en", "zh-TW": "zh-TW", "ja": "ja"}


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
    lang: str = field(default="en")


def _analyze_match(match_pct: float, has_citation: bool, semantic_score: float, lang: str = "en") -> str:
    if has_citation:
        return t(lang, "analysis_cited")
    if semantic_score > 0.65:
        return t(lang, "analysis_rewriting")
    if match_pct > 60:
        return t(lang, "analysis_overlap")
    return t(lang, "analysis_moderate")


def _build_verdict(risk_level: str, overall: float, lang: str = "en") -> str:
    key = f"verdict_{risk_level.lower()}"
    return t(lang, key, pct=overall)


def build_report(
    document_title: str,
    metrics: object,
    similarity_results: List[object],
    citation_adjustments: List[object],
    lang: str = "en",
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
        analysis = _analyze_match(res.combined_score * 100, has_citation, res.semantic_score, lang)

        matches.append(ReportMatch(
            chunk_text=res.chunk_text[:300] + ("..." if len(res.chunk_text) > 300 else ""),
            source_title=res.source_title,
            source_url=res.source_url,
            match_pct=round(res.combined_score * 100, 1),
            has_citation=has_citation,
            analysis=analysis,
        ))

    verdict = _build_verdict(metrics.risk_level, metrics.overall_similarity_pct, lang)
    explanation = t(lang, risk_explanation_key(metrics.risk_level))

    return Report(
        document_title=document_title,
        overall_similarity_pct=metrics.overall_similarity_pct,
        risk_level=metrics.risk_level,
        risk_explanation=explanation,
        high_similarity_ratio=metrics.high_similarity_ratio,
        uncited_similarity_ratio=metrics.uncited_similarity_ratio,
        paraphrase_score=metrics.paraphrase_similarity_score,
        matches=matches,
        final_verdict=verdict,
        lang=lang,
    )


def render_text(report: Report, lang: str = "") -> str:
    _lang = lang or report.lang
    emoji = _RISK_EMOJI.get(report.risk_level, "")
    risk_display = t(_lang, f"risk_level_{report.risk_level.lower()}")

    lines = [
        "=" * 70,
        f"  {t(_lang, 'report_title')}",
        "=" * 70,
        f"  {t(_lang, 'label_document')}: {report.document_title}",
        f"  {t(_lang, 'label_overall_sim')}: {report.overall_similarity_pct:.1f}%",
        f"  {t(_lang, 'label_risk_level')}: {emoji} {risk_display}",
        "-" * 70,
        f"  {t(_lang, 'label_metrics')}",
        f"    {t(_lang, 'label_high_sim_ratio')}: {report.high_similarity_ratio * 100:.1f}%",
        f"    {t(_lang, 'label_uncited_ratio')}: {report.uncited_similarity_ratio * 100:.1f}%",
        f"    {t(_lang, 'label_paraphrase')}: {report.paraphrase_score * 100:.1f}%",
        "-" * 70,
        f"  {t(_lang, 'label_matched_sources')}",
    ]

    for i, m in enumerate(report.matches, 1):
        cited_tag = t(_lang, "tag_cited_bracket") if m.has_citation else t(_lang, "tag_uncited_bracket")
        lines += [
            f"  {i}. {m.source_title} {cited_tag}",
            f"     {t(_lang, 'label_match_pct')}: {m.match_pct:.1f}%  |  {m.source_url}",
            f"     {t(_lang, 'label_excerpt')}: {m.chunk_text[:150]}...",
            f"     {t(_lang, 'label_analysis')}: {m.analysis}",
            "",
        ]

    lines += [
        "-" * 70,
        f"  {t(_lang, 'label_risk_explanation')}",
        textwrap.fill(report.risk_explanation, width=68, initial_indent="  ", subsequent_indent="  "),
        "-" * 70,
        f"  {t(_lang, 'label_final_verdict')}",
        textwrap.fill(report.final_verdict, width=68, initial_indent="  ", subsequent_indent="  "),
        "=" * 70,
    ]
    return "\n".join(lines)


def render_html(report: Report, lang: str = "") -> str:
    _lang = lang or report.lang
    html_lang_attr = _LANG_HTML_ATTR.get(_lang, "en")
    emoji = _RISK_EMOJI.get(report.risk_level, "")
    risk_display = t(_lang, f"risk_level_{report.risk_level.lower()}")

    match_rows = ""
    for i, m in enumerate(report.matches, 1):
        cited = t(_lang, "tag_cited") if m.has_citation else t(_lang, "tag_uncited")
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
<html lang="{html_lang_attr}">
<head>
<meta charset="UTF-8">
<title>AuthentiCheck Report</title>
<style>
  body {{ font-family: 'Noto Sans JP', 'Noto Sans TC', 'Microsoft JhengHei', Meiryo, Arial, sans-serif; margin: 40px; color: #222; }}
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
<h1>{t(_lang, 'report_title')}</h1>
<div class="summary">
  <p><strong>{t(_lang, 'label_document')}:</strong> {report.document_title}</p>
  <p><strong>{t(_lang, 'label_overall_sim')}:</strong> {report.overall_similarity_pct:.1f}%</p>
  <p><strong>{t(_lang, 'label_risk_level')}:</strong> <span class="risk-{report.risk_level}">{emoji} {risk_display}</span></p>
  <p><strong>{t(_lang, 'label_high_sim_ratio')}:</strong> {report.high_similarity_ratio * 100:.1f}%</p>
  <p><strong>{t(_lang, 'label_uncited_ratio')}:</strong> {report.uncited_similarity_ratio * 100:.1f}%</p>
  <p><strong>{t(_lang, 'label_paraphrase')}:</strong> {report.paraphrase_score * 100:.1f}%</p>
</div>
<h2>{t(_lang, 'label_matched_sources')}</h2>
<table>
  <tr>
    <th>{t(_lang, 'label_match_num')}</th>
    <th>{t(_lang, 'label_source')}</th>
    <th>{t(_lang, 'label_match_pct')}</th>
    <th>{t(_lang, 'label_citation')}</th>
    <th>{t(_lang, 'label_analysis')}</th>
  </tr>
  {match_rows}
</table>
<div class="verdict">
  <h3>{t(_lang, 'label_risk_explanation')}</h3>
  <p>{report.risk_explanation}</p>
  <h3>{t(_lang, 'label_final_verdict')}</h3>
  <p>{report.final_verdict}</p>
</div>
</body>
</html>"""
