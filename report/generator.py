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
    chunk_index: int = 0      # paragraph number (1-based for display)
    action: str = ""          # "add_citation" | "rewrite" | "ok"
    semantic_score: float = 0.0


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


def _action_for_match(has_citation: bool, semantic_score: float) -> str:
    if has_citation:
        return "ok"
    if semantic_score > 0.65:
        return "rewrite"
    return "add_citation"


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

        action = _action_for_match(has_citation, res.semantic_score)
        matches.append(ReportMatch(
            chunk_text=res.chunk_text,
            source_title=res.source_title,
            source_url=res.source_url,
            match_pct=round(res.combined_score * 100, 1),
            has_citation=has_citation,
            analysis=analysis,
            chunk_index=res.chunk_index,
            action=action,
            semantic_score=round(res.semantic_score, 4),
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
        location = t(_lang, "label_paragraph", n=m.chunk_index + 1)
        action_text = t(_lang, f"action_{m.action}")
        wrapped_chunk = textwrap.fill(m.chunk_text, width=66, initial_indent="     | ", subsequent_indent="     | ")
        lines += [
            f"  [{i}] {t(_lang, 'label_location')}: {location}  |  {t(_lang, 'label_match_pct')}: {m.match_pct:.1f}%  {cited_tag}",
            f"  {t(_lang, 'label_source')}: {m.source_title}",
            f"  {t(_lang, 'label_url')}: {m.source_url}",
            f"  {t(_lang, 'label_your_text')}:",
            wrapped_chunk,
            f"  {t(_lang, 'label_analysis')}: {m.analysis}",
            f"  *** {t(_lang, 'label_action_required')}: {action_text}",
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


_ACTION_CSS = {
    "add_citation": "action-cite",
    "rewrite": "action-rewrite",
    "ok": "action-ok",
}

_ACTION_ICON = {
    "add_citation": "📌",
    "rewrite": "✏️",
    "ok": "✅",
}


def render_html(report: Report, lang: str = "") -> str:
    _lang = lang or report.lang
    html_lang_attr = _LANG_HTML_ATTR.get(_lang, "en")
    emoji = _RISK_EMOJI.get(report.risk_level, "")
    risk_display = t(_lang, f"risk_level_{report.risk_level.lower()}")

    match_cards = ""
    for i, m in enumerate(report.matches, 1):
        cited_tag = t(_lang, "tag_cited") if m.has_citation else t(_lang, "tag_uncited")
        location = t(_lang, "label_paragraph", n=m.chunk_index + 1)
        action_css = _ACTION_CSS.get(m.action, "action-cite")
        action_icon = _ACTION_ICON.get(m.action, "📌")
        action_text = t(_lang, f"action_{m.action}")
        chunk_html = m.chunk_text.replace("<", "&lt;").replace(">", "&gt;")
        match_cards += f"""
        <div class="match-card {action_css}">
          <div class="match-header">
            <span class="match-num">#{i}</span>
            <span class="match-location">{t(_lang, 'label_location')}: <strong>{location}</strong></span>
            <span class="match-pct">{m.match_pct:.1f}%</span>
            <span class="cite-tag">{cited_tag}</span>
          </div>
          <div class="match-source">
            <strong>{t(_lang, 'label_source')}:</strong>
            <a href="{m.source_url}" target="_blank">{m.source_title}</a>
          </div>
          <div class="match-passage">
            <div class="passage-label">{t(_lang, 'label_your_text')}:</div>
            <blockquote class="passage-text">{chunk_html}</blockquote>
          </div>
          <div class="match-analysis">{m.analysis}</div>
          <div class="action-box">
            {action_icon} <strong>{t(_lang, 'label_action_required')}:</strong> {action_text}
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="{html_lang_attr}">
<head>
<meta charset="UTF-8">
<title>AuthentiCheck Report</title>
<style>
  body {{ font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Noto Sans JP', Meiryo, Arial, sans-serif; margin: 40px; color: #222; max-width: 960px; }}
  h1 {{ color: #1a1a2e; }}
  h2 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 6px; }}
  .summary {{ background: #f4f4f4; padding: 16px; border-radius: 8px; margin-bottom: 24px; }}
  .risk-High {{ color: #c0392b; font-weight: bold; }}
  .risk-Medium {{ color: #e67e22; font-weight: bold; }}
  .risk-Low {{ color: #27ae60; font-weight: bold; }}
  .match-card {{ border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }}
  .match-header {{ display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: #1a1a2e; color: white; flex-wrap: wrap; }}
  .match-num {{ font-weight: bold; font-size: 1.1em; }}
  .match-location {{ flex: 1; }}
  .match-pct {{ font-weight: bold; font-size: 1.05em; }}
  .cite-tag {{ font-size: 0.9em; opacity: 0.9; }}
  .match-source {{ padding: 8px 16px; background: #f0f4ff; font-size: 0.95em; }}
  .match-source a {{ color: #1a1a2e; }}
  .match-passage {{ padding: 10px 16px; }}
  .passage-label {{ font-size: 0.85em; color: #666; margin-bottom: 4px; font-weight: bold; }}
  .passage-text {{ margin: 0; padding: 10px 14px; border-left: 4px solid #aaa; background: #fafafa; font-style: normal; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }}
  .match-analysis {{ padding: 6px 16px; font-size: 0.9em; color: #555; border-top: 1px solid #eee; }}
  .action-box {{ padding: 10px 16px; font-size: 0.95em; border-top: 1px solid #eee; }}
  /* action colour coding */
  .action-cite .match-header {{ background: #c0392b; }}
  .action-cite .passage-text {{ border-color: #c0392b; background: #fff5f5; }}
  .action-cite .action-box {{ background: #fdecea; }}
  .action-rewrite .match-header {{ background: #d35400; }}
  .action-rewrite .passage-text {{ border-color: #e67e22; background: #fff8f0; }}
  .action-rewrite .action-box {{ background: #fef3e2; }}
  .action-ok .match-header {{ background: #27ae60; }}
  .action-ok .passage-text {{ border-color: #27ae60; background: #f0fff4; }}
  .action-ok .action-box {{ background: #e8fae8; }}
  .verdict {{ background: #fff3cd; padding: 16px; border-left: 4px solid #ffc107; margin-top: 24px; border-radius: 4px; }}
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
{match_cards}
<div class="verdict">
  <h3>{t(_lang, 'label_risk_explanation')}</h3>
  <p>{report.risk_explanation}</p>
  <h3>{t(_lang, 'label_final_verdict')}</h3>
  <p>{report.final_verdict}</p>
</div>
</body>
</html>"""
