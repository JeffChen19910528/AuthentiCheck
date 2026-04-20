"""Tests for the i18n translation system and multilingual report generation."""
import pytest
from i18n.translations import t, risk_explanation_key, SUPPORTED_LANGS, TRANSLATIONS
from report.generator import build_report, render_text, render_html, Report
from similarity.engine import SimilarityResult
from citation.citation_checker import CitationAdjustment
from scoring.scorer import ScoreMetrics


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _metrics(risk="Medium", overall=30.0):
    return ScoreMetrics(
        overall_similarity_pct=overall,
        high_similarity_ratio=0.3,
        uncited_similarity_ratio=0.4,
        paraphrase_similarity_score=0.35,
        risk_level=risk,
        risk_explanation="Test explanation.",
    )


def _sim(idx, score=0.6, semantic=0.4):
    return SimilarityResult(
        chunk_text=f"This is chunk number {idx} with some academic content.",
        source_title=f"Paper Title {idx}",
        source_url=f"https://example.com/{idx}",
        source_abstract="Abstract text here.",
        lexical_score=score,
        ngram_score=score,
        semantic_score=semantic,
        combined_score=score,
        chunk_index=idx,
    )


def _adj(idx, cited=False):
    return CitationAdjustment(
        chunk_index=idx,
        has_citation=cited,
        risk_modifier=0.0,
        reason="test",
    )


# ---------------------------------------------------------------------------
# Translation module tests
# ---------------------------------------------------------------------------

class TestTranslations:
    def test_supported_langs_includes_all_three(self):
        assert "en" in SUPPORTED_LANGS
        assert "zh-TW" in SUPPORTED_LANGS
        assert "ja" in SUPPORTED_LANGS

    def test_t_returns_english_string(self):
        result = t("en", "btn_analyze")
        assert result == "Analyze Document"

    def test_t_returns_chinese_string(self):
        result = t("zh-TW", "btn_analyze")
        assert result != "Analyze Document"
        assert len(result) > 0

    def test_t_returns_japanese_string(self):
        result = t("ja", "btn_analyze")
        assert result != "Analyze Document"
        assert len(result) > 0

    def test_t_falls_back_to_english_for_unknown_lang(self):
        result = t("xx", "btn_analyze")
        assert result == t("en", "btn_analyze")

    def test_t_returns_key_if_missing_from_all_langs(self):
        result = t("en", "nonexistent_key_xyz")
        assert result == "nonexistent_key_xyz"

    def test_t_formats_placeholders(self):
        result = t("en", "step_retrieve_n", i=3, n=10)
        assert "3" in result
        assert "10" in result

    def test_t_formats_verdict_pct(self):
        result = t("en", "verdict_high", pct=55.0)
        assert "55.0" in result

    def test_all_langs_have_same_keys(self):
        en_keys = set(TRANSLATIONS["en"].keys())
        for lang in ("zh-TW", "ja"):
            lang_keys = set(TRANSLATIONS[lang].keys())
            missing = en_keys - lang_keys
            assert not missing, f"{lang} is missing keys: {missing}"

    def test_risk_explanation_key_mapping(self):
        assert risk_explanation_key("High") == "risk_high"
        assert risk_explanation_key("Medium") == "risk_medium"
        assert risk_explanation_key("Low") == "risk_low"
        assert risk_explanation_key("Unknown") == "risk_none"

    def test_risk_level_display_all_langs(self):
        for lang in SUPPORTED_LANGS:
            for level in ("high", "medium", "low"):
                val = t(lang, f"risk_level_{level}")
                assert val, f"risk_level_{level} empty for {lang}"

    def test_analysis_strings_exist_in_all_langs(self):
        keys = ["analysis_cited", "analysis_rewriting", "analysis_overlap", "analysis_moderate"]
        for lang in SUPPORTED_LANGS:
            for key in keys:
                assert t(lang, key), f"{key} empty for {lang}"

    def test_verdict_strings_exist_in_all_langs(self):
        for lang in SUPPORTED_LANGS:
            for level in ("high", "medium", "low"):
                val = t(lang, f"verdict_{level}", pct=25.0)
                assert "25.0" in val, f"verdict_{level} missing pct for {lang}"

    def test_progress_steps_all_langs(self):
        steps = ["step_parse", "step_pre", "step_chunk", "step_retrieve",
                 "step_sim", "step_cite", "step_report", "step_complete"]
        for lang in SUPPORTED_LANGS:
            for step in steps:
                assert t(lang, step), f"{step} empty for {lang}"

    def test_ui_strings_differ_across_languages(self):
        en_subtitle = t("en", "subtitle")
        zhtw_subtitle = t("zh-TW", "subtitle")
        ja_subtitle = t("ja", "subtitle")
        assert en_subtitle != zhtw_subtitle
        assert en_subtitle != ja_subtitle
        assert zhtw_subtitle != ja_subtitle


# ---------------------------------------------------------------------------
# Multilingual build_report tests
# ---------------------------------------------------------------------------

class TestMultilingualBuildReport:
    def test_build_report_default_lang_is_english(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs)
        assert report.lang == "en"

    def test_build_report_stores_lang_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="zh-TW")
        assert report.lang == "zh-TW"

    def test_build_report_stores_lang_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="ja")
        assert report.lang == "ja"

    def test_risk_explanation_translated_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics("High", 50.0), sims, adjs, lang="zh-TW")
        en_report = build_report("Test", _metrics("High", 50.0), sims, adjs, lang="en")
        assert report.risk_explanation != en_report.risk_explanation

    def test_risk_explanation_translated_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics("Low", 5.0), sims, adjs, lang="ja")
        en_report = build_report("Test", _metrics("Low", 5.0), sims, adjs, lang="en")
        assert report.risk_explanation != en_report.risk_explanation

    def test_final_verdict_translated_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics("Medium", 25.0), sims, adjs, lang="zh-TW")
        en_report = build_report("Test", _metrics("Medium", 25.0), sims, adjs, lang="en")
        assert report.final_verdict != en_report.final_verdict

    def test_match_analysis_cited_translated(self):
        sims = [_sim(0)]
        adjs = [_adj(0, cited=True)]
        for lang in ("zh-TW", "ja"):
            report = build_report("Test", _metrics(), sims, adjs, lang=lang)
            en_report = build_report("Test", _metrics(), sims, adjs, lang="en")
            assert report.matches[0].analysis != en_report.matches[0].analysis

    def test_match_analysis_uncited_high_semantic(self):
        sims = [_sim(0, score=0.7, semantic=0.8)]
        adjs = [_adj(0, cited=False)]
        for lang in SUPPORTED_LANGS:
            report = build_report("Test", _metrics(), sims, adjs, lang=lang)
            expected = t(lang, "analysis_rewriting")
            assert report.matches[0].analysis == expected

    def test_match_analysis_overlap(self):
        sims = [_sim(0, score=0.65, semantic=0.3)]
        adjs = [_adj(0, cited=False)]
        for lang in SUPPORTED_LANGS:
            report = build_report("Test", _metrics(), sims, adjs, lang=lang)
            expected = t(lang, "analysis_overlap")
            assert report.matches[0].analysis == expected

    def test_match_analysis_moderate(self):
        sims = [_sim(0, score=0.3, semantic=0.2)]
        adjs = [_adj(0, cited=False)]
        for lang in SUPPORTED_LANGS:
            report = build_report("Test", _metrics(), sims, adjs, lang=lang)
            expected = t(lang, "analysis_moderate")
            assert report.matches[0].analysis == expected


# ---------------------------------------------------------------------------
# Multilingual render_text tests
# ---------------------------------------------------------------------------

class TestMultilingualRenderText:
    def test_render_text_uses_report_lang_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("My Paper", _metrics(), sims, adjs, lang="zh-TW")
        text = render_text(report)
        assert "AuthentiCheck" in text
        assert "My Paper" in text
        assert t("zh-TW", "label_matched_sources") in text
        assert t("zh-TW", "label_final_verdict") in text

    def test_render_text_uses_report_lang_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("My Paper", _metrics(), sims, adjs, lang="ja")
        text = render_text(report)
        assert "AuthentiCheck" in text
        assert t("ja", "label_matched_sources") in text
        assert t("ja", "label_risk_explanation") in text

    def test_render_text_lang_override(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("My Paper", _metrics(), sims, adjs, lang="en")
        text = render_text(report, lang="zh-TW")
        assert t("zh-TW", "label_final_verdict") in text

    def test_render_text_risk_level_display_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics("High", 55.0), sims, adjs, lang="zh-TW")
        text = render_text(report)
        assert t("zh-TW", "risk_level_high") in text

    def test_render_text_cited_tag_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0, cited=True)]
        report = build_report("Test", _metrics(), sims, adjs, lang="ja")
        text = render_text(report)
        assert t("ja", "tag_cited_bracket") in text

    def test_render_text_uncited_tag_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0, cited=False)]
        report = build_report("Test", _metrics(), sims, adjs, lang="zh-TW")
        text = render_text(report)
        assert t("zh-TW", "tag_uncited_bracket") in text

    def test_render_text_contains_percentage(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        for lang in SUPPORTED_LANGS:
            report = build_report("Test", _metrics(overall=42.5), sims, adjs, lang=lang)
            text = render_text(report)
            assert "42.5%" in text


# ---------------------------------------------------------------------------
# Multilingual render_html tests
# ---------------------------------------------------------------------------

class TestMultilingualRenderHtml:
    def test_render_html_lang_attr_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="zh-TW")
        html = render_html(report)
        assert 'lang="zh-TW"' in html

    def test_render_html_lang_attr_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="ja")
        html = render_html(report)
        assert 'lang="ja"' in html

    def test_render_html_lang_attr_en(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="en")
        html = render_html(report)
        assert 'lang="en"' in html

    def test_render_html_labels_translated_zh_tw(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="zh-TW")
        html = render_html(report)
        assert t("zh-TW", "label_matched_sources") in html
        assert t("zh-TW", "label_risk_explanation") in html
        assert t("zh-TW", "label_final_verdict") in html

    def test_render_html_labels_translated_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="ja")
        html = render_html(report)
        assert t("ja", "report_title") in html
        assert t("ja", "label_final_verdict") in html

    def test_render_html_citation_tags_zh_tw(self):
        sims = [_sim(0)]
        cited_adjs = [_adj(0, cited=True)]
        report = build_report("Test", _metrics(), sims, cited_adjs, lang="zh-TW")
        html = render_html(report)
        assert t("zh-TW", "tag_cited") in html

    def test_render_html_citation_tags_ja(self):
        sims = [_sim(0)]
        adjs = [_adj(0, cited=False)]
        report = build_report("Test", _metrics(), sims, adjs, lang="ja")
        html = render_html(report)
        assert t("ja", "tag_uncited") in html

    def test_render_html_lang_override(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="en")
        html = render_html(report, lang="ja")
        assert 'lang="ja"' in html
        assert t("ja", "label_matched_sources") in html

    def test_render_html_cjk_font_in_css(self):
        sims = [_sim(0)]
        adjs = [_adj(0)]
        report = build_report("Test", _metrics(), sims, adjs, lang="zh-TW")
        html = render_html(report)
        assert "JhengHei" in html or "Noto Sans" in html or "Meiryo" in html

    def test_render_html_risk_level_display_translated(self):
        for lang in SUPPORTED_LANGS:
            sims = [_sim(0)]
            adjs = [_adj(0)]
            report = build_report("Test", _metrics("High", 60.0), sims, adjs, lang=lang)
            html = render_html(report)
            expected_display = t(lang, "risk_level_high")
            assert expected_display in html
