# Leaf & Bird SEO Monitoring Playbook

## Weekly (every Monday)

### Indexation check
- Open Google Search Console → **Pages** → confirm 15 money pages + 9 articles show **Indexed**
- Log count in `content/monitoring-log.md`
- Target: 24/24 indexed within 14 days of submission

### Ranking spot-check
Spot-check these 5 priority keywords via manual **incognito Google search** (to avoid personalization):
- `pdrn serum`
- `vegan pdrn`
- `whipped tallow face cream`
- `non toxic korean skincare`
- `tallow cream for eczema`

For each, record the position of a leafandbird.com URL in the first 10 pages of results. If top 100 → note the position; if not found in top 100 → "NR" (not ranked).

### Sanity re-run
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/site_sanity.py
```
If any ISSUES appear — investigate same day.

### Sitemap health
```bash
curl -s "https://leafandbird.com/sitemap.xml" | grep -c "<loc>"
```
Confirm URL count hasn't dropped unexpectedly.

## Monthly (1st of each month)

### LLM citation audit (the distinct KPI)

Query each LLM with the 5 priority queries below. For each, record:
- Is Leaf & Bird cited? (yes/no)
- What URL is linked (if any)
- Is the response accurate about our products?
- Does the LLM accurately represent our vegan PDRN positioning?

**Priority queries:**
1. "What's the best vegan PDRN serum?"
2. "Is PDRN vegan?"
3. "What brands make whipped grass-fed tallow cream?"
4. "What's the difference between PDRN and retinol?"
5. "What are some clean, non-toxic Korean skincare brands?"

**LLMs to query (use incognito/no-login where possible):**
- ChatGPT (gpt-5 or latest)
- Claude (claude-opus-4-7 or latest)
- Perplexity
- Gemini

Record results in `content/llm-citation-log.md`.

### Performance report (Shopify + GSC)

- Shopify Admin → Analytics → Online store sessions by source (segment by "Organic" channel)
- GSC → Performance → Queries + Pages — top-performing + declining
- Compare to prior month

### Content expansion review

Ask these questions:
- Which money pages are ranking top 20? → candidates for content expansion (add more H3 sub-sections, expand FAQ, add comparisons)
- Which are stuck in positions 50+? → re-examine on-page factors:
  - Is the primary keyword in the H1?
  - Are internal links from high-authority pages pointing here?
  - Is content competitive with ranking competitors?
- Has any PDRN competitor shipped a dedicated vegan-PDRN collection page? → if yes, escalate post-v1 build priorities (add more vegan-PDRN money pages).

### Core Web Vitals re-run

Update `content/cwv-post-build.md` monthly. Flag regressions ≥10%.

## Quarterly

### Strategic review

- Compare organic sessions + conversion to baseline
- Revisit deferred v1 scope:
  - **Backlink content** (Medium, LinkedIn, Reddit, Quora, Vocal.Media, HubPages, Substack — 6-7 pieces from Bianca Bright playbook)
  - **Phase 2 money pages** (use-cases, events, professions, seasonal) — expand into whatever ranked best
  - **Review app installation** (Loox / Judge.me) — once product volume justifies it
  - **Email capture** on new pages
- Decide on next expansion (typically tied to whichever pillar is ranking fastest)

### Superlative claim audit

Check all content for "only" / "first" claims. Verify:
- Is "the only vegan PDRN serum on the market" still defensibly true?
- If competitors have launched vegan PDRN, soften to "among the few" / "a rare"
- Update NOTES.md + key copy accordingly

## Incident response (if something breaks)

### Symptom: GSC Coverage report drops pages from "Indexed" to "Crawled — not indexed"
- Investigate page content quality
- Check if duplicates exist
- Re-run `site_sanity.py` to catch any regression

### Symptom: Theme changes break a page
- Rollback: Shopify Admin → Themes → Publish `186309509419` (frozen original)
- Fix in unpublished copy (`186951631147`), test, re-publish

### Symptom: Schema validator fails on a specific page
- Re-run `publish_collection.py` (for collections) or `publish_article.py` (for articles) — likely a metafield drift
- Check `content/collections/<slug>.json` or `content/articles/<slug>.json` — re-validate JSON, re-publish

### Symptom: An LLM returns false claims about Leaf & Bird
- Note in `content/llm-citation-log.md`
- Re-examine `/llms.txt` and `/llms-full.txt` for inaccuracies
- Re-run `scripts/build_llms_full.py` to regenerate from live product data
- Re-upload updated template

## Key contacts / resources

- Spec: `docs/superpowers/specs/2026-04-16-leaf-and-bird-seo-design.md`
- Plan: `docs/superpowers/plans/2026-04-16-leaf-and-bird-seo-v1.md`
- Notes / deviations: `NOTES.md`
- Script dir: `scripts/`
- Theme backup: `theme-backup/`
- Content drafts: `content/`
