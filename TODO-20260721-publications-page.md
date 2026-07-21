# TODO: Publications page with citation charts

**Goal:** An interactive HTML page of published papers, with charts of how
citations have grown over time, published live via GitHub Pages so it can be
shared. Built for the UW Claude Code workshop, Lesson 2 (2026-07-21).

## Plan

- [x] Create `MyPublications` repo in `ws`, push to GitHub (public)
- [ ] Confirm whose papers to use, and the ORCID
- [ ] Fetch all works from OpenAlex by ORCID (`fetch_papers.py` → `papers.json`
      + a skimmable spreadsheet), with venue, year, type, link, citations by year
- [ ] Check the list by eye; drop anything not theirs; decide on preprints
- [ ] Design interview (~10 questions), fold answers into this spec, approve
- [ ] Build `index.html`, review in browser, commit
- [ ] Refine the look until happy
- [ ] Push, turn on GitHub Pages, confirm the live URL
- [ ] Mark this spec complete, commit; copy to `ClaudeLab/todos/completed`
- [ ] (Stretch) Package as a `/publications-page` skill in `ws/.claude/skills`

## Decisions and notes

- Run Python with `-X utf8` for anything in this session.
- OpenAlex rate-limits: on a 429/slow-down, wait and retry instead of failing.
- OpenAlex only breaks citations out by year from ~2012 on; older citations
  count in lifetime totals only.
