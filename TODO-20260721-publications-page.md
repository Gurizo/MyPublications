# TODO: Publications page with citation charts

**Goal:** An interactive HTML page of published papers, with charts of how
citations have grown over time, published live via GitHub Pages so it can be
shared. Built for the UW Claude Code workshop, Lesson 2 (2026-07-21).

## Plan

- [x] Create `MyPublications` repo in `ws`, push to GitHub (public)
- [x] Confirm whose papers to use: Brendan MacLean, ORCID 0000-0002-9575-0255,
      University of Washington (workshop stand-in — Lucas has no ORCID yet)
- [x] Fetch all works from OpenAlex by ORCID (`fetch_papers.py` → `papers.json`
      + `papers.csv`), with venue, year, type, link, citations by year
- [x] Check the list: dropped 3 name-collision papers (different Brendan MacLean:
      1975 geology, 1984 QC report, 1996 avian medicine) via `exclusions.json`;
      dropped preprint/other/report types. 82 works remain.
- [x] Design decided (see below)
- [ ] Build `index.html`, review in browser, commit
- [ ] Refine the look until happy
- [ ] Push, turn on GitHub Pages, confirm the live URL
- [ ] Mark this spec complete, commit; copy to `ClaudeLab/todos/completed`
- [ ] (Stretch) Package as a `/publications-page` skill in `ws/.claude/skills`

## Design

- **Style:** clean academic — light background, serif headings, generous
  whitespace, reads like a polished CV.
- **Accent:** UW purple (#4b2e83).
- **Header stat cards:** total papers, total citations, h-index, most-cited paper.
- **Chart:** citations per year (bar/area), the "growth over time" visual.
  Note the pre-2012 caveat on the chart.
- **Paper list:** grouped by year (newest first); each row shows title (linked to
  DOI), venue, year, and citation count.
- **Build:** `build_page.py` reads `papers.json` and writes `index.html` with the
  data embedded, so the page works locally (file://) and on GitHub Pages.

## Decisions and notes

- Run Python with `-X utf8` for anything in this session.
- OpenAlex rate-limits: on a 429/slow-down, wait and retry instead of failing.
- OpenAlex only breaks citations out by year from ~2012 on; older citations
  count in lifetime totals only.
