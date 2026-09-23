# JJA Cleaning Services: website redesign proposal

A ground-up rebuild of https://jja-cleaning-service.b12sites.com/ as a fast,
single-page microsite, to pitch to JJA as a Konversly redesign.

Target preview URL: `https://proposals.konversly.com/jja-cleaning/`

## Layout

```
site/            the built site (served under /jja-cleaning/)
src/index.html   page template ({{pic}} placeholders become <picture> tags)
cloudflare/      Pages-level _headers, _redirects, 404.html and robots.txt
scripts/         image, HTML and dist build scripts
```

## Build

```bash
npm install
npm run build     # copy font, pull and optimize the client's photos, write site/index.html
npm run serve     # preview at http://localhost:4173
```

After editing only the copy, run `npm run html`. `site/` is committed, so a
deploy doesn't require a build.

## Deploy (Cloudflare Pages)

Live at **https://proposals.konversly.com/jja-cleaning/**

| Setting | Value |
|---|---|
| Cloudflare account | Brockcdouglas@gmail.com's Account (owns the konversly.com zone) |
| Pages project | `konversly-proposals` (also at konversly-proposals.pages.dev) |
| DNS | `proposals` CNAME to `konversly-proposals.pages.dev`, proxied |

The project is shared by all proposals: each one is a folder, and the root
redirects to konversly.com. The old wildcard DNS record still sends every other
unlisted subdomain to Bluehost.

To redeploy:

```bash
npm run build                 # or just: npm run html (after copy edits)
bash scripts/make-dist.sh     # assembles dist/ with _headers, _redirects, 404, robots
```

Then upload `dist/` with `_tools/deploy.mjs` from the microsites repo, and
create the deployment with the Cloudflare API. Steps 5 and 6 of
`_tools/LAUNCH.md` in that repo cover both. `cloudflare/_headers` pins
`image/avif`, because that deploy script's MIME map has no `.avif` entry.

The preview stays out of search through a `noindex` meta tag, an
`X-Robots-Tag` header, and `robots.txt`.

## What changed vs. the current B12 site

| Area | Current site | Redesign |
|---|---|---|
| Brand | Generic B12 template colors | Palette and bubble-bucket mark from JJA's own flyer and logo |
| Hero | Text list of services | Clear promise, two CTAs, trust points, drag-to-compare before/after |
| Location | "Throughout the region" | Service-area section naming 16 Butler and Sedgwick county towns, echoed in the FAQ, meta and schema |
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
- **Service area:** confirmed from the 316 area code. The page lists 16 towns across Butler and Sedgwick counties.
- **Social links:** the flyer lists @jjacleaning. The Facebook and Instagram URLs are assumed from that handle.
- **Testimonials:** carried over from the current site. Replace them with verified Google reviews if possible.
- **Credentials:** no "licensed" or "insured" claims were added. Add them only if the client can document them.
- **Team photos:** the current site has names only. Real headshots would strengthen the crew section.
- **At launch:** remove the proposal ribbon, the `noindex` tags, `robots.txt` and the `X-Robots-Tag` header, and update the Open Graph and schema URLs to the client's domain.
