# T6.3 — Google Search Console Submission (Your Action Required)

Google Search Console requires property ownership to submit sitemaps and request indexing. This is your action — takes ~5 minutes.

## 1. Verify property ownership (skip if already done)

- Open [https://search.google.com/search-console/](https://search.google.com/search-console/)
- Confirm `leafandbird.com` (or `https://leafandbird.com/`) is listed as a verified property
- If not:
  - Click **Add Property** → choose **Domain** (preferred) or **URL prefix**
  - Follow the verification steps (DNS TXT record OR HTML upload OR HTML meta tag)
  - Shopify docs: [verify Google Search Console](https://help.shopify.com/en/manual/promoting-marketing/seo/submitting-sitemap-google-search-console)

## 2. Submit the sitemap

- In Search Console → **Sitemaps** (left nav)
- Under **Add a new sitemap**, enter: `sitemap.xml`
- Click **Submit**
- You should see the sitemap status change to "Success" within minutes. If it says "Couldn't fetch" — wait 10-15 min and retry.

## 3. Request immediate indexing on 5 priority pages

For each URL below, use **URL Inspection** (top search bar in GSC) → paste URL → click **Request Indexing**:

- `https://leafandbird.com/collections/pdrn-serum`
- `https://leafandbird.com/collections/vegan-pdrn-serum`
- `https://leafandbird.com/collections/tallow-cream`
- `https://leafandbird.com/collections/non-toxic-skincare`
- `https://leafandbird.com/blogs/journal/what-is-pdrn-complete-guide`

Google rate-limits these requests (~10/day per property), so don't try to push all 24 at once — they'll find the rest via the sitemap.

## 4. Check indexation (7-14 days later)

- Coverage report → **Pages** tab
- Confirm all 15 money pages + 9 articles show **"Indexed"** status
- If any show "Discovered — currently not indexed," use URL Inspection → Request Indexing manually on the stuck ones
- If many show "Crawled — not indexed" → that's a content-quality signal Google is flagging; re-check those pages' uniqueness

## 5. Set up performance tracking (optional but recommended)

- **Performance** report → filter by query
- Add the 5 priority queries as saved views:
  - `pdrn serum`
  - `vegan pdrn`
  - `whipped tallow face cream`
  - `non toxic korean skincare`
  - `tallow cream for eczema`
- Use these for the weekly monitoring cadence (see `content/monitoring-playbook.md` after T7.1).

## Bing / Yandex

We already submitted 26 URLs via IndexNow (T6.2, HTTP 202). Bing/Yandex will crawl within hours without any further action from you.

## Done?

Reply "GSC submitted" and I'll continue to P7 (monitoring setup).
