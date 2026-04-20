"""
Translations for AuthentiCheck UI and reports.
Supported languages: en (English), zh-TW (Traditional Chinese), ja (Japanese).
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # UI
        "subtitle": "Academic plagiarism risk detection \u2014 upload a paper to get started.",
        "label_upload": "Upload Document (PDF or DOCX)",
        "label_format": "Report Format",
        "opt_html": "HTML (view in browser)",
        "opt_text": "Plain Text (download)",
        "label_chunk": "Chunking Strategy",
        "opt_sentences": "Sentences (default, more granular)",
        "opt_paragraphs": "Paragraphs (faster)",
        "label_no_semantic": "Skip semantic analysis (faster, less accurate)",
        "btn_analyze": "Analyze Document",
        "btn_uploading": "Uploading\u2026",
        "btn_analyzing": "Analyzing\u2026",
        "label_language": "Language",
        # Errors
        "err_no_file": "Please upload a PDF or DOCX file.",
        "err_bad_format": "Only PDF and DOCX files are supported.",
        "err_upload_failed": "Upload failed.",
        "err_generic": "An error occurred.",
        "err_connection": "Lost connection to server.",
        # Progress
        "step_starting": "Starting\u2026",
        "step_parse": "Parsing document",
        "step_pre": "Preprocessing text",
        "step_chunk": "Chunking text",
        "step_retrieve": "Retrieving candidate sources",
        "step_sim": "Computing similarity scores",
        "step_cite": "Applying citation awareness",
        "step_report": "Generating report",
        "step_complete": "Analysis complete!",
        "step_retrieve_n": "Retrieving sources\u2026 ({i}/{n})",
        # Report labels
        "report_title": "AuthentiCheck \u2014 Plagiarism Risk Report",
        "label_document": "Document",
        "label_overall_sim": "Overall Similarity",
        "label_risk_level": "Risk Level",
        "label_metrics": "METRICS",
        "label_high_sim_ratio": "High Similarity Ratio",
        "label_uncited_ratio": "Uncited Similarity Ratio",
        "label_paraphrase": "Paraphrase Score",
        "label_matched_sources": "Matched Sources",
        "label_match_num": "#",
        "label_source": "Source",
        "label_match_pct": "Match %",
        "label_citation": "Citation",
        "label_analysis": "Analysis",
        "label_risk_explanation": "Risk Explanation",
        "label_final_verdict": "Final Verdict",
        "tag_cited": "\u2705 Cited",
        "tag_uncited": "\u26a0\ufe0f Uncited",
        "tag_cited_bracket": "[cited]",
        "tag_uncited_bracket": "[uncited]",
        "label_excerpt": "Excerpt",
        # Risk level display values
        "risk_level_high": "High",
        "risk_level_medium": "Medium",
        "risk_level_low": "Low",
        # Per-match analysis
        "analysis_cited": "Properly cited reference \u2014 similarity is expected and acceptable.",
        "analysis_rewriting": (
            "Suspicious rewriting detected \u2014 the passage is semantically close "
            "to the source without a citation."
        ),
        "analysis_overlap": (
            "High textual overlap without citation \u2014 possible direct copying or close paraphrase."
        ),
        "analysis_moderate": (
            "Moderate similarity; may reflect common academic phrasing or shared methodology."
        ),
        # Final verdicts (use {pct} placeholder)
        "verdict_high": (
            "Final Assessment: High likelihood of plagiarism risk (overall similarity {pct:.1f}%). "
            "A substantial portion of the submitted text closely matches external sources "
            "without proper attribution. Independent review is strongly recommended."
        ),
        "verdict_medium": (
            "Final Assessment: Moderate similarity with partially acceptable citation usage "
            "(overall similarity {pct:.1f}%). "
            "Some passages require clearer attribution or rephrasing."
        ),
        "verdict_low": (
            "Final Assessment: Low similarity risk detected (overall similarity {pct:.1f}%). "
            "The document appears to be largely original with appropriate citation practices."
        ),
        # Risk explanations
        "risk_high": (
            "A large proportion of the document contains uncited or paraphrased content "
            "that closely matches external sources, indicating a high likelihood of plagiarism risk."
        ),
        "risk_medium": (
            "Moderate similarity with some uncited passages detected. "
            "The document may contain paraphrased content that warrants further review."
        ),
        "risk_low": (
            "Most similar passages appear to be properly cited or consist of common academic phrasing. "
            "Similarity levels are within acceptable range."
        ),
        "risk_none": "No similarity data available.",
    },

    "zh-TW": {
        # UI
        "subtitle": "\u5b78\u8853\u5261\u7ad9\u98a8\u9669\u5075\u6e2c\u2014\u4e0a\u50b3\u8ad6\u6587\u5373\u53ef\u958b\u59cb\u5206\u6790\u3002",
        "label_upload": "\u4e0a\u50b3\u6587\u4ef6\uff08PDF \u6216 DOCX\uff09",
        "label_format": "\u5831\u544a\u683c\u5f0f",
        "opt_html": "HTML\uff08\u5728\u700f\u89bd\u5668\u4e2d\u6aa2\u8996\uff09",
        "opt_text": "\u7d14\u6587\u5b57\uff08\u4e0b\u8f09\uff09",
        "label_chunk": "\u5206\u584a\u7b56\u7565",
        "opt_sentences": "\u53e5\u5b50\uff08\u9810\u8a2d\uff0c\u66f4\u7d30\u81f4\uff09",
        "opt_paragraphs": "\u6bb5\u843d\uff08\u8f03\u5feb\uff09",
        "label_no_semantic": "\u8df3\u904e\u8a9e\u610f\u5206\u6790\uff08\u8f03\u5feb\uff0c\u7cbe\u78ba\u5ea6\u8f03\u4f4e\uff09",
        "btn_analyze": "\u5206\u6790\u6587\u4ef6",
        "btn_uploading": "\u4e0a\u50b3\u4e2d\u2026",
        "btn_analyzing": "\u5206\u6790\u4e2d\u2026",
        "label_language": "\u8a9e\u8a00",
        # Errors
        "err_no_file": "\u8acb\u4e0a\u50b3 PDF \u6216 DOCX \u6587\u4ef6\u3002",
        "err_bad_format": "\u50c5\u652f\u63f4 PDF \u548c DOCX \u683c\u5f0f\u3002",
        "err_upload_failed": "\u4e0a\u50b3\u5931\u6557\u3002",
        "err_generic": "\u767c\u751f\u932f\u8aa4\u3002",
        "err_connection": "\u8207\u4f3a\u670d\u5668\u7684\u9023\u7dda\u4e2d\u65b7\u3002",
        # Progress
        "step_starting": "\u555f\u52d5\u4e2d\u2026",
        "step_parse": "\u6b63\u5728\u89e3\u6790\u6587\u4ef6",
        "step_pre": "\u6b63\u5728\u524d\u8655\u7406\u6587\u5b57",
        "step_chunk": "\u6b63\u5728\u5206\u5272\u6587\u5b57",
        "step_retrieve": "\u6b63\u5728\u6aa2\u7d22\u5019\u9078\u4f86\u6e90",
        "step_sim": "\u6b63\u5728\u8a08\u7b97\u76f8\u4f3c\u5ea6\u5206\u6578",
        "step_cite": "\u6b63\u5728\u5957\u7528\u5f15\u7528\u611f\u77e5",
        "step_report": "\u6b63\u5728\u751f\u6210\u5831\u544a",
        "step_complete": "\u5206\u6790\u5b8c\u6210\uff01",
        "step_retrieve_n": "\u6b63\u5728\u6aa2\u7d22\u4f86\u6e90\u2026\uff08{i}/{n}\uff09",
        # Report labels
        "report_title": "AuthentiCheck \u2014 \u5261\u7ad9\u98a8\u9669\u5831\u544a",
        "label_document": "\u6587\u4ef6",
        "label_overall_sim": "\u6574\u9ad4\u76f8\u4f3c\u5ea6",
        "label_risk_level": "\u98a8\u9669\u7b49\u7d1a",
        "label_metrics": "\u6307\u6a19",
        "label_high_sim_ratio": "\u9ad8\u76f8\u4f3c\u5ea6\u6bd4\u4f8b",
        "label_uncited_ratio": "\u672a\u5f15\u7528\u76f8\u4f3c\u5ea6\u6bd4\u4f8b",
        "label_paraphrase": "\u6539\u5beb\u5206\u6578",
        "label_matched_sources": "\u5339\u914d\u4f86\u6e90",
        "label_match_num": "#",
        "label_source": "\u4f86\u6e90",
        "label_match_pct": "\u5339\u914d\u5ea6",
        "label_citation": "\u5f15\u7528",
        "label_analysis": "\u5206\u6790",
        "label_risk_explanation": "\u98a8\u9669\u8aaa\u660e",
        "label_final_verdict": "\u6700\u7d42\u7d50\u8ad6",
        "tag_cited": "\u2705 \u5df2\u5f15\u7528",
        "tag_uncited": "\u26a0\ufe0f \u672a\u5f15\u7528",
        "tag_cited_bracket": "[\u5df2\u5f15\u7528]",
        "tag_uncited_bracket": "[\u672a\u5f15\u7528]",
        "label_excerpt": "\u6458\u9304",
        # Risk level display values
        "risk_level_high": "\u9ad8",
        "risk_level_medium": "\u4e2d",
        "risk_level_low": "\u4f4e",
        # Per-match analysis
        "analysis_cited": "\u5df2\u6b63\u78ba\u5f15\u7528\u4f86\u6e90\u2014\u76f8\u4f3c\u5ea6\u5728\u53ef\u63a5\u53d7\u7bc4\u570d\u5167\u3002",
        "analysis_rewriting": (
            "\u5075\u6e2c\u5230\u53ef\u7591\u6539\u5beb\u2014\u8a72\u6bb5\u843d\u5728\u8a9e\u610f\u4e0a\u8207\u4f86\u6e90\u9ad8\u5ea6\u76f8\u4f3c\uff0c"
            "\u4f46\u7f3a\u4e4f\u5f15\u7528\u3002"
        ),
        "analysis_overlap": (
            "\u672a\u5f15\u7528\u7684\u9ad8\u5ea6\u6587\u5b57\u91cd\u758a\u2014\u53ef\u80fd\u5b58\u5728\u76f4\u63a5\u8907\u88fd\u6216\u63a5\u8fd1\u9010\u5b57\u6539\u5beb\u7684\u60c5\u6cc1\u3002"
        ),
        "analysis_moderate": (
            "\u4e2d\u5ea6\u76f8\u4f3c\uff1b\u53ef\u80fd\u53cd\u6620\u5e38\u898b\u7684\u5b78\u8853\u7528\u8a9e\u6216\u5171\u4eab\u65b9\u6cd5\u8ad6\u3002"
        ),
        # Final verdicts
        "verdict_high": (
            "\u6700\u7d42\u8a55\u4f30\uff1a\u9ad8\u5ea6\u5261\u7ad9\u98a8\u9669\uff08\u6574\u9ad4\u76f8\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u63d0\u4ea4\u6587\u672c\u4e2d\u6709\u76f8\u7576\u5927\u6bd4\u4f8b\u8207\u5916\u90e8\u4f86\u6e90\u9ad8\u5ea6\u76f8\u7b26\u4e14\u7f3a\u4e4f\u9069\u7576\u5f15\u7528\u3002"
            "\u5f37\u70c8\u5efa\u8b70\u9032\u884c\u4eba\u5de5\u5be9\u67e5\u3002"
        ),
        "verdict_medium": (
            "\u6700\u7d42\u8a55\u4f30\uff1a\u4e2d\u5ea6\u76f8\u4f3c\uff0c\u5f15\u7528\u4f7f\u7528\u90e8\u5206\u7b26\u5408\u898f\u7bc4\uff08\u6574\u9ad4\u76f8\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u90e8\u5206\u6bb5\u843d\u9700\u8981\u66f4\u660e\u78ba\u7684\u5f15\u7528\u6a19\u6ce8\u6216\u91cd\u65b0\u6539\u5beb\u3002"
        ),
        "verdict_low": (
            "\u6700\u7d42\u8a55\u4f30\uff1a\u5075\u6e2c\u5230\u4f4e\u76f8\u4f3c\u5ea6\u98a8\u9669\uff08\u6574\u9ad4\u76f8\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u8a72\u6587\u4ef6\u5927\u81f4\u70ba\u539f\u5275\uff0c\u4e26\u5177\u6709\u9069\u7576\u7684\u5f15\u7528\u898f\u7bc4\u3002"
        ),
        # Risk explanations
        "risk_high": (
            "\u6587\u4ef6\u4e2d\u6709\u5927\u91cf\u5167\u5bb9\u5305\u542b\u672a\u5f15\u7528\u6216\u6539\u5beb\u7684\u6bb5\u843d\uff0c"
            "\u8207\u5916\u90e8\u4f86\u6e90\u9ad8\u5ea6\u76f8\u7b26\uff0c\u986f\u793a\u51fa\u9ad8\u5ea6\u7684\u5261\u7ad9\u98a8\u9669\u3002"
        ),
        "risk_medium": (
            "\u5075\u6e2c\u5230\u4e2d\u5ea6\u76f8\u4f3c\u6027\uff0c\u4e14\u5b58\u5728\u90e8\u5206\u672a\u5f15\u7528\u6bb5\u843d\u3002"
            "\u6587\u4ef6\u53ef\u80fd\u5305\u542b\u9700\u8981\u9032\u4e00\u6b65\u5be9\u67e5\u7684\u6539\u5beb\u5167\u5bb9\u3002"
        ),
        "risk_low": (
            "\u5927\u591a\u6578\u76f8\u4f3c\u6bb5\u843d\u5747\u5df2\u9069\u7576\u5f15\u7528\u6216\u5c6c\u65bc\u5e38\u898b\u5b78\u8853\u7528\u8a9e\uff0c"
            "\u76f8\u4f3c\u5ea6\u6c34\u6e96\u5728\u53ef\u63a5\u53d7\u7bc4\u570d\u5167\u3002"
        ),
        "risk_none": "\u7121\u53ef\u7528\u7684\u76f8\u4f3c\u5ea6\u8cc7\u6599\u3002",
    },

    "ja": {
        # UI
        "subtitle": "\u5b66\u8853\u7684\u5264\u7a83\u30ea\u30b9\u30af\u691c\u51fa\u2014\u8ad6\u6587\u3092\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u3057\u3066\u5206\u6790\u3092\u958b\u59cb\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "label_upload": "\u6587\u66f8\u3092\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\uff08PDF \u307e\u305f\u306f DOCX\uff09",
        "label_format": "\u30ec\u30dd\u30fc\u30c8\u5f62\u5f0f",
        "opt_html": "HTML\uff08\u30d6\u30e9\u30a6\u30b6\u3067\u8868\u793a\uff09",
        "opt_text": "\u30d7\u30ec\u30fc\u30f3\u30c6\u30ad\u30b9\u30c8\uff08\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9\uff09",
        "label_chunk": "\u30c1\u30e3\u30f3\u30af\u6226\u7565",
        "opt_sentences": "\u6587\uff08\u30c7\u30d5\u30a9\u30eb\u30c8\u3001\u3088\u308a\u8a73\u7d30\uff09",
        "opt_paragraphs": "\u6bb5\u843d\uff08\u9ad8\u901f\uff09",
        "label_no_semantic": "\u610f\u5473\u89e3\u6790\u3092\u30b9\u30ad\u30c3\u30d7\uff08\u9ad8\u901f\u3060\u304c\u7cbe\u5ea6\u4f4e\u4e0b\uff09",
        "btn_analyze": "\u6587\u66f8\u3092\u5206\u6790",
        "btn_uploading": "\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u4e2d\u2026",
        "btn_analyzing": "\u5206\u6790\u4e2d\u2026",
        "label_language": "\u8a00\u8a9e",
        # Errors
        "err_no_file": "PDF\u307e\u305f\u306fDOCX\u30d5\u30a1\u30a4\u30eb\u3092\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "err_bad_format": "PDF\u3068DOCX\u5f62\u5f0f\u306e\u307f\u5bfe\u5fdc\u3057\u3066\u3044\u307e\u3059\u3002",
        "err_upload_failed": "\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002",
        "err_generic": "\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002",
        "err_connection": "\u30b5\u30fc\u30d0\u30fc\u3068\u306e\u63a5\u7d9a\u304c\u5207\u65ad\u3055\u308c\u307e\u3057\u305f\u3002",
        # Progress
        "step_starting": "\u958b\u59cb\u4e2d\u2026",
        "step_parse": "\u6587\u66f8\u3092\u89e3\u6790\u4e2d",
        "step_pre": "\u30c6\u30ad\u30b9\u30c8\u3092\u524d\u51e6\u7406\u4e2d",
        "step_chunk": "\u30c6\u30ad\u30b9\u30c8\u3092\u5206\u5272\u4e2d",
        "step_retrieve": "\u5019\u88dc\u30bd\u30fc\u30b9\u3092\u691c\u7d22\u4e2d",
        "step_sim": "\u985e\u4f3c\u5ea6\u30b9\u30b3\u30a2\u3092\u8a08\u7b97\u4e2d",
        "step_cite": "\u5f15\u7528\u8a8d\u8b58\u3092\u9069\u7528\u4e2d",
        "step_report": "\u30ec\u30dd\u30fc\u30c8\u3092\u751f\u6210\u4e2d",
        "step_complete": "\u5206\u6790\u5b8c\u4e86\uff01",
        "step_retrieve_n": "\u30bd\u30fc\u30b9\u3092\u691c\u7d22\u4e2d\u2026 ({i}/{n})",
        # Report labels
        "report_title": "AuthentiCheck \u2014 \u5264\u7a83\u30ea\u30b9\u30af\u30ec\u30dd\u30fc\u30c8",
        "label_document": "\u6587\u66f8",
        "label_overall_sim": "\u7dcf\u5408\u985e\u4f3c\u5ea6",
        "label_risk_level": "\u30ea\u30b9\u30af\u30ec\u30d9\u30eb",
        "label_metrics": "\u6307\u6a19",
        "label_high_sim_ratio": "\u9ad8\u985e\u4f3c\u5ea6\u6bd4\u7387",
        "label_uncited_ratio": "\u672a\u5f15\u7528\u985e\u4f3c\u5ea6\u6bd4\u7387",
        "label_paraphrase": "\u8a00\u3044\u63db\u3048\u30b9\u30b3\u30a2",
        "label_matched_sources": "\u4e00\u81f4\u3057\u305f\u30bd\u30fc\u30b9",
        "label_match_num": "#",
        "label_source": "\u30bd\u30fc\u30b9",
        "label_match_pct": "\u4e00\u81f4\u7387",
        "label_citation": "\u5f15\u7528",
        "label_analysis": "\u5206\u6790",
        "label_risk_explanation": "\u30ea\u30b9\u30af\u8aac\u660e",
        "label_final_verdict": "\u6700\u7d42\u5224\u5b9a",
        "tag_cited": "\u2705 \u5f15\u7528\u3042\u308a",
        "tag_uncited": "\u26a0\ufe0f \u5f15\u7528\u306a\u3057",
        "tag_cited_bracket": "[\u5f15\u7528\u3042\u308a]",
        "tag_uncited_bracket": "[\u5f15\u7528\u306a\u3057]",
        "label_excerpt": "\u629c\u7c8b",
        # Risk level display values
        "risk_level_high": "\u9ad8",
        "risk_level_medium": "\u4e2d",
        "risk_level_low": "\u4f4e",
        # Per-match analysis
        "analysis_cited": "\u9069\u5207\u306a\u5f15\u7528\u304c\u3042\u308b\u53c2\u7167\u2014\u985e\u4f3c\u5ea6\u306f\u60f3\u5b9a\u5185\u3067\u8a31\u5bb9\u7bc4\u56f2\u3067\u3059\u3002",
        "analysis_rewriting": (
            "\u4e0d\u5be9\u306a\u8a00\u3044\u63db\u3048\u3092\u691c\u51fa\u2014\u3053\u306e\u6587\u306f\u5f15\u7528\u306a\u3057\u306b\u30bd\u30fc\u30b9\u3068\u610f\u5473\u7684\u306b\u8fd1\u4f3c\u3057\u3066\u3044\u307e\u3059\u3002"
        ),
        "analysis_overlap": (
            "\u5f15\u7528\u306a\u3057\u306e\u9ad8\u3044\u30c6\u30ad\u30b9\u30c8\u91cd\u8907\u2014\u76f4\u63a5\u7684\u306a\u30b3\u30d4\u30fc\u307e\u305f\u306f\u63a5\u8fd1\u3057\u305f\u8a00\u3044\u63db\u3048\u306e\u53ef\u80fd\u6027\u304c\u3042\u308a\u307e\u3059\u3002"
        ),
        "analysis_moderate": (
            "\u4e2d\u7a0b\u5ea6\u306e\u985e\u4f3c\u5ea6\uff1b\u4e00\u822c\u7684\u306a\u5b66\u8853\u7684\u8868\u73fe\u3084\u5171\u901a\u306e\u65b9\u6cd5\u8ad6\u3092\u53cd\u6620\u3057\u3066\u3044\u308b\u53ef\u80fd\u6027\u304c\u3042\u308a\u307e\u3059\u3002"
        ),
        # Final verdicts
        "verdict_high": (
            "\u6700\u7d42\u8a55\u4fa1\uff1a\u5264\u7a83\u30ea\u30b9\u30af\u304c\u9ad8\u3044\u53ef\u80fd\u6027\u304c\u3042\u308a\u307e\u3059\uff08\u7dcf\u5408\u985e\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u63d0\u51fa\u6587\u66f8\u306e\u76f8\u5f53\u90e8\u5206\u304c\u9069\u5207\u306a\u5e30\u5c5e\u8868\u793a\u306a\u3057\u306b\u5916\u90e8\u30bd\u30fc\u30b9\u3068\u9ad8\u5ea6\u306b\u4e00\u81f4\u3057\u3066\u3044\u307e\u3059\u3002"
            "\u72ec\u7acb\u3057\u305f\u30ec\u30d3\u30e5\u30fc\u3092\u5f37\u304f\u304a\u52e7\u3081\u3057\u307e\u3059\u3002"
        ),
        "verdict_medium": (
            "\u6700\u7d42\u8a55\u4fa1\uff1a\u4e2d\u7a0b\u5ea6\u306e\u985e\u4f3c\u5ea6\u3067\u3001\u5f15\u7528\u4f7f\u7528\u306f\u90e8\u5206\u7684\u306b\u8a31\u5bb9\u7bc4\u56f2\u5185\u3067\u3059\uff08\u7dcf\u5408\u985e\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u4e00\u90e8\u306e\u6587\u7ae0\u306f\u3088\u308a\u660e\u78ba\u306a\u5e30\u5c5e\u8868\u793a\u307e\u305f\u306f\u8a00\u3044\u63db\u3048\u304c\u5fc5\u8981\u3067\u3059\u3002"
        ),
        "verdict_low": (
            "\u6700\u7d42\u8a55\u4fa1\uff1a\u4f4e\u3044\u985e\u4f3c\u5ea6\u30ea\u30b9\u30af\u3092\u691c\u51fa\u3057\u307e\u3057\u305f\uff08\u7dcf\u5408\u985e\u4f3c\u5ea6 {pct:.1f}%\uff09\u3002"
            "\u3053\u306e\u6587\u66f8\u306f\u6982\u306d\u72ec\u5275\u7684\u3067\u3042\u308a\u3001\u9069\u5207\u306a\u5f15\u7528\u6163\u884c\u304c\u898b\u3089\u308c\u307e\u3059\u3002"
        ),
        # Risk explanations
        "risk_high": (
            "\u6587\u66f8\u306e\u5927\u90e8\u5206\u306b\u3001\u5916\u90e8\u30bd\u30fc\u30b9\u3068\u9ad8\u5ea6\u306b\u4e00\u81f4\u3059\u308b\u672a\u5f15\u7528\u307e\u305f\u306f\u8a00\u3044\u63db\u3048\u3089\u308c\u305f\u30b3\u30f3\u30c6\u30f3\u30c4\u304c\u542b\u307e\u308c\u3066\u304a\u308a\u3001"
            "\u5264\u7a83\u30ea\u30b9\u30af\u304c\u9ad8\u3044\u53ef\u80fd\u6027\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
        ),
        "risk_medium": (
            "\u4e2d\u7a0b\u5ea6\u306e\u985e\u4f3c\u5ea6\u304c\u691c\u51fa\u3055\u308c\u3001\u4e00\u90e8\u306b\u672a\u5f15\u7528\u306e\u6587\u7ae0\u304c\u898b\u3089\u308c\u307e\u3059\u3002"
            "\u6587\u66f8\u306b\u306f\u3055\u3089\u306a\u308b\u30ec\u30d3\u30e5\u30fc\u304c\u5fc5\u8981\u306a\u8a00\u3044\u63db\u3048\u30b3\u30f3\u30c6\u30f3\u30c4\u304c\u542b\u307e\u308c\u3066\u3044\u308b\u53ef\u80fd\u6027\u304c\u3042\u308a\u307e\u3059\u3002"
        ),
        "risk_low": (
            "\u307b\u3068\u3093\u3069\u306e\u985e\u4f3c\u3057\u305f\u6587\u7ae0\u306f\u9069\u5207\u306b\u5f15\u7528\u3055\u308c\u3066\u3044\u308b\u304b\u3001\u4e00\u822c\u7684\u306a\u5b66\u8853\u7684\u8868\u73fe\u3067\u69cb\u6210\u3055\u308c\u3066\u3044\u307e\u3059\u3002"
            "\u985e\u4f3c\u5ea6\u30ec\u30d9\u30eb\u306f\u8a31\u5bb9\u7bc4\u56f2\u5185\u3067\u3059\u3002"
        ),
        "risk_none": "\u5229\u7528\u53ef\u80fd\u306a\u985e\u4f3c\u5ea6\u30c7\u30fc\u30bf\u304c\u3042\u308a\u307e\u305b\u3093\u3002",
    },
}

_RISK_EXPLANATION_KEYS = {
    "High": "risk_high",
    "Medium": "risk_medium",
    "Low": "risk_low",
}

SUPPORTED_LANGS = list(TRANSLATIONS.keys())


def t(lang: str, key: str, **kwargs) -> str:
    """Return a translated string, falling back to English if not found."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = lang_dict.get(key) or TRANSLATIONS["en"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def risk_explanation_key(risk_level: str) -> str:
    return _RISK_EXPLANATION_KEYS.get(risk_level, "risk_none")
