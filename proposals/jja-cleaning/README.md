# JJA Cleaning Services: website redesign proposal

A ground-up rebuild of https://jja-cleaning-service.b12sites.com/ as a fast,
single-page microsite, to pitch to JJA as a Konversly redesign.

Target preview URL: `https://proposals.konversly.com/jja-cleaning/`

## Layout

```
site/            deployable static site; upload this folder as-is
src/index.html   page template ({{pic}} placeholders become <picture> tags)
scripts/         build and deploy scripts
```

## Build

```bash
npm install
npm run build     # copy font, pull and optimize the client's photos, write site/index.html
npm run serve     # preview at http://localhost:4173
```

After editing only the copy, run `npm run html`. `site/` is committed, so a
deploy doesn't require a build.

## Deploy to proposals.konversly.com

`proposals.konversly.com` is on Bluehost shared hosting. At build time it
returned a redirect to `/404.html` and had no matching SSL certificate.

1. In cPanel, confirm the `proposals` subdomain exists and note its document root.
2. Run AutoSSL (cPanel > SSL/TLS Status) so the subdomain gets a valid HTTPS cert.
3. Upload `site/` into `<document root>/jja-cleaning/`, either with the cPanel
   File Manager or with the deploy script:

```bash
export KONVERSLY_FTP_HOST=ftp.konversly.com
export KONVERSLY_FTP_USER=...
export KONVERSLY_FTP_PASS=...
export KONVERSLY_FTP_ROOT=/public_html/proposals   # the subdomain's document root
npm run deploy                                      # needs lftp
```

The preview is deliberately kept out of search engines through a `noindex` meta
tag, the `X-Robots-Tag` header in `.htaccess`, and `robots.txt`.

## What changed vs. the current B12 site

| Area | Current site | Redesign |
|---|---|---|
| Brand | Generic B12 template colors | Palette and bubble-bucket mark from JJA's own flyer and logo |
| Hero | Text list of services | Clear promise, two CTAs, trust points, drag-to-compare before/after |
| Location | "Throughout the region" | Augusta & Wichita, KS named in copy, title, meta and schema |
| Services | 15 flat cards | 3 buyer-based groups (Home / Rentals & business / Haul-off & outdoor) |
| Proof | 12 full-resolution images, about 43 MB in total | 3 interactive sliders + lazy gallery with lightbox, AVIF/WebP |
| Conversion | One form at the bottom | Sticky mobile Call / Text / Quote bar, per-service quote buttons, text-first form |
| Recurring work | Not mentioned | Frequency packages from the flyer (daily to monthly) |
| SEO | Title and description only | LocalBusiness + FAQPage schema, Open Graph image, semantic headings |
| Accessibility | Template defaults | Skip link, keyboard slider, labeled form, focus styles, reduced motion |
| Page weight | Photos served at original size, up to 8 MB each | About 140 KB on first load, no framework, one font file |

## Talking points for the pitch

- The quote form opens a pre-written text or email today, with no backend.
  Konversly can wire it to a CRM with instant SMS follow-up as the upsell.
- Every photo is JJA's own work, so the page proves results instead of claiming them.
- The site is fast on a phone signal, and most cleaning leads come from phones.

## Verify with the client before launch

- **Business name:** the flyer and logo say "JJA Cleaning Services", the B12 site says "Service". The redesign uses "Services".
- **Service area:** Augusta and Wichita come from their public listings. Confirm the towns listed in the schema.
- **Social links:** the flyer lists @jjacleaning. The Facebook and Instagram URLs are assumed from that handle.
- **Testimonials:** carried over from the current site. Replace them with verified Google reviews if possible.
- **Credentials:** no "licensed" or "insured" claims were added. Add them only if the client can document them.
- **Team photos:** the current site has names only. Real headshots would strengthen the crew section.
- **At launch:** remove the proposal ribbon, the `noindex` tags and `robots.txt`, and update the Open Graph URLs to the client's domain.
