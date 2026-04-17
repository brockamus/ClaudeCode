# Core Web Vitals — Post-Build Delta Report

**Date:** _<fill in after user runs>_
**Commit at capture:** _<fill in — latest main SHA>_

## Baseline vs Post-Build

See `content/cwv-baseline.md` for pre-build numbers (was not captured before P1 theme edits — user has to run manually since Google anonymous PSI quota was exhausted).

## Capture now

For each URL, run [PageSpeed Insights](https://pagespeed.web.dev/) twice (mobile + desktop) and record the Performance score + LCP + CLS + INP.

### Homepage — `https://leafandbird.com/`

| Device | Performance | LCP | CLS | INP | FCP | TBT |
|---|---|---|---|---|---|---|
| Mobile | | | | | | |
| Desktop | | | | | | |

### Top money page — `https://leafandbird.com/collections/pdrn-serum`

| Device | Performance | LCP | CLS | INP | FCP | TBT |
|---|---|---|---|---|---|---|
| Mobile | | | | | | |
| Desktop | | | | | | |

### Top article — `https://leafandbird.com/blogs/journal/what-is-pdrn-complete-guide`

| Device | Performance | LCP | CLS | INP | FCP | TBT |
|---|---|---|---|---|---|---|
| Mobile | | | | | | |
| Desktop | | | | | | |

## Expected range (for this theme)

The Konversly theme is a third-party skincare theme — it carries some JS bloat. Typical ranges we'd expect:
- Mobile Performance: 40-65 (theme-dependent)
- Desktop Performance: 70-90
- LCP (mobile): 2.5-4.5s (flag if >5s)
- CLS: should be <0.1 (flag otherwise)
- INP: should be <200ms

If any score is significantly below these ranges, follow-up task recommendations:
- Large LCP → compress hero images, lazy-load below-fold
- High CLS → audit for layout shifts (product grid images without explicit dimensions)
- Slow INP → theme carries too much blocking JS; consider deferring third-party scripts

## Red flags to note

_(Any immediate red flags after your capture — large hero images, render-blocking JS, excessive third-party scripts, etc.)_

---

**Re-measurement cadence:** Re-run monthly during P7 monitoring. Sustained regression = theme-level investigation.
