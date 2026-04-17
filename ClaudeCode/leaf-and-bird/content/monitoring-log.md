# Leaf & Bird — Weekly SEO Monitoring Log

Format per week:

```
## YYYY-MM-DD
- Indexed pages: NN / 24
- Ranking spot-checks (incognito Google):
  - "pdrn serum" → position N
  - "vegan pdrn" → position N
  - "whipped tallow face cream" → position N
  - "non toxic korean skincare" → position N
  - "tallow cream for eczema" → position N
- site_sanity.py: OK / N issues
- Sitemap URL count: N
- Notes:
```

## 2026-04-17 (v1 build-completion snapshot)

- **Indexed pages:** 0 / 24 (just published — allow 7-14 days for Google to crawl + index)
- **Ranking spot-checks:** N/A (too early)
- **site_sanity.py:** ✅ OK (24/24 URLs pass all 7 checks: schema, H1, meta description, canonical, HTTPS OG, ≥2 internal links, FAQPage)
- **IndexNow:** 26 URLs submitted (Bing/Yandex will pick up within hours)
- **GSC sitemap:** pending user submission (see `gsc-submission-instructions.md`)
- **Notes:** v1 build complete — 15 money pages + 9 articles + 9 products rewritten + tech SEO + llms.txt + robots.txt. First weekly check scheduled for **2026-04-24**.

## 2026-04-17 (post-launch sanity tick)

- **site_sanity.py:** ✅ OK (24/24 URLs pass all 7 checks)
- **check_links.py:** ✅ OK (0 warnings across 15 money pages; internal-link density healthy — every page has ≥7 collection links, ≥3 product links, ≥1 pillar cluster link)
- **Sitemap URL count:** 54 total (10 products, 24 collections, 5 pages, 15 blog articles) — sitemap.xml + all 4 sub-sitemaps return 200
- **Indexed pages:** 0 / 24 (still early — ~4 hours since IndexNow ping, no GSC submission yet)
- **Ranking spot-checks:** N/A (too early)
- **Notes:** No regressions detected. Kicking off content expansion round 2 this session.

## 2026-04-17 (content expansion round 2 shipped)

- **New money pages (3):**
  - `/collections/vegan-snail-mucin-alternative` (id 526393082155) — primary kw: `vegan snail mucin alternative`
  - `/collections/korean-skincare-without-snail-mucin` (id 526393114923) — primary kw: `korean skincare without snail mucin`
  - `/collections/snail-mucin-vs-pdrn` (id 526393213227) — primary kw: `snail mucin vs pdrn`
- **New blog articles (4):**
  - `/blogs/journal/snail-mucin-alternatives-for-vegans` (id 612228989227)
  - `/blogs/journal/snail-mucin-vs-pdrn-explained` (id 612229021995)
  - `/blogs/journal/pdrn-vs-hyaluronic-acid` (id 612229054763)
  - `/blogs/journal/pdrn-vs-peptides` (id 612229087531)
- **Site totals after round 2:** 18 money pages (was 15) + 13 blog articles (was 9) = 31 URLs in `site_sanity.py`
- **Cross-links added:** `clean-korean-skincare`, `vegan-pdrn-serum`, `is-pdrn-vegan`, `is-korean-skincare-non-toxic` all now link into round-2 cluster for crawl equity
- **site_sanity.py (extended):** ✅ OK (31/31 URLs pass all 7 checks)
- **IndexNow:** 7 new URLs submitted to api.indexnow.org (200), Bing (200), Yandex (202)
- **Schema + FAQPage:** all 4 new articles emit 2 JSON-LD blocks with FAQPage
- **GSC sitemap:** new collections + articles will appear in sub-sitemaps automatically (Shopify regenerates); user still needs to resubmit `/sitemap.xml` in GSC to trigger re-crawl
- **Notes:** Cluster A (snail mucin alternative) is the strongest organic play — targets K-beauty → crunchy-mom bridge with our vegan PDRN moat. Cluster C (PDRN vs X) reinforces PDRN entity authority and supports LLM citation. Expected ranking signal within 2-4 weeks for lowest-competition queries (e.g., `vegan snail mucin alternative`, `korean skincare without snail mucin`).
