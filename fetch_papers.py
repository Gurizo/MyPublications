#!/usr/bin/env python3
"""Fetch a researcher's works from OpenAlex by ORCID.

Usage: python -X utf8 fetch_papers.py [ORCID] [--exclude-types type1,type2]

Saves:
  papers.json  - full records for the page (title, year, venue, type, link,
                 lifetime citations, citations by year, authors)
  papers.csv   - skimmable list for checking by eye

Respects OpenAlex rate limits: on a 429 or server error it waits and retries
instead of failing.
"""

import csv
import json
import ssl
import sys
import time
import urllib.parse
import urllib.request

try:  # macOS python.org installs don't trust system certs without certifi
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

DEFAULT_ORCID = "0000-0002-9575-0255"
MAILTO = "cho.ta@husky.neu.edu"  # polite-pool contact for OpenAlex
EXCLUSIONS_FILE = "exclusions.json"  # OpenAlex work IDs to always drop


def get_json(url, tries=6):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"fetch_papers.py (mailto:{MAILTO})"})
            with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                wait = 2 ** attempt
                print(f"  OpenAlex asked us to slow down ({e.code}); waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("unreachable")


def fetch_works(orcid):
    base = "https://api.openalex.org/works"
    filt = f"author.orcid:{orcid}"
    cursor = "*"
    works = []
    while cursor:
        params = urllib.parse.urlencode({
            "filter": filt, "per-page": 200, "cursor": cursor, "mailto": MAILTO,
        })
        page = get_json(f"{base}?{params}")
        works.extend(page["results"])
        cursor = page["meta"].get("next_cursor")
    return works


def simplify(w):
    loc = w.get("primary_location") or {}
    source = loc.get("source") or {}
    return {
        "id": w["id"],
        "title": w.get("display_name") or "(untitled)",
        "year": w.get("publication_year"),
        "venue": source.get("display_name") or "",
        "type": w.get("type") or "",
        "doi": w.get("doi") or "",
        "url": w.get("doi") or (loc.get("landing_page_url") or w["id"]),
        "cited_by_count": w.get("cited_by_count", 0),
        "counts_by_year": sorted(
            [{"year": c["year"], "cited_by_count": c["cited_by_count"]}
             for c in w.get("counts_by_year", [])],
            key=lambda c: c["year"]),
        "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    orcid = args[0] if args else DEFAULT_ORCID
    exclude_types = set()
    for a in sys.argv[1:]:
        if a.startswith("--exclude-types"):
            exclude_types = set(a.split("=", 1)[1].split(","))

    author = get_json(f"https://api.openalex.org/authors/orcid:{orcid}?mailto={MAILTO}")
    print(f"Author: {author['display_name']} — {author['works_count']} works, "
          f"{author['cited_by_count']} lifetime citations")

    papers = [simplify(w) for w in fetch_works(orcid)]

    try:
        with open(EXCLUSIONS_FILE, encoding="utf-8") as f:
            excluded_ids = set(json.load(f))
        before = len(papers)
        papers = [p for p in papers if p["id"] not in excluded_ids]
        if before != len(papers):
            print(f"Dropped {before - len(papers)} previously excluded work(s).")
    except FileNotFoundError:
        pass

    if exclude_types:
        before = len(papers)
        papers = [p for p in papers if p["type"] not in exclude_types]
        print(f"Dropped {before - len(papers)} work(s) of type: {', '.join(sorted(exclude_types))}")

    papers.sort(key=lambda p: (-(p["year"] or 0), -p["cited_by_count"]))

    with open("papers.json", "w", encoding="utf-8") as f:
        json.dump({"author": {
            "name": author["display_name"],
            "orcid": orcid,
            "works_count": len(papers),
            "cited_by_count": author["cited_by_count"],
        }, "papers": papers}, f, indent=1, ensure_ascii=False)

    with open("papers.csv", "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["title", "year", "venue", "type", "citations", "co-authors"])
        for p in papers:
            wr.writerow([p["title"], p["year"], p["venue"], p["type"],
                         p["cited_by_count"], "; ".join(p["authors"])])

    print(f"\nSaved {len(papers)} works to papers.json and papers.csv")
    by_type = {}
    for p in papers:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    print("Breakdown by type:")
    for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
        print(f"  {t:20s} {n}")


if __name__ == "__main__":
    main()
