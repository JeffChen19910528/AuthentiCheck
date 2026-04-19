import time
import requests
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SourceResult:
    title: str
    abstract: str
    url: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    source_api: str = ""


def _extract_keywords(text: str, top_n: int = 5) -> List[str]:
    try:
        from keybert import KeyBERT
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=top_n)
        return [kw for kw, _ in keywords]
    except Exception:
        words = text.split()
        seen = set()
        out = []
        for w in words:
            w = w.lower().strip(".,;:()")
            if len(w) > 5 and w not in seen:
                seen.add(w)
                out.append(w)
                if len(out) >= top_n:
                    break
        return out


def _query_semantic_scholar(query: str, limit: int = 5) -> List[SourceResult]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": "title,abstract,authors,year,externalIds"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        results = []
        for item in data:
            paper_id = item.get("paperId", "")
            ext = item.get("externalIds", {})
            doi = ext.get("DOI", "")
            paper_url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else ""
            if doi:
                paper_url = f"https://doi.org/{doi}"
            results.append(SourceResult(
                title=item.get("title", ""),
                abstract=item.get("abstract", "") or "",
                url=paper_url,
                authors=[a.get("name", "") for a in item.get("authors", [])],
                year=item.get("year"),
                source_api="SemanticScholar",
            ))
        return results
    except Exception:
        return []


def _query_arxiv(query: str, limit: int = 5) -> List[SourceResult]:
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "max_results": limit}
    try:
        import xml.etree.ElementTree as ET
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            abstract = entry.findtext("atom:summary", default="", namespaces=ns).strip()
            link = entry.find("atom:id", ns)
            paper_url = link.text.strip() if link is not None else ""
            results.append(SourceResult(
                title=title,
                abstract=abstract,
                url=paper_url,
                source_api="arXiv",
            ))
        return results
    except Exception:
        return []


def _query_crossref(query: str, limit: int = 5) -> List[SourceResult]:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": limit, "select": "title,abstract,author,published,DOI,URL"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
        results = []
        for item in items:
            titles = item.get("title", [""])
            title = titles[0] if titles else ""
            abstract = item.get("abstract", "") or ""
            abstract = _strip_jats(abstract)
            doi = item.get("DOI", "")
            paper_url = f"https://doi.org/{doi}" if doi else item.get("URL", "")
            authors = [
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in item.get("author", [])
            ]
            pub = item.get("published", {}).get("date-parts", [[None]])[0]
            year = pub[0] if pub else None
            results.append(SourceResult(
                title=title,
                abstract=abstract,
                url=paper_url,
                authors=authors,
                year=year,
                source_api="CrossRef",
            ))
        return results
    except Exception:
        return []


def _strip_jats(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


def retrieve_sources(chunk_text: str, top_n: int = 5) -> List[SourceResult]:
    keywords = _extract_keywords(chunk_text, top_n=5)
    query = " ".join(keywords)

    results: List[SourceResult] = []
    results += _query_semantic_scholar(query, limit=top_n)
    time.sleep(0.3)
    results += _query_arxiv(query, limit=top_n)
    time.sleep(0.3)
    results += _query_crossref(query, limit=top_n)

    seen_titles = set()
    deduped = []
    for r in results:
        key = r.title.lower().strip()
        if key and key not in seen_titles:
            seen_titles.add(key)
            deduped.append(r)

    return deduped[:top_n]
