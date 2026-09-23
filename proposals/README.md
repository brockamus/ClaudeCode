# Konversly proposals

Everything served at https://proposals.konversly.com, from the
`konversly-proposals` Cloudflare Pages project.

| Path | What it is |
|---|---|
| `/website/` | Generic website proposal: $500 build plus Hosting, Hosting + Automations, and Growth + SEO plans |
| `/jja-cleaning/` | JJA Cleaning Services redesign concept |
| `/jja-cleaning/proposal` | Short link to JJA's personalized proposal |

## Personalizing the website proposal

The proposal fills itself in from the link:

```
https://proposals.konversly.com/website/?for=Business%20Name&contact=First%20Name&site=/their-folder/
```

| Parameter | Effect |
|---|---|
| `for` | Business name in the header and page title |
| `contact` | "Attn:" line and the sign-off in the acceptance email |
| `site` | Shows a "Preview your new website" card (proposals domain only) |
| `plan` | Preselects `hosting`, `automations` or `seo` |

For a cleaner link, add a line to `_pages/_redirects`, like the JJA one.

Prices, plan names and the reply email live in one block near the bottom of
`website/index.html` (`PRICES`, `PLAN_NAMES`, `CONTACT_EMAIL`).

## Deploy

```bash
bash make-dist.sh   # builds dist/ from every proposal plus _pages/
```

Then upload `dist/` to the Pages project. See `jja-cleaning/README.md` for the
upload steps.
