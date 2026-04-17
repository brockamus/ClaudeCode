# Leaf & Bird SEO Build Notes

## Theme IDs
- **LIVE:** `186309509419` — Konversly-1-5-1-skincare-2 (role: main)
- **BACKUP (pre-SEO build, 2026-04-16):** `186951631147` — "Copy of Konversly-1-5-1-skincare-2" (role: unpublished)
- **Local theme backup:** `theme-backup/` (636 files, pulled 2026-04-16 at commit `55cdf1b`)

### Rollback procedure

If anything goes catastrophic during P1 theme edits:
1. Shopify Admin → Themes → find "Copy of Konversly-1-5-1-skincare-2"
2. Actions → Publish

The backup will become live instantly. Then identify the break and iterate on the unpublished live copy.

## Theme Section Naming (important — customized Konversly, NOT Dawn)

The theme uses non-standard section filenames. When plan tasks reference `main-product.liquid` or similar Dawn-conventional names, the actual files are:
- Product detail section: `sections/shop-product-details.liquid` + `sections/featured-product-details.liquid`
- Collection grid section: `sections/main-collection-product-grid.liquid` (this one matches plan)
- Header: `sections/header.liquid` (duplicate Org + WebSite schema lives here at lines 875 + 900)

Refer to `content/theme-audit-report.md` for the full file:line mapping when doing P1 edits.

## Review App Status

(Populated by Task T0.5.)

## IndexNow Key

(Populated by Task T6.2 — do NOT commit the key to git.)
