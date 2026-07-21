#!/usr/bin/env python3
"""Build index.html from papers.json.

Reads papers.json (produced by fetch_papers.py) and writes a self-contained
index.html with the data embedded, so it works both locally (file://) and on
GitHub Pages. No external JS/CSS — the citation chart is drawn as inline SVG.

Usage: python -X utf8 build_page.py
"""

import html
import json
from collections import defaultdict

ACCENT = "#4b2e83"  # UW purple


def h_index(citations):
    citations = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(citations, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def citations_by_year(papers):
    totals = defaultdict(int)
    for p in papers:
        for c in p["counts_by_year"]:
            totals[c["year"]] += c["cited_by_count"]
    return dict(sorted(totals.items()))


def svg_bar_chart(year_counts, width=760, height=280, pad=44):
    if not year_counts:
        return "<p>No yearly citation data.</p>"
    years = list(year_counts.keys())
    vals = list(year_counts.values())
    ymax = max(vals) or 1
    plot_w = width - pad * 2
    plot_h = height - pad * 2
    n = len(years)
    gap = plot_w / n
    bar_w = gap * 0.7
    bars = []
    for i, (yr, v) in enumerate(year_counts.items()):
        bh = (v / ymax) * plot_h
        x = pad + i * gap + (gap - bar_w) / 2
        y = pad + (plot_h - bh)
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" '
            f'rx="2" fill="{ACCENT}"><title>{yr}: {v} citations</title></rect>')
    # x labels every ~5 years to avoid crowding
    labels = []
    step = max(1, n // 8)
    for i, yr in enumerate(years):
        if i % step == 0 or i == n - 1:
            x = pad + i * gap + gap / 2
            labels.append(
                f'<text x="{x:.1f}" y="{height - pad + 18:.1f}" text-anchor="middle" '
                f'font-size="11" fill="#666">{yr}</text>')
    # y gridlines
    grid = []
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        gy = pad + plot_h - frac * plot_h
        val = round(ymax * frac)
        grid.append(
            f'<line x1="{pad}" y1="{gy:.1f}" x2="{width - pad}" y2="{gy:.1f}" '
            f'stroke="#eee" stroke-width="1"/>')
        grid.append(
            f'<text x="{pad - 8}" y="{gy + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#999">{val}</text>')
    return (f'<svg viewBox="0 0 {width} {height}" width="100%" '
            f'role="img" aria-label="Citations per year">'
            + "".join(grid) + "".join(bars) + "".join(labels) + "</svg>")


def paper_rows(papers):
    by_year = defaultdict(list)
    for p in papers:
        by_year[p["year"] or 0].append(p)
    out = []
    for yr in sorted(by_year, reverse=True):
        out.append(f'<h3 class="year">{yr or "Undated"}</h3>')
        for p in sorted(by_year[yr], key=lambda p: -p["cited_by_count"]):
            title = html.escape(p["title"])
            venue = html.escape(p["venue"]) if p["venue"] else ""
            url = html.escape(p["url"])
            cites = p["cited_by_count"]
            venue_html = f'<span class="venue">{venue}</span>' if venue else ""
            out.append(
                '<div class="paper">'
                f'<a class="ptitle" href="{url}" target="_blank" rel="noopener">{title}</a>'
                f'<div class="pmeta">{venue_html}'
                f'<span class="cites">{cites} citation{"s" if cites != 1 else ""}</span>'
                '</div></div>')
    return "\n".join(out)


def main():
    data = json.load(open("papers.json", encoding="utf-8"))
    author = data["author"]
    papers = data["papers"]

    total_papers = len(papers)
    total_cites = author["cited_by_count"]
    hidx = h_index([p["cited_by_count"] for p in papers])
    top = max(papers, key=lambda p: p["cited_by_count"])
    year_counts = citations_by_year(papers)
    chart = svg_bar_chart(year_counts)
    rows = paper_rows(papers)
    name = html.escape(author["name"])
    orcid = html.escape(author["orcid"])

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Publications</title>
<style>
  :root {{ --accent: {ACCENT}; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; color: #1a1a1a; background: #fafafa;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.55;
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 3rem 1.25rem 5rem; }}
  header h1 {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 2.4rem; margin: 0 0 .25rem; color: var(--accent);
  }}
  header .sub {{ color: #666; margin: 0; font-size: 1rem; }}
  header .sub a {{ color: var(--accent); }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem; margin: 2rem 0; }}
  .stat {{ background: #fff; border: 1px solid #ececec; border-radius: 10px;
    padding: 1.1rem 1.25rem; }}
  .stat .num {{ font-size: 1.9rem; font-weight: 700; color: var(--accent);
    font-family: Georgia, serif; }}
  .stat .lbl {{ font-size: .82rem; color: #777; text-transform: uppercase;
    letter-spacing: .04em; }}
  .stat.top .num {{ font-size: 1.05rem; line-height: 1.3; }}
  section {{ margin-top: 2.5rem; }}
  section > h2 {{ font-family: Georgia, serif; font-size: 1.4rem; color: #222;
    border-bottom: 2px solid var(--accent); padding-bottom: .4rem; }}
  .card {{ background: #fff; border: 1px solid #ececec; border-radius: 10px;
    padding: 1.5rem; }}
  .caveat {{ font-size: .82rem; color: #999; margin-top: .75rem; }}
  h3.year {{ font-family: Georgia, serif; color: var(--accent); font-size: 1.15rem;
    margin: 1.75rem 0 .5rem; }}
  .paper {{ padding: .7rem 0; border-bottom: 1px solid #f0f0f0; }}
  .paper:last-child {{ border-bottom: none; }}
  .ptitle {{ color: #1a1a1a; text-decoration: none; font-weight: 600; }}
  .ptitle:hover {{ color: var(--accent); text-decoration: underline; }}
  .pmeta {{ font-size: .85rem; color: #777; margin-top: .2rem;
    display: flex; gap: 1rem; flex-wrap: wrap; }}
  .pmeta .venue {{ font-style: italic; }}
  .pmeta .cites {{ color: var(--accent); font-weight: 600; }}
  footer {{ margin-top: 3rem; font-size: .8rem; color: #aaa; text-align: center; }}
  footer a {{ color: #999; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{name}</h1>
    <p class="sub">Published research &middot;
      <a href="https://orcid.org/{orcid}" target="_blank" rel="noopener">ORCID {orcid}</a></p>
  </header>

  <div class="stats">
    <div class="stat"><div class="num">{total_papers}</div><div class="lbl">Publications</div></div>
    <div class="stat"><div class="num">{total_cites:,}</div><div class="lbl">Total citations</div></div>
    <div class="stat"><div class="num">{hidx}</div><div class="lbl">h-index</div></div>
    <div class="stat top"><div class="num">{html.escape(top['title'][:60])}{'…' if len(top['title']) > 60 else ''}</div>
      <div class="lbl">Most cited · {top['cited_by_count']:,}</div></div>
  </div>

  <section>
    <h2>Citations per year</h2>
    <div class="card">
      {chart}
      <p class="caveat">OpenAlex breaks citations out by year from about 2012 on;
        earlier citations count in the lifetime total but are not shown here.</p>
    </div>
  </section>

  <section>
    <h2>Publications ({total_papers})</h2>
    {rows}
  </section>

  <footer>
    Data from <a href="https://openalex.org" target="_blank" rel="noopener">OpenAlex</a>.
    Built with Claude Code.
  </footer>
</div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote index.html — {total_papers} papers, {total_cites:,} citations, "
          f"h-index {hidx}, chart spans {min(year_counts)}–{max(year_counts)}")


if __name__ == "__main__":
    main()
