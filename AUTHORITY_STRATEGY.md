# Authority Strategy — Suppressing Accurate Gov/News Results

**Situation:** The negative results are accurate, current `.gov`/court records and real
news articles. They **cannot be removed**. You already own a strong, page-1 personal site.

**Win condition:** A name search has ~8–10 organic page-1 slots. You can't delete the
negatives — you *out-populate* them. Legitimately own 7–8 distinct, authoritative slots
and the gov/news pages sink to the bottom of page 1 and onto page 2. That is the goal.
Timeframe is 3–9 months, not weeks. Anyone promising removal of accurate government
records is lying.

---

## Stop (retired from the pipeline)

`telegraph`, `gist`, `tumblr`, `github_pages` — and the mass-duplicate dev.to/hashnode
spray. At 283 near-duplicate keyword pages these now trigger Google's *scaled-content-abuse*
and *site-reputation-abuse* policies (2024–25). They get suppressed/deindexed and drag your
whole footprint down — which is why the gov/news pages are climbing back. Already disabled
in `publish.py` via `DEAD_WEIGHT_PLATFORMS` (override with `ORM_ALLOW_DEAD_WEIGHT=1`).

---

## Do — the authority stack (in priority order)

### 1. Entity / Knowledge Panel signal  *(highest leverage, do first)*
- Run `python publish.py --export-schema` → paste `person_schema.html` into the `<head>`
  of your site's home + about pages. Set `SAME_AS_URLS` in `.env` first (comma-separated
  list of every profile you own — keep the list byte-identical everywhere it appears).
- Create a **Wikidata** entry for yourself (allowed without Wikipedia notability) with the
  same `sameAs` links. This is the strongest single Knowledge-Panel trigger.
- Consistent NAP: exact same name, title, and location everywhere.

### 2. Own distinct name-ranking profiles  *(one canonical bio each — no variations)*
Each reliably takes a page-1 slot for a person's name:
- Crunchbase · Muck Rack · About.me · F6S · real Medium profile · YouTube channel
- X/Twitter · a university alumni or professional-association directory page
Fill them out fully (photo, bio, links back to your site). Thin profiles don't rank.

### 3. Real third-party coverage  *(the only thing that outranks a news negative)*
- Journalist-request platforms: **HARO / Qwoted / Featured** — respond to reporters in
  your domain (operations, construction ops, exec leadership). Each pickup = a real news
  URL that competes on the same footing as the negative news pages.
- **Podcast guesting** — each episode's show-notes page is a rankable, name-anchored asset.
- Guest columns on genuine trade publications; speaking-engagement/agenda pages.

### 4. Feed your strong site, not the spray
- Repurpose the best ~15 existing articles into substantive, *unique* pieces on your own
  domain + real Medium profile. Internally link them. Keep them fresh (freshness ranks).
- Retire/deindex the rest to shrink the spam footprint.

---

## What NOT to do
- Don't try to "knock down" the gov/news pages directly — you can't touch someone else's
  page, and low-quality attack content backfires.
- Don't keep mass-publishing near-duplicates; it's now a net negative.
- Don't buy links or use PBNs — a manual action would sink your good site too.

## Legal / removal notes (accurate content)
- Accurate government records: generally not removable. Check only for record
  sealing/expungement if legally eligible.
- If any specific page becomes outdated/changes, use Google's *Remove Outdated Content* tool.
- If any news item is genuinely defamatory/false, that's a legal question for counsel — not SEO.
