# Leaf & Bird SEO + Content Build v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 15 SEO money pages, 9 cornerstone blog articles, full tech SEO remediation, schema coverage, and AI/LLM discoverability infrastructure for the Leaf & Bird Shopify store, positioning it to win organic rankings for vegan PDRN, tallow cream, and crunchy-mom skincare queries.

**Architecture:** Shopify Admin API drives all data changes (products, collections, articles, metafields, pages). One custom Liquid snippet (`lb-seo-schema.liquid`) renders all structured data site-wide. Collection page content is metafield-driven (not `body_html`) for consistency, rollback, and future automation. Blog article images generated via Gemini multimodal using product photos as visual references.

**Tech Stack:** Shopify Admin API (REST, 2024-10), Shopify Liquid, Shopify Metafields, Google Gemini API (Imagen 4.0 + Gemini 2.5 Flash Image), Python 3 (scripts), bash (orchestration), git (version control). No npm packages — project uses standard library only.

**Spec:** [`../specs/2026-04-16-leaf-and-bird-seo-design.md`](../specs/2026-04-16-leaf-and-bird-seo-design.md)

---

## Context for the Executor

You are implementing an SEO and content build for Leaf & Bird, a brand-new Shopify store in the clean-beauty niche. The target audience is "crunchy moms" (health-conscious mothers who avoid synthetic/toxic ingredients). The two hero products are:

1. **Vegan PDRN Brightening Serum** — rare non-salmon-derived PDRN (vegan confirmed by brand owner). Most commercial PDRN is salmon-derived; ours isn't. This is a significant competitive moat.
2. **Whipped Grass-Fed Tallow Creams** (3 scents) — ancestral skincare angle, pasture-raised, chemical-free.

**Before executing any task:** Read the spec linked above end-to-end. It contains the keyword map, module library, voice guidelines, schema strategy, and success metrics. Every content task references the spec's module library — do not re-design.

**Credentials:** The Shopify Admin API token and Gemini API key live in auto-memory (`~/.claude/projects/-Users-skitch/memory/project_leaf_and_bird.md` and `reference_gemini_api.md`). Never commit them to git. Use them from environment variables or ephemeral script files in `/tmp/`.

**Brand voice:**
- PDRN content → clinical/scientific, K-beauty roots, clean-active framing
- Tallow content → warm/ancestral, grass-fed, "what our grandmothers used"
- Crunchy-mom pages → audience-first, ingredient-avoidance, EWG-style reasoning
- Every page gets direct-answer intro sentences for LLM extraction

**Canonical brand identity line** (use in llms.txt, About page, Organization schema, social bios — identical wording):
> "Leaf & Bird is a clean vegan skincare brand making rare non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers."

(Avoid "only" superlatives in public copy until brand owner verifies no competing vegan PDRN product exists.)

---

## File Structure

```
/Users/skitch/ClaudeCode/leaf-and-bird/
├── docs/superpowers/
│   ├── specs/2026-04-16-leaf-and-bird-seo-design.md    [the spec]
│   └── plans/2026-04-16-leaf-and-bird-seo-v1.md        [this plan]
├── scripts/                                             [API helpers, validators]
│   ├── shopify_api.py                                  [shared Shopify client]
│   ├── schema_validator.py                             [JSON-LD validator]
│   ├── gen_image.py                                    [Gemini image generator]
│   ├── audit_theme.py                                  [theme SEO audit]
│   └── content_publisher.py                            [content → metafield publisher]
├── content/                                             [drafted content by page/article]
│   ├── products/                                       [product page rewrites, JSON per SKU]
│   ├── collections/                                    [money page content, JSON per slug]
│   └── articles/                                       [article drafts, markdown per slug]
├── images/                                              [Gemini-generated images]
│   ├── products/
│   ├── collections/
│   └── articles/
├── theme-backup/                                        [local copy of live theme pre-edits]
└── theme-working/                                       [local working copy if needed]

/Users/skitch/claude-code/theme/                         [user's existing theme checkout — do not move]
```

**Shopify-side artifacts** (created via API, not local files):
- `snippets/lb-seo-schema.liquid` (new Liquid snippet in live theme)
- Metafield definitions on Product, Collection, Article resources
- `robots.txt.liquid` template override
- `/llms.txt` + `/llms-full.txt` pages (Shopify Pages with custom templates)

**Commit cadence:** Commit to git after each task. One commit per task. Git user is already configured (Brock). Working tree for this project is `/Users/skitch/ClaudeCode/leaf-and-bird/` inside the `/Users/skitch` root git repo.

---

## Task Map

| Phase | Tasks | Total |
|---|---|---|
| P0 — Preflight | T0.1 – T0.7 | 7 |
| P1 — Foundation (schema + tech SEO) | T1.1 – T1.14 | 14 |
| P2 — Product pages (9 SKUs) | T2.1 – T2.10 | 10 |
| P3 — PDRN money pages | T3.1 – T3.9 | 9 |
| P4 — Tallow + Crunchy-mom money pages | T4.1 – T4.10 | 10 |
| P5 — Blog articles (9) | T5.1 – T5.11 | 11 |
| P6 — Nav + submission | T6.1 – T6.5 | 5 |
| P7 — Monitoring setup | T7.1 – T7.2 | 2 |

**68 total tasks.** Phases execute sequentially; tasks within phases are mostly sequential (some parallelizable — noted per phase).

---

## Phase P0 — Preflight (7 tasks)

### Task T0.1: Verify Shopify API access and pull shop info

**Files:**
- Create: `scripts/shopify_api.py`

- [ ] **Step 1: Read Shopify credentials from auto-memory**

Load the admin token from `~/.claude/projects/-Users-skitch/memory/project_leaf_and_bird.md`. Export to environment:

```bash
export SHOPIFY_SHOP="leaf-and-bird.myshopify.com"
export SHOPIFY_TOKEN="<token from memory file>"
```

- [ ] **Step 2: Create shared Shopify API client**

Create `scripts/shopify_api.py`:

```python
"""Shared Shopify Admin API client for Leaf & Bird SEO project."""
import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error

SHOP = os.environ["SHOPIFY_SHOP"]
TOKEN = os.environ["SHOPIFY_TOKEN"]
API_VERSION = "2024-10"
BASE = f"https://{SHOP}/admin/api/{API_VERSION}"


def _request(method, path, body=None, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code} on {method} {url}: {body_text}")


def get(path, params=None):
    return _request("GET", path, params=params)


def post(path, body):
    return _request("POST", path, body=body)


def put(path, body):
    return _request("PUT", path, body=body)


def delete(path):
    return _request("DELETE", path)


def shop():
    return get("/shop.json")["shop"]


if __name__ == "__main__":
    s = shop()
    print(f"Connected to: {s['name']} ({s['myshopify_domain']})")
    print(f"Plan: {s.get('plan_name')}  |  Currency: {s['currency']}  |  Timezone: {s['iana_timezone']}")
```

- [ ] **Step 3: Run client to verify access**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/shopify_api.py
```

Expected output:
```
Connected to: Leaf and Bird (leaf-and-bird.myshopify.com)
Plan: <plan>  |  Currency: USD  |  Timezone: America/...
```

If 401/403: token is wrong or expired — stop and alert user.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/shopify_api.py
git commit -m "Add Shopify Admin API client for Leaf & Bird project"
```

---

### Task T0.2: Pull live theme files locally for audit

**Files:**
- Create: `scripts/pull_theme.py`
- Create: `theme-backup/` (populated)

- [ ] **Step 1: Write theme-pull script**

Create `scripts/pull_theme.py`:

```python
"""Pull all files from the live Shopify theme to a local directory."""
import os
import sys
import pathlib
import shopify_api

LIVE_THEME_ID = 186309509419  # Konversly-1-5-1-skincare-2 (confirmed live in spec)
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "theme-backup"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assets = shopify_api.get(f"/themes/{LIVE_THEME_ID}/assets.json")["assets"]
    print(f"Found {len(assets)} assets. Downloading...")
    for asset in assets:
        key = asset["key"]
        detail = shopify_api.get(f"/themes/{LIVE_THEME_ID}/assets.json", params={"asset[key]": key})["asset"]
        dest = OUT_DIR / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        if "value" in detail:
            dest.write_text(detail["value"], encoding="utf-8")
        elif "attachment" in detail:
            import base64
            dest.write_bytes(base64.b64decode(detail["attachment"]))
        print(f"  {key}")
    print(f"Done. {len(assets)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the pull**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 pull_theme.py
```

Expected: ~200+ files downloaded to `theme-backup/`, mix of `templates/*.json`, `sections/*.liquid`, `snippets/*.liquid`, `assets/*.css`, etc.

If theme ID is wrong: run `python3 -c "import shopify_api; import json; print(json.dumps([{'id':t['id'],'name':t['name'],'role':t['role']} for t in shopify_api.get('/themes.json')['themes']], indent=2))"` and pick the one with `role: main`. Update `LIVE_THEME_ID` in `pull_theme.py` and re-run.

- [ ] **Step 3: Verify key files are present**

Run:
```bash
ls -la /Users/skitch/ClaudeCode/leaf-and-bird/theme-backup/layout/
ls -la /Users/skitch/ClaudeCode/leaf-and-bird/theme-backup/sections/ | head -30
ls -la /Users/skitch/ClaudeCode/leaf-and-bird/theme-backup/snippets/ | head -30
```

Expected: `layout/theme.liquid` exists; `sections/main-product*.liquid` and `sections/main-collection*.liquid` exist.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/pull_theme.py ClaudeCode/leaf-and-bird/theme-backup/
git commit -m "Pull live Shopify theme to local backup for SEO audit"
```

---

### Task T0.3: Create unpublished theme backup in Shopify (safety net)

**Files:** (no local files — uses Admin API)

- [ ] **Step 1: Duplicate live theme via Shopify Admin UI (manual user action)**

⚠️ The Shopify REST API does NOT expose a "duplicate theme" endpoint. The safest duplicate method is manual.

**Instruct the user:**
> "Open Shopify Admin → Online Store → Themes → find the live theme (Konversly-1-5-1-skincare-2) → click Actions → Duplicate. Rename the duplicate to `BACKUP-before-seo-build-2026-04-16`. Report back the new theme ID."

- [ ] **Step 2: Verify the new backup theme exists via API**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
import json
themes = s.get('/themes.json')['themes']
for t in themes:
    print(f\"  id={t['id']}  role={t['role']}  name={t['name']}\")"
```

Expected: an unpublished theme named `BACKUP-before-seo-build-2026-04-16` appears in the list.

- [ ] **Step 3: Record the backup theme ID in project notes**

Append to `/Users/skitch/ClaudeCode/leaf-and-bird/NOTES.md` (create if missing):

```markdown
# Leaf & Bird SEO Build Notes

## Theme IDs
- LIVE: 186309509419 — Konversly-1-5-1-skincare-2
- BACKUP (pre-SEO): <id from step 2>
- Local theme backup: theme-backup/
```

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/NOTES.md
git commit -m "Record Shopify theme backup IDs pre-SEO build"
```

---

### Task T0.4: Audit live theme for SEO issues

**Files:**
- Create: `scripts/audit_theme.py`
- Create: `content/theme-audit-report.md`

- [ ] **Step 1: Write audit script**

Create `scripts/audit_theme.py`:

```python
"""Audit the locally-backed-up theme for common SEO issues."""
import pathlib
import re
import json

THEME_DIR = pathlib.Path(__file__).resolve().parent.parent / "theme-backup"


def read(path):
    p = THEME_DIR / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def find_patterns(pattern, file_glob, flags=0):
    hits = []
    for path in THEME_DIR.rglob(file_glob):
        rel = path.relative_to(THEME_DIR)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.finditer(pattern, text, flags):
            line_no = text[: m.start()].count("\n") + 1
            hits.append((str(rel), line_no, m.group(0)[:200]))
    return hits


def main():
    report = ["# Leaf & Bird Theme SEO Audit\n"]

    report.append("## 1. Organization schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"Organization"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 2. Product schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"Product"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 3. WebSite schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"WebSite"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 4. H1 usages in theme")
    for hit in find_patterns(r"<h1[\s>]", "*.liquid", re.IGNORECASE):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 5. Logo-in-header patterns (possible H1 abuse)")
    for hit in find_patterns(r"header.*logo|logo.*h1|h1.*logo", "*.liquid", re.IGNORECASE | re.DOTALL):
        report.append(f"- `{hit[0]}:{hit[1]}`")
    report.append("")

    report.append("## 6. OG image tags (check for http:// instead of https://)")
    for hit in find_patterns(r'property="og:image"[^>]*http://', "*.liquid"):
        report.append(f"- HTTP OG image: `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 7. Canonical tag references")
    for hit in find_patterns(r'rel="canonical"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 8. robots meta / noindex")
    for hit in find_patterns(r'name="robots"|noindex', "*.liquid", re.IGNORECASE):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 9. Image alt attribute usage")
    imgs_with_alt = find_patterns(r"<img[^>]*\balt=", "*.liquid", re.IGNORECASE)
    imgs_all = find_patterns(r"<img\b", "*.liquid", re.IGNORECASE)
    report.append(f"- Total `<img` tags: {len(imgs_all)}")
    report.append(f"- With `alt=`: {len(imgs_with_alt)}")
    report.append(f"- Missing alt: {len(imgs_all) - len(imgs_with_alt)}")
    report.append("")

    report.append("## 10. Meta description usages")
    for hit in find_patterns(r'name="description"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 11. Existing FAQPage schema")
    for hit in find_patterns(r'"@type"\s*:\s*"FAQPage"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    out = pathlib.Path(__file__).resolve().parent.parent / "content" / "theme-audit-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Report written to {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the audit**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 audit_theme.py
```

Expected: `content/theme-audit-report.md` populated with findings across 11 categories.

- [ ] **Step 3: Review the report, classify findings into a fix list**

Read `content/theme-audit-report.md`. For each category, classify each hit as one of:
- **FIX** — we will edit the theme to fix this
- **KEEP** — existing behavior is correct
- **INVESTIGATE** — need to load the live page to confirm behavior

Append a "Fix List" section at the bottom of the report with explicit file:line entries to be edited in Phase P1.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/audit_theme.py ClaudeCode/leaf-and-bird/content/theme-audit-report.md
git commit -m "Audit Leaf & Bird live theme for SEO issues"
```

---

### Task T0.5: Verify review app status (for AggregateRating schema)

**Files:** (no local files)

- [ ] **Step 1: Check installed apps via Shopify API**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
import json
# Check metafields namespace for common review apps
resp = s.get('/products.json', params={'limit': 1, 'fields': 'id,metafields'})
print(json.dumps(resp, indent=2)[:2000])
# Also list metafield definitions
mfdef = s.get('/metafield_definitions.json', params={'owner_type': 'PRODUCT'})
print('Metafield definitions on product:')
for d in mfdef.get('metafield_definitions', []):
    print(f\"  {d['namespace']}.{d['key']} ({d['type']['name']})\")"
```

- [ ] **Step 2: Check theme for known review app snippets**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && grep -rli "loox\|judge\.me\|yotpo\|stamped\|okendo\|reviews" theme-backup/ 2>/dev/null | head -20
```

Expected: either hits for one of those apps (Loox/Judge.me/Yotpo/Stamped/Okendo) or empty.

- [ ] **Step 3: Record review app status in NOTES.md**

Append to `/Users/skitch/ClaudeCode/leaf-and-bird/NOTES.md`:

```markdown
## Review App
- App detected: <name or "none">
- Location in theme: <file references or "n/a">
- AggregateRating schema: <"emits" / "does not emit" / "n/a">
- Decision: If a review app is present, emit AggregateRating from lb-seo-schema.liquid ONLY when the app has NOT already emitted it (avoid duplication). Detect by reading from a per-product metafield we populate manually, OR by checking if the app's schema node is already rendered. If no app, skip AggregateRating entirely until reviews exist.
```

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/NOTES.md
git commit -m "Record review app status for AggregateRating decision"
```

---

### Task T0.6: Create Shopify metafield definitions

**Files:**
- Create: `scripts/create_metafields.py`

- [ ] **Step 1: Write the metafield creation script**

Create `scripts/create_metafields.py`:

```python
"""Create metafield definitions for Leaf & Bird SEO content storage."""
import sys
import shopify_api


DEFINITIONS = [
    # Collection metafields (money page content)
    {"owner": "COLLECTION", "namespace": "seo", "key": "h1", "name": "SEO H1",
     "type": "single_line_text_field", "description": "Collection page H1 (overrides title)."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "intro", "name": "SEO intro",
     "type": "multi_line_text_field", "description": "Hero paragraph (40-65 words)."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "body_modules", "name": "SEO body modules",
     "type": "json", "description": "Ordered array of {type, content} modules for diverse page rendering."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} — source of truth for FAQPage schema."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "meta_title", "name": "Meta title",
     "type": "single_line_text_field", "description": "SEO meta title override."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "meta_description", "name": "Meta description",
     "type": "multi_line_text_field", "description": "SEO meta description override."},
    {"owner": "COLLECTION", "namespace": "seo", "key": "primary_keyword", "name": "Primary keyword",
     "type": "single_line_text_field", "description": "Primary target keyword for this page."},
    # Product metafields (FAQ + free-from)
    {"owner": "PRODUCT", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} — source of truth for product FAQPage schema."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "free_from", "name": "Free from list",
     "type": "json", "description": "Array of strings (e.g., ['parabens','sulfates','fragrance'])."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "meta_title", "name": "Meta title",
     "type": "single_line_text_field", "description": "SEO meta title override."},
    {"owner": "PRODUCT", "namespace": "seo", "key": "meta_description", "name": "Meta description",
     "type": "multi_line_text_field", "description": "SEO meta description override."},
    # Article metafields
    {"owner": "ARTICLE", "namespace": "seo", "key": "faq_json", "name": "SEO FAQ JSON",
     "type": "json", "description": "Array of {question, answer} for article FAQPage schema."},
    {"owner": "ARTICLE", "namespace": "seo", "key": "primary_keyword", "name": "Primary keyword",
     "type": "single_line_text_field", "description": "Primary target keyword for this article."},
]


def main():
    for d in DEFINITIONS:
        body = {
            "metafield_definition": {
                "namespace": d["namespace"],
                "key": d["key"],
                "name": d["name"],
                "type": d["type"],
                "owner_type": d["owner"],
                "description": d["description"],
            }
        }
        try:
            resp = shopify_api.post("/metafield_definitions.json", body)
            print(f"OK   {d['owner']}.{d['namespace']}.{d['key']}")
        except RuntimeError as e:
            if "taken" in str(e).lower() or "already" in str(e).lower() or "422" in str(e):
                print(f"SKIP {d['owner']}.{d['namespace']}.{d['key']} (exists)")
            else:
                print(f"FAIL {d['owner']}.{d['namespace']}.{d['key']}: {e}")
                sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 create_metafields.py
```

Expected: 13 definitions created or skipped. No FAIL lines.

- [ ] **Step 3: Verify in Shopify Admin**

Instruct user to confirm in Shopify Admin → Settings → Custom data → Products / Collections / Articles → the `seo.*` namespace appears.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/create_metafields.py
git commit -m "Create Shopify metafield definitions for SEO content storage"
```

---

### Task T0.7: Set up .gitignore + project README

**Files:**
- Create: `.gitignore` (at project root of `leaf-and-bird/`)
- Create: `README.md`

- [ ] **Step 1: Write .gitignore**

Create `/Users/skitch/ClaudeCode/leaf-and-bird/.gitignore`:

```
# Python
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
.env.*

# OS
.DS_Store

# Temporary
/tmp/
*.tmp

# Images (too large for git; they're on Shopify CDN after publishing)
images/products/*
images/collections/*
images/articles/*
!images/**/.gitkeep

# Content drafts (optional — keep or remove per preference; keeping for now)
# content/drafts/

# Theme backup (large, optional to track)
# theme-backup/
```

- [ ] **Step 2: Add .gitkeep placeholders so image dirs are tracked even when empty**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && \
  mkdir -p images/products images/collections images/articles && \
  touch images/products/.gitkeep images/collections/.gitkeep images/articles/.gitkeep
```

- [ ] **Step 3: Write a short README**

Create `/Users/skitch/ClaudeCode/leaf-and-bird/README.md`:

```markdown
# Leaf & Bird SEO + Content Build

SEO money pages, blog articles, and tech SEO for leaf-and-bird.com (Shopify).

- Spec: `docs/superpowers/specs/2026-04-16-leaf-and-bird-seo-design.md`
- Plan: `docs/superpowers/plans/2026-04-16-leaf-and-bird-seo-v1.md`
- Scripts: `scripts/` — Shopify API client, theme audit, schema validator, image generator
- Content drafts: `content/`
- Theme backup: `theme-backup/` (pulled from live Shopify theme)

## Environment

Credentials in auto-memory (`~/.claude/projects/-Users-skitch/memory/project_leaf_and_bird.md`).
Export before running any script:

```sh
export SHOPIFY_SHOP="leaf-and-bird.myshopify.com"
export SHOPIFY_TOKEN="<from memory>"
export GEMINI_API_KEY="<from memory>"
```
```

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/.gitignore ClaudeCode/leaf-and-bird/README.md ClaudeCode/leaf-and-bird/images/
git commit -m "Add .gitignore, README, and image directory scaffolding"
```

---

## Phase P1 — Foundation: Schema Snippet + Tech SEO Fixes (14 tasks)

### Task T1.1: Write `lb-seo-schema.liquid` snippet (TDD — failing test first)

**Files:**
- Create: `scripts/schema_validator.py`
- Create: `content/schema-fixtures/collection_page.json`
- Test: `scripts/test_schema.py`

- [ ] **Step 1: Write a failing schema-validation test**

Create `scripts/schema_validator.py`:

```python
"""Validate JSON-LD schema output against schema.org conventions."""
import json
import re
import sys


REQUIRED_GRAPH_TYPES_COLLECTION = {"Organization", "WebSite", "BreadcrumbList", "CollectionPage"}
REQUIRED_GRAPH_TYPES_PRODUCT = {"Organization", "WebSite", "BreadcrumbList", "Product"}
REQUIRED_GRAPH_TYPES_ARTICLE = {"Organization", "WebSite", "BreadcrumbList", "Article"}


def extract_jsonld(html):
    """Extract all JSON-LD blocks from a page of HTML."""
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL,
    )
    parsed = []
    for b in blocks:
        try:
            parsed.append(json.loads(b))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON-LD: {e}\n{b[:300]}")
    return parsed


def assert_valid_graph(jsonld, required_types):
    if "@graph" not in jsonld:
        raise AssertionError(f"JSON-LD missing @graph node")
    graph = jsonld["@graph"]
    types = {n.get("@type") for n in graph if isinstance(n.get("@type"), str)}
    types.update(t for n in graph if isinstance(n.get("@type"), list) for t in n["@type"])
    missing = required_types - types
    if missing:
        raise AssertionError(f"Graph missing required types: {missing}. Present: {types}")
    for n in graph:
        if "@id" not in n and n.get("@type") not in ("BreadcrumbList",):
            raise AssertionError(f"Node {n.get('@type')} missing @id for graph cross-referencing")


def validate_collection_page(html):
    blocks = extract_jsonld(html)
    # Find the single @graph block
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_COLLECTION)
    return True


def validate_product_page(html):
    blocks = extract_jsonld(html)
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_PRODUCT)
    return True


def validate_article_page(html):
    blocks = extract_jsonld(html)
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_ARTICLE)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python schema_validator.py <collection|product|article> <url_or_file>")
        sys.exit(2)
    kind = sys.argv[1]
    src = sys.argv[2]
    if src.startswith("http"):
        import urllib.request
        html = urllib.request.urlopen(src).read().decode("utf-8", errors="replace")
    else:
        html = open(src, encoding="utf-8").read()
    if kind == "collection":
        validate_collection_page(html)
    elif kind == "product":
        validate_product_page(html)
    elif kind == "article":
        validate_article_page(html)
    print(f"OK: {src} passes {kind} schema validation.")
```

Create `scripts/test_schema.py`:

```python
"""Tests for the schema validator — run before writing the Liquid snippet."""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema_validator import extract_jsonld, assert_valid_graph, validate_collection_page


def test_extract_jsonld_finds_blocks():
    html = '''<html><head>
    <script type="application/ld+json">{"@type":"Organization","name":"x"}</script>
    </head></html>'''
    blocks = extract_jsonld(html)
    assert len(blocks) == 1
    assert blocks[0]["name"] == "x"


def test_assert_valid_graph_passes_minimum():
    g = {"@graph": [
        {"@type": "Organization", "@id": "#org"},
        {"@type": "WebSite", "@id": "#site"},
        {"@type": "BreadcrumbList"},
        {"@type": "CollectionPage", "@id": "#page"},
    ]}
    assert_valid_graph(g, {"Organization", "WebSite", "BreadcrumbList", "CollectionPage"})


def test_assert_valid_graph_fails_missing_type():
    g = {"@graph": [{"@type": "Organization", "@id": "#org"}]}
    try:
        assert_valid_graph(g, {"Organization", "WebSite"})
    except AssertionError as e:
        assert "WebSite" in str(e)
        return
    raise AssertionError("should have raised")


def test_validate_collection_page_rejects_empty():
    try:
        validate_collection_page("<html></html>")
    except AssertionError:
        return
    raise AssertionError("should have raised")


if __name__ == "__main__":
    test_extract_jsonld_finds_blocks()
    test_assert_valid_graph_passes_minimum()
    test_assert_valid_graph_fails_missing_type()
    test_validate_collection_page_rejects_empty()
    print("All schema validator tests passed.")
```

- [ ] **Step 2: Run the tests — verify they pass (validator correctness)**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 test_schema.py
```

Expected: `All schema validator tests passed.`

- [ ] **Step 3: Write the Liquid snippet file locally**

Create `/Users/skitch/ClaudeCode/leaf-and-bird/theme-working/snippets/lb-seo-schema.liquid`:

```liquid
{%- comment -%}
  Leaf & Bird SEO Schema Snippet
  Renders schema.org JSON-LD as a single @graph object per page.
  Reads FAQ data from `seo.faq_json` metafield (Product, Collection, Article).
  Included once from layout/theme.liquid.
{%- endcomment -%}

{%- assign page_url = canonical_url | default: request.origin | append: request.path -%}
{%- assign site_name = shop.name -%}
{%- assign brand_desc = 'Leaf & Bird is a clean vegan skincare brand making rare non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers.' -%}
{%- assign logo_url = shop.brand.logo.image | image_url: width: 600 | default: shop.brand.square_logo.image | image_url: width: 600 -%}

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "{{ shop.url }}#org",
      "name": {{ site_name | json }},
      "url": "{{ shop.url }}",
      "logo": {{ logo_url | json }},
      "description": {{ brand_desc | json }},
      "sameAs": [
        {%- if settings.social_instagram_link != blank %}{{ settings.social_instagram_link | json }}{% endif -%}
        {%- if settings.social_tiktok_link != blank %},{{ settings.social_tiktok_link | json }}{% endif -%}
        {%- if settings.social_facebook_link != blank %},{{ settings.social_facebook_link | json }}{% endif -%}
      ]
    },
    {
      "@type": "WebSite",
      "@id": "{{ shop.url }}#site",
      "url": "{{ shop.url }}",
      "name": {{ site_name | json }},
      "publisher": { "@id": "{{ shop.url }}#org" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "{{ shop.url }}/search?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    }

    {%- comment -%} BreadcrumbList {%- endcomment -%}
    ,{
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "{{ shop.url }}" }
        {%- if template contains 'collection' and collection -%}
        ,{ "@type": "ListItem", "position": 2, "name": {{ collection.title | json }}, "item": "{{ shop.url }}{{ collection.url }}" }
        {%- elsif template contains 'product' and product -%}
        ,{ "@type": "ListItem", "position": 2, "name": {{ product.title | json }}, "item": "{{ shop.url }}{{ product.url }}" }
        {%- elsif template contains 'article' and article -%}
        ,{ "@type": "ListItem", "position": 2, "name": {{ blog.title | json }}, "item": "{{ shop.url }}/blogs/{{ blog.handle }}" }
        ,{ "@type": "ListItem", "position": 3, "name": {{ article.title | json }}, "item": "{{ shop.url }}{{ article.url }}" }
        {%- endif -%}
      ]
    }

    {%- comment -%} CollectionPage + ItemList {%- endcomment -%}
    {%- if template contains 'collection' and collection -%}
    ,{
      "@type": "CollectionPage",
      "@id": "{{ page_url }}#page",
      "url": "{{ page_url }}",
      "name": {{ collection.metafields.seo.h1 | default: collection.title | json }},
      "description": {{ collection.metafields.seo.meta_description | default: collection.description | strip_html | truncate: 300 | json }},
      "isPartOf": { "@id": "{{ shop.url }}#site" },
      "about": { "@id": "{{ shop.url }}#org" },
      "mainEntity": {
        "@type": "ItemList",
        "itemListElement": [
          {%- for p in collection.products limit: 12 -%}
          {%- unless forloop.first %},{% endunless -%}
          {
            "@type": "ListItem",
            "position": {{ forloop.index }},
            "url": "{{ shop.url }}{{ p.url }}",
            "name": {{ p.title | json }},
            "image": {{ p.featured_image | image_url: width: 800 | prepend: 'https:' | json }},
            "offers": {
              "@type": "Offer",
              "price": "{{ p.price | money_without_currency | remove: ',' }}",
              "priceCurrency": "{{ cart.currency.iso_code }}",
              "availability": "{% if p.available %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}"
            }
          }
          {%- endfor -%}
        ]
      }
    }
    {%- endif -%}

    {%- comment -%} Product schema {%- endcomment -%}
    {%- if template contains 'product' and product -%}
    ,{
      "@type": "Product",
      "@id": "{{ page_url }}#product",
      "name": {{ product.title | json }},
      "description": {{ product.description | strip_html | truncate: 500 | json }},
      "image": {{ product.featured_image | image_url: width: 1200 | prepend: 'https:' | json }},
      "sku": {{ product.selected_or_first_available_variant.sku | json }},
      "brand": { "@id": "{{ shop.url }}#org" },
      "offers": {
        "@type": "Offer",
        "url": "{{ page_url }}",
        "price": "{{ product.selected_or_first_available_variant.price | money_without_currency | remove: ',' }}",
        "priceCurrency": "{{ cart.currency.iso_code }}",
        "availability": "{% if product.available %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}"
      }
    }
    {%- endif -%}

    {%- comment -%} Article schema {%- endcomment -%}
    {%- if template contains 'article' and article -%}
    ,{
      "@type": "Article",
      "@id": "{{ page_url }}#article",
      "headline": {{ article.title | json }},
      "image": {{ article.image | image_url: width: 1200 | prepend: 'https:' | json }},
      "datePublished": {{ article.published_at | date: '%Y-%m-%dT%H:%M:%S%z' | json }},
      "dateModified": {{ article.updated_at | date: '%Y-%m-%dT%H:%M:%S%z' | json }},
      "author": {
        "@type": "Person",
        "name": {{ article.author | default: 'Leaf & Bird' | json }}
      },
      "publisher": { "@id": "{{ shop.url }}#org" },
      "mainEntityOfPage": "{{ page_url }}"
    }
    {%- endif -%}

    {%- comment -%} FAQPage — reads from metafield seo.faq_json on the current resource {%- endcomment -%}
    {%- assign faq_source = nil -%}
    {%- if template contains 'collection' and collection.metafields.seo.faq_json -%}
      {%- assign faq_source = collection.metafields.seo.faq_json.value -%}
    {%- elsif template contains 'product' and product.metafields.seo.faq_json -%}
      {%- assign faq_source = product.metafields.seo.faq_json.value -%}
    {%- elsif template contains 'article' and article.metafields.seo.faq_json -%}
      {%- assign faq_source = article.metafields.seo.faq_json.value -%}
    {%- endif -%}
    {%- if faq_source and faq_source.size > 0 -%}
    ,{
      "@type": "FAQPage",
      "@id": "{{ page_url }}#faq",
      "mainEntity": [
        {%- for qa in faq_source -%}
        {%- unless forloop.first %},{% endunless -%}
        {
          "@type": "Question",
          "name": {{ qa.question | json }},
          "acceptedAnswer": {
            "@type": "Answer",
            "text": {{ qa.answer | json }}
          }
        }
        {%- endfor -%}
      ]
    }
    {%- endif -%}
  ]
}
</script>
```

- [ ] **Step 4: Commit the snippet (local file + test infra)**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/schema_validator.py ClaudeCode/leaf-and-bird/scripts/test_schema.py ClaudeCode/leaf-and-bird/theme-working/snippets/lb-seo-schema.liquid
git commit -m "Add lb-seo-schema.liquid snippet + JSON-LD validator"
```

---

### Task T1.2: Upload snippet to live theme + include in theme.liquid

**Files:**
- Create: `scripts/upload_asset.py`
- Modify: live theme `layout/theme.liquid` (via API)

- [ ] **Step 1: Write the upload helper**

Create `scripts/upload_asset.py`:

```python
"""Upload a local file to the live Shopify theme."""
import sys
import pathlib
import shopify_api

LIVE_THEME_ID = 186309509419


def upload(local_path, asset_key):
    content = pathlib.Path(local_path).read_text(encoding="utf-8")
    body = {"asset": {"key": asset_key, "value": content}}
    resp = shopify_api.put(f"/themes/{LIVE_THEME_ID}/assets.json", body)
    print(f"Uploaded {local_path} → {asset_key}")
    return resp


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python upload_asset.py <local_file> <asset_key>")
        sys.exit(2)
    upload(sys.argv[1], sys.argv[2])
```

- [ ] **Step 2: Upload the snippet**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/snippets/lb-seo-schema.liquid snippets/lb-seo-schema.liquid
```

Expected: `Uploaded ... → snippets/lb-seo-schema.liquid`

- [ ] **Step 3: Include snippet in theme.liquid**

Read `theme-backup/layout/theme.liquid` to find a safe insertion point just before `</head>`.

Copy the file to `theme-working/layout/theme.liquid` and insert this line immediately before `</head>`:

```liquid
  {% render 'lb-seo-schema' %}
```

Upload:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/layout/theme.liquid layout/theme.liquid
```

- [ ] **Step 4: Verify by loading a live page**

Run:
```bash
curl -s https://leaf-and-bird.com/collections/all | python3 -c "
import sys, re, json
html = sys.stdin.read()
blocks = re.findall(r'<script[^>]*type=\"application/ld\\+json\"[^>]*>\\s*(.*?)\\s*</script>', html, flags=re.DOTALL)
print(f'JSON-LD blocks found: {len(blocks)}')
for i, b in enumerate(blocks):
    try:
        d = json.loads(b)
        print(f'  Block {i}: {list(d.keys())}')
    except Exception as e:
        print(f'  Block {i}: INVALID JSON ({e})')
"
```

Expected: at least 1 block with `@graph` key present. If 0, snippet didn't load — check theme.liquid edit.

- [ ] **Step 5: Run validator against live collection page**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 schema_validator.py collection https://leaf-and-bird.com/collections/all
```

Expected: `OK: ...passes collection schema validation.`

If it fails, iterate on the snippet locally → re-upload → re-test.

- [ ] **Step 6: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/upload_asset.py ClaudeCode/leaf-and-bird/theme-working/layout/theme.liquid
git commit -m "Install lb-seo-schema.liquid snippet in live theme layout"
```

---

### Task T1.3: Remove duplicate Organization schema from theme

**Files:**
- Modify: `theme-working/<files from audit report §1>.liquid`

- [ ] **Step 1: Open audit report**

Read `content/theme-audit-report.md` §1 ("Organization schema occurrences"). Identify any hits OTHER than our new `snippets/lb-seo-schema.liquid`.

- [ ] **Step 2: For each existing Organization block, remove or comment it**

For each file listed (example: `sections/header.liquid:NN`), copy the backup file to `theme-working/` if not already there. Remove the entire `<script type="application/ld+json">...Organization...</script>` block (or wrap it in `{% comment %}...{% endcomment %}` to preserve history).

- [ ] **Step 3: Upload each modified file**

Run for each file:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/<path> <path>
```

- [ ] **Step 4: Verify — curl homepage and count Organization mentions**

Run:
```bash
curl -s https://leaf-and-bird.com/ | grep -c '"@type": "Organization"'
```

Expected: `1` (only our snippet's occurrence).

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/
git commit -m "Remove duplicate Organization schema from theme"
```

---

### Task T1.4: Remove duplicate Product schema from theme

**Files:**
- Modify: `theme-working/sections/main-product*.liquid` (confirmed via audit)

- [ ] **Step 1: Identify the duplicate**

From audit report §2, find the existing Product schema (commonly in `sections/main-product.liquid` via `{% schema %}`-unrelated inline JSON-LD, or `snippets/product-json-ld.liquid`).

- [ ] **Step 2: Remove it**

Open the file in `theme-working/`. Find the `<script type="application/ld+json">...Product...</script>` block and delete (or comment out).

Upload:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/sections/main-product.liquid sections/main-product.liquid
```

- [ ] **Step 3: Verify on a live product page**

Run:
```bash
curl -s https://leaf-and-bird.com/products/pdrn-brightening-serum | grep -c '"@type": "Product"'
```

Expected: `1` (only our snippet).

- [ ] **Step 4: Full validator run**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 schema_validator.py product https://leaf-and-bird.com/products/pdrn-brightening-serum
```

Expected: OK pass.

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/
git commit -m "Remove duplicate Product schema from theme"
```

---

### Task T1.5: Fix logo-as-H1 (demote logo to non-H1 element)

**Files:**
- Modify: `theme-working/sections/header.liquid` (or equivalent from audit §5)

- [ ] **Step 1: Identify the logo H1**

From audit §4 + §5, locate `<h1>` wrapping logo in header. Common pattern:

```liquid
<h1 class="site-logo">{% render 'site-logo' %}</h1>
```

- [ ] **Step 2: Demote to `<div>` or `<span>` while preserving class names**

Change `<h1 class="site-logo">` → `<div class="site-logo">` (and closing tag). If theme uses Liquid conditionals like `{% if template == 'index' %}<h1>{% else %}<div>{% endif %}`, change both branches to non-H1.

- [ ] **Step 3: Upload**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/sections/header.liquid sections/header.liquid
```

- [ ] **Step 4: Verify homepage**

Run:
```bash
curl -s https://leaf-and-bird.com/ | grep -oE '<h1[^>]*>[^<]*</h1>' | head -5
```

Expected: Either no H1 on homepage, or an H1 that is the intended hero heading (not the logo). Homepage H1 should be set by whichever hero section is visible.

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/sections/header.liquid
git commit -m "Demote site logo from H1 to preserve page-level H1 hierarchy"
```

---

### Task T1.6: Fix OG image protocol (HTTP → HTTPS)

**Files:**
- Modify: `theme-working/snippets/meta-tags.liquid` or `theme-working/layout/theme.liquid` (from audit §6)

- [ ] **Step 1: Find the OG image output**

Common pattern to find:

```liquid
<meta property="og:image" content="http:{{ page_image | image_url: width: 1200 }}">
```

Replace `http:` with `https:` (or remove the prefix entirely — Shopify returns protocol-relative URLs):

```liquid
<meta property="og:image" content="https:{{ page_image | image_url: width: 1200 }}">
```

- [ ] **Step 2: Upload**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/<file> <file>
```

- [ ] **Step 3: Verify**

Run:
```bash
curl -s https://leaf-and-bird.com/ | grep -E 'property="og:image"'
```

Expected: `content="https://...`, not `content="http://...`.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/
git commit -m "Force HTTPS on OG image URLs"
```

---

### Task T1.7: Add noindex on internal search results page

**Files:**
- Modify: `theme-working/templates/search.json` or `theme-working/sections/main-search.liquid`

- [ ] **Step 1: Check current behavior**

Run:
```bash
curl -sI "https://leaf-and-bird.com/search?q=pdrn" | grep -i "x-robots"
curl -s "https://leaf-and-bird.com/search?q=pdrn" | grep -E 'name="robots"'
```

If neither shows `noindex`, add it.

- [ ] **Step 2: Add robots meta via theme.liquid conditional**

Edit `theme-working/layout/theme.liquid`. Find the `<head>` block and add (before our schema snippet render):

```liquid
{%- if template contains 'search' -%}
<meta name="robots" content="noindex, follow">
{%- endif -%}
```

Also consider adding for `template contains 'customers'` (login/account pages).

- [ ] **Step 3: Upload and verify**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/layout/theme.liquid layout/theme.liquid
curl -s "https://leaf-and-bird.com/search?q=pdrn" | grep -E 'name="robots"'
```

Expected: `<meta name="robots" content="noindex, follow">`.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/layout/theme.liquid
git commit -m "Add noindex on internal search results"
```

---

### Task T1.8: Update robots.txt to allow AI crawlers

**Files:**
- Create: `theme-working/templates/robots.txt.liquid`

- [ ] **Step 1: Create the custom robots.txt template**

Shopify allows customizing `robots.txt` via `templates/robots.txt.liquid`. Create it with AI crawler allow rules prepended to the default rules:

```liquid
# LEAF & BIRD custom robots.txt — AI crawler allow + Shopify defaults
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: AppleBot-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: Diffbot
Allow: /

# --- Begin Shopify default rules ---
{%- for group in robots.default_groups -%}
{%- for rule in group.rules -%}
{{ rule }}
{%- endfor -%}
{%- if group.sitemap != blank -%}
{{ group.sitemap }}
{%- endif -%}
{%- endfor -%}
```

- [ ] **Step 2: Upload**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/templates/robots.txt.liquid templates/robots.txt.liquid
```

- [ ] **Step 3: Verify**

Run:
```bash
curl -s https://leaf-and-bird.com/robots.txt
```

Expected: AI crawler allow rules at top, Shopify default rules below.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/templates/robots.txt.liquid
git commit -m "Customize robots.txt to explicitly allow AI crawlers"
```

---

### Task T1.9: Modify collection section to render metafield-driven content

**Files:**
- Modify: `theme-working/sections/main-collection-product-grid.liquid` (or equivalent per theme)

- [ ] **Step 1: Identify the collection grid section**

From `theme-backup/`, find the section whose schema name contains "collection" and which renders the product grid. Common names: `main-collection-product-grid.liquid`, `main-collection.liquid`, `collection-products.liquid`.

- [ ] **Step 2: Add metafield-rendering blocks**

Edit the section to render `collection.metafields.seo.*` before AND after the product grid. Structure:

```liquid
{%- comment -%} === Leaf & Bird SEO metafield content (above grid) === {%- endcomment -%}
{%- if collection.metafields.seo.intro -%}
  <div class="lb-seo-intro page-width">
    {%- if collection.metafields.seo.h1 -%}
      <h1>{{ collection.metafields.seo.h1 }}</h1>
    {%- else -%}
      <h1>{{ collection.title }}</h1>
    {%- endif -%}
    <div class="lb-seo-intro__text rte">{{ collection.metafields.seo.intro }}</div>
  </div>
{%- endif -%}

{%- comment -%} (existing product grid content stays here) {%- endcomment -%}

{%- comment -%} === Below grid: body modules + FAQ === {%- endcomment -%}
{%- if collection.metafields.seo.body_modules -%}
  <div class="lb-seo-body page-width">
    {%- for module in collection.metafields.seo.body_modules.value -%}
      <section class="lb-module lb-module--{{ module.type }}">
        {%- if module.heading %}<h2>{{ module.heading }}</h2>{% endif -%}
        <div class="rte">{{ module.html }}</div>
      </section>
    {%- endfor -%}
  </div>
{%- endif -%}

{%- if collection.metafields.seo.faq_json -%}
  <div class="lb-seo-faq page-width">
    <h2>Frequently Asked Questions</h2>
    {%- for qa in collection.metafields.seo.faq_json.value -%}
      <details class="lb-faq-item">
        <summary><strong>{{ qa.question }}</strong></summary>
        <div class="rte">{{ qa.answer }}</div>
      </details>
    {%- endfor -%}
  </div>
{%- endif -%}
```

- [ ] **Step 3: Upload**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/sections/main-collection-product-grid.liquid sections/main-collection-product-grid.liquid
```

Adjust filename to match actual section name.

- [ ] **Step 4: Seed a test metafield on one collection to confirm rendering**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
# Use the existing 'featured' collection as a harmless test target
cid = 525366133035
payload = {'metafield': {'namespace':'seo','key':'intro','type':'multi_line_text_field','value':'TEST intro paragraph — delete me.'}}
print(s.post(f'/collections/{cid}/metafields.json', payload))"
```

Load `https://leaf-and-bird.com/collections/featured` and confirm the text appears. Then clean up:

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
cid = 525366133035
mfs = s.get(f'/collections/{cid}/metafields.json')['metafields']
for m in mfs:
    if m['namespace']=='seo' and m['key']=='intro':
        s.delete(f'/metafields/{m[\"id\"]}.json')
        print('deleted test metafield')"
```

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/sections/
git commit -m "Render SEO metafields in collection section (intro, modules, FAQ)"
```

---

### Task T1.10: Create `/llms.txt` via Shopify Page + template

**Files:**
- Create: `theme-working/templates/page.llms-txt.liquid` (plain-text page template)
- Create: Shopify Page `llms-txt` via API
- Create: `content/llms-txt-content.txt`

- [ ] **Step 1: Draft the llms.txt content**

Create `/Users/skitch/ClaudeCode/leaf-and-bird/content/llms-txt-content.txt`:

```
# Leaf & Bird

> Clean vegan skincare brand making rare non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers.

Leaf & Bird is a direct-to-consumer clean beauty brand. Our formulations are vegan, free from parabens, sulfates, synthetic fragrance, and PEGs. Hero products are a vegan PDRN serum (most commercial PDRN is salmon-derived; ours isn't) and whipped grass-fed beef tallow creams in three botanical scents.

## Shop
- Homepage: https://leaf-and-bird.com/
- All products: https://leaf-and-bird.com/collections/all
- Best sellers: https://leaf-and-bird.com/collections/best-sellers
- PDRN serum: https://leaf-and-bird.com/collections/pdrn-serum
- Vegan PDRN: https://leaf-and-bird.com/collections/vegan-pdrn-serum
- Tallow cream: https://leaf-and-bird.com/collections/tallow-cream
- Non-toxic skincare: https://leaf-and-bird.com/collections/non-toxic-skincare
- Pregnancy-safe skincare: https://leaf-and-bird.com/collections/pregnancy-safe-skincare
- Clean Korean skincare: https://leaf-and-bird.com/collections/clean-korean-skincare

## Products
- Vegan PDRN Brightening Serum — https://leaf-and-bird.com/products/pdrn-brightening-serum — Rare non-salmon-derived PDRN + Acetyl Hexapeptide-8 brightening serum. $32.
- Whipped Grass-Fed Tallow Cream — Lemongrass & Lavender — https://leaf-and-bird.com/products/tallow-cream-lemongrass-lavender — $27.
- Whipped Grass-Fed Tallow Cream — Orange & Bergamot — https://leaf-and-bird.com/products/tallow-cream-orange-bergamot — $27.
- Whipped Grass-Fed Tallow Cream — Peaceful Night — https://leaf-and-bird.com/products/tallow-cream-peaceful-night — $27.
- Peptide Eye Gel-Cream — https://leaf-and-bird.com/products/peptide-eye-gel-cream — $35.99.
- Sleep Plus Collagen Cream — https://leaf-and-bird.com/products/sleep-plus-collagen-cream — $32.99.
- Vitamin C Serum — https://leaf-and-bird.com/products/vitamin-c-serum — $20.
- Vitamin Glow Serum — https://leaf-and-bird.com/products/vitamin-glow-serum — $24.90.
- Dead Sea Mud — https://leaf-and-bird.com/products/dead-sea-mud — $31.90.

## Journal (blog)
- Full content: https://leaf-and-bird.com/blogs/journal

## Full details
- Detailed product ingredients, FAQs, and collection reasoning: https://leaf-and-bird.com/llms-full.txt

## Contact
- Email: hello@leaf-and-bird.com
- Store domain: leaf-and-bird.com
```

(The executor may expand this — it's the seed. Update product URLs to real handles after renames in Phase P2.)

- [ ] **Step 2: Create Shopify Page `llms-txt`**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
body = open('content/llms-txt-content.txt').read()
# Shopify Page body is HTML; wrap in <pre> so raw text renders, OR use custom template (below) for true text/plain
payload = {'page': {
  'title': 'llms.txt',
  'handle': 'llms-txt',
  'body_html': '<pre>' + body.replace('<','&lt;').replace('>','&gt;') + '</pre>',
  'template_suffix': 'llms-txt',
  'published': True,
}}
print(s.post('/pages.json', payload))"
```

This creates `/pages/llms-txt`. We also need the URL `/llms.txt` to work — handled in Step 3.

- [ ] **Step 3: Create plain-text template + route `/llms.txt` via redirect**

Create `theme-working/templates/page.llms-txt.liquid`:

```liquid
{{ page.body | strip_html | escape }}
```

Upload:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/templates/page.llms-txt.liquid templates/page.llms-txt.liquid
```

Add a URL redirect in Shopify: `/llms.txt` → `/pages/llms-txt`. Run:

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
print(s.post('/redirects.json', {'redirect': {'path': '/llms.txt', 'target': '/pages/llms-txt'}}))"
```

- [ ] **Step 4: Verify**

Run:
```bash
curl -sL https://leaf-and-bird.com/llms.txt | head -20
```

Expected: Plain-text llms.txt content visible. (Shopify will 301 `/llms.txt` → `/pages/llms-txt` and the page renders plain text via our template.)

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/llms-txt-content.txt ClaudeCode/leaf-and-bird/theme-working/templates/page.llms-txt.liquid
git commit -m "Publish /llms.txt for AI crawler brand summary"
```

---

### Task T1.11: Create `/llms-full.txt` with deep brand/product data

**Files:**
- Create: `content/llms-full-txt-content.txt`
- Create: `theme-working/templates/page.llms-full-txt.liquid`

- [ ] **Step 1: Auto-generate llms-full.txt from Shopify data**

Create `scripts/build_llms_full.py`:

```python
"""Build llms-full.txt from live Shopify product + collection + article data."""
import json
import pathlib
import shopify_api

OUT = pathlib.Path(__file__).resolve().parent.parent / "content" / "llms-full-txt-content.txt"


def main():
    lines = ["# Leaf & Bird — Full AI-Discoverability Index",
             "",
             "> Clean vegan skincare brand making rare non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers.",
             "",
             "## Brand identity",
             "Leaf & Bird is a direct-to-consumer clean beauty brand. Formulations are vegan, free from parabens, sulfates, synthetic fragrance, and PEGs. Hero products: vegan PDRN serum (most commercial PDRN is salmon-derived; ours is not) and whipped grass-fed beef tallow creams in three botanical scents.",
             ""]

    lines.append("## Products")
    for p in shopify_api.get("/products.json", params={"limit": 250})["products"]:
        if p["status"] != "active":
            continue
        price = p["variants"][0]["price"]
        lines.append(f"### {p['title']}")
        lines.append(f"- URL: https://leaf-and-bird.com/products/{p['handle']}")
        lines.append(f"- Price: ${price}")
        lines.append(f"- Type: {p.get('product_type') or '-'}")
        lines.append(f"- Tags: {p.get('tags') or '-'}")
        import re
        body = re.sub(r"<[^>]+>", " ", (p.get("body_html") or "")).strip()
        import html as htmllib
        body = htmllib.unescape(re.sub(r"\s+", " ", body))
        lines.append(f"- Description: {body[:800]}")
        lines.append("")

    lines.append("## Collections (money pages)")
    for c in shopify_api.get("/custom_collections.json", params={"limit": 250})["custom_collections"]:
        lines.append(f"- {c['title']}: https://leaf-and-bird.com/collections/{c['handle']}")
    for c in shopify_api.get("/smart_collections.json", params={"limit": 250})["smart_collections"]:
        lines.append(f"- {c['title']}: https://leaf-and-bird.com/collections/{c['handle']}")
    lines.append("")

    lines.append("## Blog")
    blogs = shopify_api.get("/blogs.json")["blogs"]
    for b in blogs:
        lines.append(f"### {b['title']}")
        articles = shopify_api.get(f"/blogs/{b['id']}/articles.json", params={"limit": 250})["articles"]
        for a in articles:
            lines.append(f"- {a['title']}: https://leaf-and-bird.com/blogs/{b['handle']}/{a['handle']}")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
```

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 build_llms_full.py
```

Expected: `content/llms-full-txt-content.txt` populated.

- [ ] **Step 2: Create Shopify Page + template**

Create `theme-working/templates/page.llms-full-txt.liquid`:

```liquid
{{ page.body | strip_html | escape }}
```

Upload and create page:

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/templates/page.llms-full-txt.liquid templates/page.llms-full-txt.liquid

cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
body = open('content/llms-full-txt-content.txt').read()
payload = {'page': {
  'title': 'llms-full.txt',
  'handle': 'llms-full-txt',
  'body_html': '<pre>' + body.replace('<','&lt;').replace('>','&gt;') + '</pre>',
  'template_suffix': 'llms-full-txt',
  'published': True,
}}
print(s.post('/pages.json', payload))
print(s.post('/redirects.json', {'redirect': {'path':'/llms-full.txt','target':'/pages/llms-full-txt'}}))"
```

- [ ] **Step 3: Verify**

Run:
```bash
curl -sL https://leaf-and-bird.com/llms-full.txt | head -30
```

Expected: Plain-text content starting with `# Leaf & Bird — Full AI-Discoverability Index`.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/build_llms_full.py ClaudeCode/leaf-and-bird/content/llms-full-txt-content.txt ClaudeCode/leaf-and-bird/theme-working/templates/page.llms-full-txt.liquid
git commit -m "Publish /llms-full.txt with auto-generated deep brand index"
```

---

### Task T1.12: Fix canonical tags on paginated/filtered collection URLs

**Files:**
- Modify: `theme-working/layout/theme.liquid` or `theme-working/snippets/meta-tags.liquid`

- [ ] **Step 1: Verify current canonical behavior**

Run:
```bash
curl -s "https://leaf-and-bird.com/collections/all?page=2" | grep 'rel="canonical"'
curl -s "https://leaf-and-bird.com/collections/all?filter.v.price.gte=20" | grep 'rel="canonical"'
```

- [ ] **Step 2: Ensure canonical always points to the base collection URL (ignoring page= and filter.* params)**

Find the canonical tag output in theme. Replace with:

```liquid
<link rel="canonical" href="{{ canonical_url }}">
```

Shopify's built-in `canonical_url` already strips most parameters; if audit showed issues, add explicit strip logic:

```liquid
{%- assign canon = request.origin | append: request.path -%}
<link rel="canonical" href="{{ canon }}">
```

- [ ] **Step 3: Upload and verify**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/layout/theme.liquid layout/theme.liquid

curl -s "https://leaf-and-bird.com/collections/all?page=2" | grep 'rel="canonical"'
```

Expected: Canonical href has no `?page=...` or `?filter...`.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/layout/theme.liquid
git commit -m "Fix canonical tags to ignore pagination and filter params"
```

---

### Task T1.13: Audit image alt attributes across theme

**Files:** (audit only; fix in later tasks as content is published)

- [ ] **Step 1: From audit report §9, quantify alt coverage**

The audit report already includes "missing alt" counts. For each theme file with `<img>` tags lacking `alt=`, decide:
- If it's a dynamic image from a product/collection/etc. → ensure `alt={{ resource.alt | default: resource.title }}` is supplied.
- If it's a static theme image → add descriptive alt.

- [ ] **Step 2: Edit each offending file**

For each file from audit, update `<img>` tags missing `alt`. Example:

Before:
```liquid
<img src="{{ product.featured_image | image_url }}">
```

After:
```liquid
<img src="{{ product.featured_image | image_url }}" alt="{{ product.featured_image.alt | default: product.title }}">
```

- [ ] **Step 3: Upload modified files**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 upload_asset.py ../theme-working/<file> <file>
```

Repeat per edited file.

- [ ] **Step 4: Re-run the audit script**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && \
  python3 scripts/pull_theme.py && python3 scripts/audit_theme.py
```

Expected: §9 "Missing alt" count is 0 (or near-0 after accounting for decorative images using `alt=""`).

- [ ] **Step 5: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/theme-working/ ClaudeCode/leaf-and-bird/content/theme-audit-report.md
git commit -m "Audit and fix missing image alt attributes across theme"
```

---

### Task T1.14: Capture Core Web Vitals baseline

**Files:**
- Create: `content/cwv-baseline.md`

- [ ] **Step 1: Run PageSpeed Insights for 3 representative pages**

Instruct user (or handle via PageSpeed Insights API if credentials available):
- Homepage: https://leaf-and-bird.com/
- Product page: https://leaf-and-bird.com/products/pdrn-brightening-serum
- Collection page: https://leaf-and-bird.com/collections/all

For each: capture mobile + desktop LCP, CLS, INP, total score.

- [ ] **Step 2: Document in baseline file**

Create `content/cwv-baseline.md`:

```markdown
# Core Web Vitals — Baseline (2026-04-16, pre-SEO-build)

## Homepage
| Device | LCP | CLS | INP | Score |
|---|---|---|---|---|
| Mobile | X.Xs | 0.XX | XXms | NN |
| Desktop | X.Xs | 0.XX | XXms | NN |

## Product page (/products/pdrn-brightening-serum)
| Device | LCP | CLS | INP | Score |
|---|---|---|---|---|
| Mobile | X.Xs | 0.XX | XXms | NN |
| Desktop | X.Xs | 0.XX | XXms | NN |

## Collection page (/collections/all)
| Device | LCP | CLS | INP | Score |
|---|---|---|---|---|
| Mobile | X.Xs | 0.XX | XXms | NN |
| Desktop | X.Xs | 0.XX | XXms | NN |

## Notes
- [any immediate red flags — large images, blocking JS, etc.]
```

Re-measure after P6 to validate no regression.

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/cwv-baseline.md
git commit -m "Capture Core Web Vitals baseline before SEO build"
```

---

## Phase P2 — Product Page Optimization (10 tasks)

### Shared pattern for each product task (T2.1–T2.9)

Every product task performs **the same 6 operations** against one SKU. They are listed once here so each task below can be concise. **Execute all 6 steps for every product task unless the task explicitly overrides.**

**Operation A — Draft the content JSON locally**
Create `content/products/<handle>.json` with the following shape (fill every field):

```json
{
  "product_id": 0,
  "title": "",
  "new_handle": null,
  "body_html": "",
  "meta_title": "",
  "meta_description": "",
  "product_type": "",
  "tags": "",
  "faq_json": [{"question": "", "answer": ""}],
  "free_from": [],
  "primary_keyword": ""
}
```

`body_html` structure (write in HTML so Shopify renders as-is, ~2,500-3,500 chars):

```html
<p><strong>[Hero paragraph — 40-70 words with primary keyword naturally woven in, crunchy-mom voice, addresses the reader's outcome.]</strong></p>

<h2>Key ingredients</h2>
<ul>
  <li><strong>[Ingredient 1]:</strong> [why it matters — 1-2 sentences]</li>
  <li><strong>[Ingredient 2]:</strong> ...</li>
  <!-- 3-6 hero ingredients -->
</ul>

<h2>What it does</h2>
<ul>
  <li>[Concrete benefit 1]</li>
  <li>[Concrete benefit 2]</li>
  <li>[Concrete benefit 3-5]</li>
</ul>

<h2>How to use</h2>
<ol>
  <li>[Step 1]</li>
  <li>[Step 2]</li>
  <li>[Step 3]</li>
</ol>

<h2>Who it's for</h2>
<p>[Persona match — crunchy-mom-specific language. 2-3 sentences.]</p>

<h2>Free from</h2>
<p>No parabens • No sulfates • No synthetic fragrance • No PEGs • [product-specific claims]</p>

<!-- Rotating modules, pick 1-3: sourcing story / study citations / ancestral context / routine pairing / before-after scenarios / pregnancy reassurance -->

<h2>Ingredients (full)</h2>
<p>[Full INCI list as currently on product — preserve exactly]</p>

<p><em>Suggested use, warnings, size, weight</em> — preserve from current body if present.</p>
```

**Operation B — Publish via Shopify Admin API**
Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/publish_product.py content/products/<handle>.json
```

(See `publish_product.py` defined in Task T2.0 below.)

**Operation C — Verify render on live site**
Run:
```bash
curl -s https://leaf-and-bird.com/products/<handle> | grep -oE '<h1[^>]*>[^<]*</h1>'
```

Expected: new title appears in H1 (or primary heading, depending on theme).

**Operation D — Verify schema**
Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && \
  python3 schema_validator.py product https://leaf-and-bird.com/products/<handle>
```

Expected: OK.

**Operation E — Visual spot-check (manual)**
Load the live URL in a browser. Confirm the new content renders correctly, FAQ accordion works, images have alt text.

**Operation F — Commit**
```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/products/<handle>.json
git commit -m "Rewrite <Product Name> product page with SEO + brand positioning"
```

---

### Task T2.0: Create `publish_product.py` helper (shared by all product tasks)

**Files:**
- Create: `scripts/publish_product.py`

- [ ] **Step 1: Write publisher**

Create `scripts/publish_product.py`:

```python
"""Publish a drafted product page (body, title, handle, metafields, meta tags) to Shopify."""
import json
import sys
import pathlib
import shopify_api


def publish(draft_path):
    d = json.loads(pathlib.Path(draft_path).read_text(encoding="utf-8"))
    pid = d["product_id"]

    # 1. Update product core fields
    update = {"product": {
        "id": pid,
        "title": d["title"],
        "body_html": d["body_html"],
        "product_type": d.get("product_type") or None,
        "tags": d.get("tags") or None,
    }}
    if d.get("new_handle"):
        update["product"]["handle"] = d["new_handle"]
    resp = shopify_api.put(f"/products/{pid}.json", update)
    print(f"Updated product {pid}: {resp['product']['title']}")

    # 2. Set meta_title + meta_description via Shopify SEO fields (handled via metafields `global.title_tag` / `global.description_tag`)
    if d.get("meta_title"):
        _upsert_metafield(pid, "products", "global", "title_tag", "single_line_text_field", d["meta_title"])
    if d.get("meta_description"):
        _upsert_metafield(pid, "products", "global", "description_tag", "multi_line_text_field", d["meta_description"])

    # 3. Set FAQ metafield
    if d.get("faq_json"):
        _upsert_metafield(pid, "products", "seo", "faq_json", "json", json.dumps(d["faq_json"]))

    # 4. Set free_from metafield
    if d.get("free_from"):
        _upsert_metafield(pid, "products", "seo", "free_from", "json", json.dumps(d["free_from"]))

    # 5. Set primary_keyword metafield (if your metafield def exists on Product too; else skip)
    # NOTE: primary_keyword is a collection/article metafield in our definitions; keep here only if you add it for products.

    print("Done.")


def _upsert_metafield(owner_id, owner_resource, namespace, key, type_, value):
    existing = shopify_api.get(f"/{owner_resource}/{owner_id}/metafields.json")["metafields"]
    for m in existing:
        if m["namespace"] == namespace and m["key"] == key:
            shopify_api.put(f"/metafields/{m['id']}.json",
                            {"metafield": {"id": m["id"], "value": value, "type": type_}})
            print(f"  updated metafield {namespace}.{key}")
            return
    shopify_api.post(f"/{owner_resource}/{owner_id}/metafields.json",
                     {"metafield": {"namespace": namespace, "key": key, "type": type_, "value": value}})
    print(f"  created metafield {namespace}.{key}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publish_product.py <path/to/draft.json>")
        sys.exit(2)
    publish(sys.argv[1])
```

- [ ] **Step 2: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/publish_product.py
git commit -m "Add publish_product.py helper for SKU rewrites"
```

---

### Task T2.1: Rewrite PDRN Brightening Serum (hero product)

**Files:**
- Create: `content/products/pdrn-brightening-serum.json`

- [ ] **Step 1: Draft the JSON (Operation A)**

Create `content/products/pdrn-brightening-serum.json`. Use these values:

- `product_id`: `10325332066603`
- `title`: `Vegan PDRN Brightening Serum`
- `new_handle`: `null` (keep existing handle)
- `primary_keyword`: `vegan pdrn serum`
- `product_type`: `Facial Care`
- `tags`: keep existing, add `Vegan, PDRN, Korean Skincare, Clean Beauty, Salmon-Free`
- `meta_title`: `Vegan PDRN Brightening Serum (Non-Salmon) | Leaf & Bird` (≤60 chars)
- `meta_description`: `Rare non-salmon-derived PDRN + Argireline peptide brightening serum. Vegan, clean, K-beauty-grade. Made for health-conscious moms. Shop $32.` (≤160 chars)
- `free_from`: `["salmon DNA", "animal derivatives", "parabens", "sulfates", "synthetic fragrance", "PEGs"]`

Write `body_html` with the structure from the shared pattern. Content emphasis:
- Hero paragraph: lead with "The only vegan PDRN serum you'll find" framing, tie to K-beauty heritage + clean-science credibility
- Key ingredients section: Polydeoxyribonucleotide (PDRN, plant/synthetic source — not salmon), Acetyl Hexapeptide-8 (Argireline — Botox-alternative peptide), Sodium Hyaluronate, Panthenol
- Rotating modules to include: science/study citations (PDRN skin regeneration studies), routine pairing (pair with Peptide Eye Gel-Cream for AM+PM Korean-routine positioning)
- FAQ seeds (7 questions minimum; answers 40-80 words each):
  - "Is this PDRN vegan?"
  - "Does this contain salmon DNA?"
  - "What does PDRN do for skin?"
  - "Can I use this during pregnancy?" (acknowledge phenoxyethanol honestly, note consult-doctor)
  - "How does PDRN compare to retinol?"
  - "Does this contain phenoxyethanol?" (direct-answer the preservative question — honesty > hiding)
  - "What's the difference between PDRN serum and PDRN cream?"

- [ ] **Step 2: Publish (Operation B)**

Run `python3 scripts/publish_product.py content/products/pdrn-brightening-serum.json`.

- [ ] **Step 3: Verify (Operations C + D + E)**

Follow Operations C, D, E from the shared pattern for this product.

- [ ] **Step 4: Commit (Operation F)**

---

### Task T2.2: Rewrite Tallow Cream Lemongrass & Lavender

**Files:**
- Create: `content/products/tallow-cream-lemongrass-lavender.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325459599659`
- `title`: `Whipped Grass-Fed Tallow Cream — Lemongrass & Lavender`
- `new_handle`: `null` (keep existing)
- `primary_keyword`: `whipped grass-fed tallow cream`
- `product_type`: `Body Care`
- `tags`: add `Whipped Tallow, Grass-Fed, Beef Tallow, Ancestral Skincare`
- `meta_title`: `Whipped Grass-Fed Tallow Cream — Lemongrass & Lavender` (60 chars)
- `meta_description`: `Pasture-raised whipped beef tallow cream with lemongrass + lavender essential oils. Chemical-free, ancestral skincare for dry and sensitive skin.` (≤160)
- `free_from`: `["seed oils", "parabens", "sulfates", "synthetic fragrance", "PEGs"]`

Body emphasis: ancestral/warm voice, sourcing story (pasture-raised, grass-fed beef), why tallow mimics human sebum biologically, lemongrass + lavender benefits, whipped texture benefits (absorbs fast, doesn't feel greasy). Rotating modules: ancestral context, sourcing story, before-after skin texture scenarios. FAQ seeds: "Does it smell like beef?", "Is tallow safe during pregnancy?", "Can I use this on my baby?", "Does tallow help eczema?", "Is it really chemical-free?", "Grass-fed vs grain-fed — why does it matter?", "How long does one jar last?"

- [ ] **Step 2-4: Publish, verify, commit (Operations B-F)**

---

### Task T2.3: Rewrite Tallow Cream Orange & Bergamot

**Files:**
- Create: `content/products/tallow-cream-orange-bergamot.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325331902763`
- `title`: `Whipped Grass-Fed Tallow Cream — Orange & Bergamot`
- `primary_keyword`: `whipped tallow face cream`
- `meta_title`: `Whipped Grass-Fed Tallow Cream — Orange & Bergamot`
- `meta_description`: `Uplifting orange + bergamot whipped tallow cream. Grass-fed, chemical-free. Moisturizes without clogging pores. Pregnancy and baby safe.` (≤160)

Differentiator from T2.2: brighter/citrus mood; daytime use; lighter feel; bergamot's clarifying/antioxidant story. Otherwise similar structure. FAQ includes one about photosensitivity from bergamot (furocoumarins) — address honestly (bergamot FCF-free if true; otherwise advise nighttime use).

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.4: Rewrite Tallow Cream Peaceful Night

**Files:**
- Create: `content/products/tallow-cream-peaceful-night.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325459763499`
- `title`: `Whipped Grass-Fed Tallow Cream — Peaceful Night`
- `primary_keyword`: `night tallow cream`
- `meta_title`: `Whipped Grass-Fed Tallow Cream — Peaceful Night`
- `meta_description`: `Calming nighttime whipped tallow cream with fir + relaxing botanicals. Grass-fed, chemical-free. Wake up with softer, deeply moisturized skin.` (≤160)

Differentiator: night-routine positioning, sleep-supportive aromatherapy angle, heavier overnight repair story. FAQ adds sleep + night-routine questions.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.5: Rewrite Peptide Eye Gel-Cream

**Files:**
- Create: `content/products/peptide-eye-gel-cream.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325332721963`
- `title`: `Peptide Eye Gel-Cream`
- `primary_keyword`: `peptide eye cream`
- `meta_title`: `Peptide Eye Gel-Cream — Vegan & Clean | Leaf & Bird`
- `meta_description`: `Lightweight peptide-packed eye gel-cream for fine lines, dark circles, and puffiness. Vegan, fragrance-free. Pairs with our PDRN serum.` (≤160)

Body emphasis: cross-sell pairing with PDRN serum (under-eye PDRN routine is a K-beauty trend — own this positioning), lightweight gel-cream texture, caffeine + peptide story (verify actual ingredients from current body_html). FAQ seeds include pairing with PDRN, pregnancy-safety, compatibility with makeup.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.6: Rewrite Sleep Plus Collagen Cream

**Files:**
- Create: `content/products/sleep-plus-collagen-cream.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325332361515`
- `title`: `Sleep Plus Collagen Cream` (keep title — positioning clear)
- `primary_keyword`: `night collagen cream`
- `meta_title`: `Sleep Plus Collagen Cream — Vegan Night Cream | Leaf & Bird`
- `meta_description`: `Overnight vegan collagen cream with hydrating peptides. Wake up to plumper, firmer skin. Clean, non-toxic, fragrance-free.` (≤160)

Body emphasis: night-routine positioning, vegan "collagen" clarification (plant-derived amino acid/peptide analogues — not actual bovine collagen; be honest about mechanism), pairing with PDRN or tallow creams. FAQ addresses vegan-collagen honestly.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.7: Rewrite Vitamin C Serum

**Files:**
- Create: `content/products/vitamin-c-serum.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325459960107`
- `title`: `Vitamin C Serum`
- `primary_keyword`: `clean vitamin c serum`
- `meta_title`: `Vitamin C Serum — Clean, Vegan, Daily Brightening | Leaf & Bird`
- `meta_description`: `Stable vitamin C serum for daily brightening and antioxidant protection. Clean, vegan, gentle enough for sensitive skin.` (≤160)

Positioning: pure/daily vitamin C hero, different from Vitamin Glow Serum. FAQ addresses "Vitamin C vs Vitamin Glow — which do I choose?"

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.8: Rewrite Vitamin Glow Serum

**Files:**
- Create: `content/products/vitamin-glow-serum.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325332230443`
- `title`: `Vitamin Glow Serum`
- `primary_keyword`: `brightening serum`
- `meta_title`: `Vitamin Glow Serum — Multi-Active Radiance | Leaf & Bird`
- `meta_description`: `Multi-active brightening and radiance serum. Clean, vegan, targets dull skin and uneven tone. For glow-seekers who want efficacy without harsh actives.` (≤160)

Positioning: multi-active brightening/radiance (niacinamide + licorice + whatever actuals — read body_html first). Different lane from Vitamin C. FAQ addresses the comparison head-on.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.9: Rewrite Dead Sea Mud

**Files:**
- Create: `content/products/dead-sea-mud.json`

- [ ] **Step 1: Draft**

- `product_id`: `10325332558123`
- `title`: `Dead Sea Mud Mask` (adjust if current title is just "Dead Sea Mud" — clarify as mask)
- `primary_keyword`: `dead sea mud mask`
- `meta_title`: `Dead Sea Mud Mask — Detox, Blackheads, Clarifying | Leaf & Bird`
- `meta_description`: `Mineral-rich Dead Sea mud mask for blackheads, oily skin, and clarified pores. Clean, vegan, gentle weekly detox ritual.` (≤160)

Body emphasis: detox/clarifying ritual, weekly use, body + face use, mineral content story. Crunchy-mom angle: "the detox your skin actually needs" + EWG-friendly.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T2.10: Full product-schema audit across all 9 SKUs

**Files:** (no files — verification only)

- [ ] **Step 1: Run schema validator against every product URL**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && for h in \
  pdrn-brightening-serum \
  tallow-cream-lemongrass-lavender \
  tallow-cream-orange-bergamot \
  tallow-cream-peaceful-night \
  peptide-eye-gel-cream \
  sleep-plus-collagen-cream \
  vitamin-c-serum \
  vitamin-glow-serum \
  dead-sea-mud; do
  echo "=== $h ==="
  python3 schema_validator.py product "https://leaf-and-bird.com/products/$h" || echo "FAILED: $h"
done
```

Expected: every URL prints `OK: ... passes product schema validation.`

- [ ] **Step 2: Check in Google Rich Results Test (manual)**

For each product URL, paste into https://search.google.com/test/rich-results. Confirm `Product` and `FAQPage` detected without errors.

- [ ] **Step 3: If any fail, fix in the relevant content JSON and republish**

- [ ] **Step 4: Commit the phase-complete marker**

```bash
cd /Users/skitch && git commit --allow-empty -m "P2 complete: all 9 product pages rewritten with schema + FAQ"
```

---

## Phase P3 — PDRN Money Pages (9 tasks)

### Shared pattern for each money-page task (T3.1–T3.7, T4.1–T4.8)

**Pre-work:** Each collection must already exist in Shopify. For any that doesn't, the task creates it. Then the task populates `seo.*` metafields and the `body_html` fallback.

**Operation A — Draft the collection JSON locally**
Create `content/collections/<slug>.json`:

```json
{
  "slug": "",
  "collection_id": null,
  "title": "",
  "body_html": "",
  "h1": "",
  "intro": "",
  "body_modules": [
    {"type": "h2h3s", "heading": "", "html": ""},
    {"type": "table", "heading": "", "html": ""}
  ],
  "faq_json": [{"question": "", "answer": ""}],
  "meta_title": "",
  "meta_description": "",
  "primary_keyword": "",
  "product_ids_to_include": []
}
```

`body_modules[]` types that correspond to module library in the spec:
- `h2h3s` — H2 with 2-4 H3 sub-blocks
- `table` — a comparison table (`<table>...</table>` HTML)
- `ingredient` — ingredient breakdown list
- `routine` — numbered how-to routine
- `myths` — myth-busting section
- `scenario` — persona/scenario block
- `quote` — expert/study citation block
- `ranked_list` — a numbered list of our products with "best for X" (used on listicle-intent pages)
- `prosCons` — pros and cons block

**Diversity enforcement:** No two consecutive money-page tasks may use identical `module_order` arrays. Per-page module selection is prescribed in each task below.

**Operation B — Create/update the collection via Shopify API**
Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/publish_collection.py content/collections/<slug>.json
```

(See `publish_collection.py` in Task T3.0.)

**Operation C — Verify**
```bash
curl -sL https://leaf-and-bird.com/collections/<slug> | grep -oE '<h1[^>]*>[^<]*</h1>'
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 schema_validator.py collection "https://leaf-and-bird.com/collections/<slug>"
```

**Operation D — Commit**
```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/collections/<slug>.json
git commit -m "Build money page: <slug>"
```

---

### Task T3.0: Create `publish_collection.py` helper

**Files:**
- Create: `scripts/publish_collection.py`

- [ ] **Step 1: Write publisher**

Create `scripts/publish_collection.py`:

```python
"""Create or update a Shopify collection with SEO metafields for money-page rendering."""
import json
import sys
import pathlib
import shopify_api


def publish(draft_path):
    d = json.loads(pathlib.Path(draft_path).read_text(encoding="utf-8"))

    cid = d.get("collection_id")
    if not cid:
        # Create a new custom_collection
        payload = {"custom_collection": {
            "title": d["title"],
            "handle": d["slug"],
            "body_html": d.get("body_html", ""),
            "published": True,
        }}
        resp = shopify_api.post("/custom_collections.json", payload)
        cid = resp["custom_collection"]["id"]
        print(f"Created collection {cid} at /collections/{d['slug']}")
        # Add products
        for pid in d.get("product_ids_to_include", []):
            shopify_api.post("/collects.json",
                             {"collect": {"collection_id": cid, "product_id": pid}})
            print(f"  attached product {pid}")
    else:
        # Update existing collection
        resp = shopify_api.put(f"/custom_collections/{cid}.json",
                               {"custom_collection": {"id": cid, "title": d["title"], "body_html": d.get("body_html", "")}})
        print(f"Updated collection {cid}")

    # Metafields
    _upsert(cid, "collections", "global", "title_tag", "single_line_text_field", d.get("meta_title", ""))
    _upsert(cid, "collections", "global", "description_tag", "multi_line_text_field", d.get("meta_description", ""))
    _upsert(cid, "collections", "seo", "h1", "single_line_text_field", d.get("h1", ""))
    _upsert(cid, "collections", "seo", "intro", "multi_line_text_field", d.get("intro", ""))
    _upsert(cid, "collections", "seo", "body_modules", "json", json.dumps(d.get("body_modules", [])))
    _upsert(cid, "collections", "seo", "faq_json", "json", json.dumps(d.get("faq_json", [])))
    _upsert(cid, "collections", "seo", "primary_keyword", "single_line_text_field", d.get("primary_keyword", ""))
    _upsert(cid, "collections", "seo", "meta_title", "single_line_text_field", d.get("meta_title", ""))
    _upsert(cid, "collections", "seo", "meta_description", "multi_line_text_field", d.get("meta_description", ""))

    # Persist collection_id back to the draft file for future updates
    if not d.get("collection_id"):
        d["collection_id"] = cid
        pathlib.Path(draft_path).write_text(json.dumps(d, indent=2), encoding="utf-8")


def _upsert(owner_id, owner_resource, namespace, key, type_, value):
    if not value:
        return
    existing = shopify_api.get(f"/{owner_resource}/{owner_id}/metafields.json")["metafields"]
    for m in existing:
        if m["namespace"] == namespace and m["key"] == key:
            shopify_api.put(f"/metafields/{m['id']}.json",
                            {"metafield": {"id": m["id"], "value": value, "type": type_}})
            print(f"  updated metafield {namespace}.{key}")
            return
    shopify_api.post(f"/{owner_resource}/{owner_id}/metafields.json",
                     {"metafield": {"namespace": namespace, "key": key, "type": type_, "value": value}})
    print(f"  created metafield {namespace}.{key}")


if __name__ == "__main__":
    publish(sys.argv[1])
```

- [ ] **Step 2: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/publish_collection.py
git commit -m "Add publish_collection.py helper for money-page creation"
```

---

### Task T3.1: Build `/collections/pdrn-serum` (PRIMARY PDRN hero page)

**Files:**
- Create: `content/collections/pdrn-serum.json`

- [ ] **Step 1: Draft**

- `slug`: `pdrn-serum`
- `title`: `PDRN Serum`
- `h1`: `Vegan PDRN Serum — Clean, K-Beauty-Grade Brightening`
- `primary_keyword`: `pdrn serum`
- `meta_title`: `Vegan PDRN Serum — Non-Salmon, Clean K-Beauty | Leaf & Bird` (60)
- `meta_description`: `Shop the rare vegan PDRN serum — non-salmon-derived, K-beauty-grade brightening for clean-beauty-loving moms. Fast absorption. $32.` (≤160)
- `product_ids_to_include`: `[10325332066603]` (PDRN serum); optionally add Peptide Eye Gel-Cream `10325332721963` for routine-pair presentation
- Intent: Commercial
- Shape: Intro → grid → benefits (H2+H3s module) → trust module (free-from) → routine-pair module → FAQ

`intro` (40-65 words, direct-answer hook for LLMs): "PDRN serum is the K-beauty brightening treatment everyone's talking about — and almost every version on the market is made from salmon DNA. Ours isn't. Leaf & Bird's vegan PDRN serum delivers the same clinical brightening, minus the fish. Formulated clean for health-conscious moms."

`body_modules` (choose module_order diverse from other PDRN pages):
1. `h2h3s` — "What makes our PDRN different" with 3 H3s (Vegan-sourced polydeoxyribonucleotide / Argireline co-hero / Clean formulation without phenoxyethanol trade-off)
2. `ingredient` — "The active system" with 4-5 ingredients explained
3. `routine` — "AM + PM routine" numbered steps pairing PDRN with eye cream
4. `scenario` — "Who it's for: the crunchy-K-beauty crossover mom"

`faq_json` (6-7 Qs):
- "Is this PDRN vegan?"
- "How is this different from Korean brand PDRN serums?"
- "Can I use PDRN with retinol / vitamin C / niacinamide?"
- "Is this pregnancy-safe?"
- "How long until I see results?"
- "Does PDRN replace retinol?"
- "Why is yours the only vegan PDRN?" (soften to "Why is vegan PDRN so rare?" pending superlative verification)

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.2: Build `/collections/pdrn-skincare` (umbrella)

**Files:**
- Create: `content/collections/pdrn-skincare.json`

- [ ] **Step 1: Draft**

- `slug`: `pdrn-skincare`
- `h1`: `PDRN Skincare — Vegan & Clean`
- `primary_keyword`: `pdrn skincare`
- `meta_title`: `PDRN Skincare — Vegan Serums & Eye Cream | Leaf & Bird`
- `meta_description`: `The complete vegan PDRN skincare routine — brightening serum + eye cream. Clean, K-beauty-grade, health-conscious-mom-approved.` (≤160)
- `product_ids_to_include`: `[10325332066603, 10325332721963]` (PDRN serum + Peptide Eye Gel-Cream positioned as PDRN-adjacent)
- Intent: Commercial (umbrella)
- Shape: Intro → grid → "What is PDRN skincare" (H2+H3s) → full-routine module → ingredient-safety trust block → FAQ

**Module order must differ from T3.1.** Use this order:
1. `h2h3s` — "What is PDRN skincare" (different heading set from T3.1)
2. `routine` — "Build your PDRN routine" (different focus — broader than AM+PM pairing; includes mud mask cadence)
3. `myths` — "Common PDRN myths" (3-4 short myth-debunks)
4. `trust` — free-from matrix

FAQ differs from T3.1 with different angles.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.3: Build `/collections/best-pdrn-serum` (listicle intent)

**Files:**
- Create: `content/collections/best-pdrn-serum.json`

- [ ] **Step 1: Draft — listicle-shaped page**

- `slug`: `best-pdrn-serum`
- `h1`: `Best PDRN Serums: Our Picks for 2026`
- `primary_keyword`: `best pdrn serum`
- `meta_title`: `Best PDRN Serums 2026 — Clean & Vegan Picks | Leaf & Bird`
- `meta_description`: `The best PDRN serum for every skin concern — our 2026 lineup, ranked and explained. Vegan, clean, K-beauty-quality.` (≤160)
- `product_ids_to_include`: PDRN Brightening Serum + Peptide Eye Gel-Cream + (as "best for night routine") Sleep Plus Collagen Cream
- Intent: Listicle
- Shape: Intro → **ranked_list** (numbered, per-item "best for" callout per product) → minimal FAQ

**Module order completely different from T3.1 and T3.2.** Use:
1. `ranked_list` — "#1 Best overall: ... / #2 Best for under-eyes: ... / #3 Best for overnight: ..." each with 60-90 word blurb
2. `h2h3s` — "How we chose" (2-3 H3s on criteria: vegan sourcing, efficacy evidence, texture)
3. Short FAQ (3-4 Qs — shorter page intentionally)

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.4: Build `/collections/pdrn-eye-cream`

**Files:**
- Create: `content/collections/pdrn-eye-cream.json`

- [ ] **Step 1: Draft**

- `slug`: `pdrn-eye-cream`
- `h1`: `PDRN Eye Cream`
- `primary_keyword`: `pdrn eye cream`
- `meta_title`: `PDRN Eye Cream — Vegan & Peptide-Powered | Leaf & Bird`
- `meta_description`: `Peptide-powered eye gel-cream designed to pair with our vegan PDRN serum. Targets fine lines, puffiness, and dark circles.` (≤160)
- `product_ids_to_include`: Peptide Eye Gel-Cream (primary); PDRN Serum (for routine pairing)
- Intent: Commercial
- Shape: Intro → grid → pairing-with-PDRN explainer → benefits → FAQ

**Module order** (must differ from T3.1-T3.3):
1. `scenario` — "The under-eye concern PDRN is known for" (lead with scenario, not benefits)
2. `h2h3s` — "How peptides + PDRN work together under the eye" (3 H3s)
3. `routine` — "Your AM + PM under-eye routine"
4. FAQ

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.5: Build `/collections/pdrn-vs-retinol` (comparison intent)

**Files:**
- Create: `content/collections/pdrn-vs-retinol.json`

- [ ] **Step 1: Draft — comparison-shaped page**

- `slug`: `pdrn-vs-retinol`
- `h1`: `PDRN vs Retinol: Which Is Right for You?`
- `primary_keyword`: `pdrn vs retinol`
- `meta_title`: `PDRN vs Retinol — Which Active Is Right for You? | Leaf & Bird`
- `meta_description`: `PDRN vs retinol: efficacy, safety, pregnancy considerations, and which to pick for your skin goals. Includes our vegan PDRN options.` (≤160)
- `product_ids_to_include`: PDRN Serum (primary), Peptide Eye Gel-Cream (alternative pathway)
- Intent: Comparison
- Shape: Table first → deep-dive → decision helper → grid (products as alternatives) → FAQ

**Module order:**
1. `table` — comparison: efficacy / safety / pregnancy / cost / skin types / time to results (PDRN column vs Retinol column)
2. `h2h3s` — deep-dive: how PDRN works vs how retinol works
3. `prosCons` — pros/cons of each
4. `scenario` — "Choose PDRN if / Choose retinol if" decision helper
5. FAQ

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.6: Build `/collections/clean-korean-skincare` (bridge page — unicorn keyword)

**Files:**
- Create: `content/collections/clean-korean-skincare.json`

- [ ] **Step 1: Draft — narrative/bridge-shaped page**

- `slug`: `clean-korean-skincare`
- `h1`: `Clean Korean Skincare — Non-Toxic K-Beauty for Moms`
- `primary_keyword`: `non toxic korean skincare`
- `meta_title`: `Clean Korean Skincare — Non-Toxic K-Beauty Picks | Leaf & Bird`
- `meta_description`: `K-beauty loves actives; crunchy moms avoid toxins. Our clean Korean skincare picks deliver both — led by vegan PDRN. Shop the edit.` (≤160)
- `product_ids_to_include`: PDRN Serum, Peptide Eye Gel-Cream, Vitamin C Serum, Vitamin Glow Serum
- Intent: Bridge/niche narrative
- Shape: Narrative essay → curated picks → FAQ (no big benefits table)

**Module order** (very different from product-first pages):
1. (longer) `intro` — essay-style, narrative tone, sets the tension: K-beauty efficacy + crunchy-mom clean standards seem incompatible; here's how we bridge it
2. `h2h3s` — "The 3 things most K-beauty products get wrong (from a crunchy-mom lens)" (3 H3s: fragrance, preservatives, synthetic actives)
3. `ranked_list` — "Our clean K-beauty picks" — curated products with "why it makes the list"
4. FAQ: "Is Korean skincare safe during pregnancy?", "Can K-beauty be truly clean?", "Is all PDRN from salmon?", etc.

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.7: Build `/collections/vegan-pdrn-serum` (unique moat page)

**Files:**
- Create: `content/collections/vegan-pdrn-serum.json`

- [ ] **Step 1: Draft — positioning-shaped page**

- `slug`: `vegan-pdrn-serum`
- `h1`: `Vegan PDRN Serum`
- `primary_keyword`: `vegan pdrn`
- `meta_title`: `Vegan PDRN Serum — Rare Non-Salmon Formula | Leaf & Bird`
- `meta_description`: `Vegan PDRN serum — rare non-salmon-derived polydeoxyribonucleotide. Clean, K-beauty-quality, formulated for ethically-minded health-conscious moms.` (≤160)
- `product_ids_to_include`: PDRN Brightening Serum
- Intent: Commercial + audience/values
- Shape: Values-led intro → direct-answer "is PDRN vegan?" block → grid → ingredient proof → FAQ

**Module order** (distinct from T3.1 which also features the PDRN serum):
1. `intro` (values-led opening: "If you love what PDRN does for skin but not where most PDRN comes from — this is for you.")
2. `myths` — "Is all PDRN from salmon? Three things every shopper should know"
3. `ingredient` — "Proof in the ingredient list" (direct quote of the INCI, highlighting the polydeoxyribonucleotide + no animal-derived ingredients)
4. `scenario` — "Who chooses vegan PDRN" (ethical vegan / crunchy mom / K-beauty crossover)
5. FAQ: strong direct-answer questions for LLM citation (is pdrn vegan / is our pdrn from salmon / what is plant-based pdrn / vegan pdrn alternatives)

- [ ] **Step 2-4: Publish, verify, commit**

---

### Task T3.8: Verify PDRN pillar internal linking graph

**Files:**
- Create: `scripts/check_links.py`

- [ ] **Step 1: Write link checker**

Create `scripts/check_links.py`:

```python
"""Verify each PDRN money page links to 2-3 related money pages + 1 article."""
import re
import urllib.request

PDRN_PAGES = [
    "/collections/pdrn-serum",
    "/collections/pdrn-skincare",
    "/collections/best-pdrn-serum",
    "/collections/pdrn-eye-cream",
    "/collections/pdrn-vs-retinol",
    "/collections/clean-korean-skincare",
    "/collections/vegan-pdrn-serum",
]

BASE = "https://leaf-and-bird.com"


def get_internal_links(url):
    html = urllib.request.urlopen(url).read().decode("utf-8", errors="replace")
    # Find main content area links
    links = set(re.findall(r'href="(/collections/[^"#?\s]+|/blogs/[^"#?\s]+|/products/[^"#?\s]+)"', html))
    return links


def main():
    for path in PDRN_PAGES:
        url = BASE + path
        links = get_internal_links(url)
        money_links = [l for l in links if l.startswith("/collections/")]
        blog_links = [l for l in links if l.startswith("/blogs/")]
        other_pdrn = [l for l in money_links if "/pdrn" in l or "clean-korean" in l or "vegan-pdrn" in l]
        print(f"{path}")
        print(f"  Outbound collection links: {len(money_links)}")
        print(f"  Outbound blog links: {len(blog_links)}")
        print(f"  PDRN-pillar links: {len(other_pdrn)}")
        if len(other_pdrn) < 2:
            print(f"  WARNING: fewer than 2 PDRN-pillar links")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 check_links.py
```

If any page shows WARNING, revisit its `body_modules` and add the required 2-3 PDRN-pillar internal links.

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/check_links.py
git commit -m "Verify PDRN pillar internal linking graph"
```

---

### Task T3.9: Full schema validation across all 7 PDRN pages

**Files:** (verification only)

- [ ] **Step 1: Run validator in a loop**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && for slug in \
  pdrn-serum pdrn-skincare best-pdrn-serum pdrn-eye-cream \
  pdrn-vs-retinol clean-korean-skincare vegan-pdrn-serum; do
  python3 schema_validator.py collection "https://leaf-and-bird.com/collections/$slug" || echo "FAIL: $slug"
done
```

Expected: 7 OK lines, no FAIL.

- [ ] **Step 2: Spot-check Rich Results Test on 3 pages (manual)**

Paste 3 URLs (pdrn-serum, vegan-pdrn-serum, pdrn-vs-retinol) into https://search.google.com/test/rich-results. Confirm CollectionPage + FAQPage detected.

- [ ] **Step 3: Commit phase marker**

```bash
cd /Users/skitch && git commit --allow-empty -m "P3 complete: 7 PDRN money pages with schema + linking"
```

---

## Phase P4 — Tallow + Crunchy-Mom Money Pages (10 tasks)

Uses the same shared pattern defined at the top of Phase P3. Each task below lists only the page-specific parameters. Every task performs Operations A-D from the P3 shared pattern.

**Module-diversity constraint for P4:** No two consecutive tasks in P4 may use the same `module_order`. The prescribed module lists below have been pre-checked for diversity.

---

### Task T4.1: Build `/collections/tallow-cream`

- `slug`: `tallow-cream`
- `h1`: `Whipped Grass-Fed Tallow Cream`
- `primary_keyword`: `tallow cream`
- `meta_title`: `Whipped Grass-Fed Tallow Cream — Clean, Ancestral | Leaf & Bird`
- `meta_description`: `Whipped grass-fed beef tallow cream — ancestral skincare for dry, sensitive, and postpartum skin. Three botanical scents. Shop all.` (≤160)
- `product_ids_to_include`: `[10325459599659, 10325331902763, 10325459763499]` (all 3 tallow creams)
- Intent: Commercial + audience
- Shape: Intro → grid → ancestral story → biological rationale → sourcing → FAQ

**Module order (diverse from all PDRN pages):**
1. `scenario` — "Why moms are returning to tallow" (narrative hook)
2. `h2h3s` — "What grass-fed tallow does for skin" (3 H3s: mimics sebum / ingredient simplicity / safe for sensitive skin)
3. `ingredient` — pasture-raised sourcing breakdown
4. FAQ (7 Qs: smell, shelf life, eczema, pregnancy, babies, grass-fed vs grain-fed, vegan-alternative question)

- [ ] **Step 1-4: Draft → publish → verify → commit (Operations A-D from P3)**

---

### Task T4.2: Build `/collections/whipped-tallow-face-cream`

- `slug`: `whipped-tallow-face-cream`
- `h1`: `Whipped Tallow Face Cream`
- `primary_keyword`: `whipped tallow face cream`
- `meta_title`: `Whipped Tallow Face Cream — Grass-Fed, Fast-Absorbing | Leaf & Bird`
- `meta_description`: `Whipped tallow face cream made from grass-fed beef tallow. Absorbs fast, no greasy feel. Three scents. For dry + sensitive skin.` (≤160)
- `product_ids_to_include`: same as T4.1
- Intent: Commercial
- Shape: Intro → grid → "whipped vs traditional tallow" → how-to → FAQ

**Module order:**
1. `h2h3s` — "What makes 'whipped' different" (3 H3s)
2. `table` — comparison: whipped tallow vs traditional tallow balm vs standard lotion
3. `routine` — "How to use whipped tallow day + night"
4. FAQ (different angle: whipping process, texture, layering under makeup, seasonal adjustments)

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.3: Build `/collections/best-tallow-cream` (listicle)

- `slug`: `best-tallow-cream`
- `h1`: `Best Tallow Creams: Our 2026 Picks`
- `primary_keyword`: `best tallow cream`
- `meta_title`: `Best Tallow Creams 2026 — Grass-Fed Picks | Leaf & Bird`
- `meta_description`: `The best tallow creams for face, body, and sensitive skin — our 2026 picks, ranked and explained. Grass-fed, clean, ancestral.` (≤160)
- `product_ids_to_include`: 3 tallow creams
- Intent: Listicle
- Shape: Ranked list with "best for" per product

**Module order (listicle-shaped, different from T3.3):**
1. `ranked_list` — "#1 Best for daily use: Orange & Bergamot / #2 Best for night: Peaceful Night / #3 Best for sensitive skin: Lemongrass & Lavender" (each 80-120 words, "best for X" justification)
2. `h2h3s` — "How we evaluated" (2-3 H3s: grass-fed sourcing, scent profile, skin-type fit)
3. Short FAQ

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.4: Build `/collections/tallow-cream-for-eczema` (problem-solution)

- `slug`: `tallow-cream-for-eczema`
- `h1`: `Tallow Cream for Eczema`
- `primary_keyword`: `tallow cream for eczema`
- `meta_title`: `Tallow Cream for Eczema — Natural Relief | Leaf & Bird`
- `meta_description`: `Grass-fed tallow cream for eczema — chemical-free, sensitive-skin-friendly. Why moms choose tallow for flare-ups and dry patches.` (≤160)
- `product_ids_to_include`: 3 tallow creams, lead with Lemongrass & Lavender (gentlest)
- Intent: Problem-solution
- Shape: Condition explainer → mechanism → application guidance → grid → FAQ

**Module order:**
1. `h2h3s` — "Understanding eczema-prone skin" (3 H3s: barrier dysfunction / inflammation / what ingredients worsen it)
2. `ingredient` — "Why tallow fits eczema-prone skin" (lipid profile focus)
3. `routine` — "How to apply tallow cream during a flare-up"
4. `quote` — study citation block (cite a peer-reviewed reference on lipid barrier repair if available)
5. FAQ: medical disclaimer, kid-safety, corticosteroid pairing question, when to see a doctor

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.5: Build `/collections/non-toxic-skincare` (crunchy-mom umbrella)

- `slug`: `non-toxic-skincare`
- `h1`: `Non-Toxic Skincare`
- `primary_keyword`: `non toxic skincare`
- `meta_title`: `Non-Toxic Skincare — Clean, Vegan, EWG-Safe | Leaf & Bird`
- `meta_description`: `Non-toxic skincare for health-conscious moms — clean, vegan, free of endocrine disruptors. PDRN serum, tallow cream, and more.` (≤160)
- `product_ids_to_include`: all 9 SKUs (full catalog)
- Intent: Audience umbrella
- Shape: Avoidance list first → "what we do instead" → curated products → FAQ

**Module order:**
1. `h2h3s` — "Ingredients we never use" (3 H3s: parabens & preservatives / synthetic fragrance / seed oils & endocrine disruptors)
2. `table` — "Our formulation standards" matrix (category vs. our rule)
3. `h2h3s` — "What we use instead" (3 H3s: grass-fed tallow / vegan PDRN / plant peptides)
4. FAQ: EWG rating, phenoxyethanol honesty, kids-safety, pregnancy, comparison to Primally Pure (honest)

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.6: Build `/collections/pregnancy-safe-skincare`

- `slug`: `pregnancy-safe-skincare`
- `h1`: `Pregnancy-Safe Skincare`
- `primary_keyword`: `pregnancy safe skincare`
- `meta_title`: `Pregnancy-Safe Skincare — Clean, Vegan Picks | Leaf & Bird`
- `meta_description`: `Pregnancy-safe skincare from Leaf & Bird — tallow cream, gentle brighteners, no retinoids. Curated for expectant and new moms.` (≤160)
- `product_ids_to_include`: 3 tallow creams, Peptide Eye Gel-Cream, Vitamin C (gentle), Sleep Plus Collagen, Dead Sea Mud (flag "once per week use during pregnancy"); EXCLUDE the main PDRN serum IF brand owner prefers (discuss in task — phenoxyethanol + niacinamide + newer actives may be conservative; default to INCLUDE with a caveat unless instructed otherwise)
- Intent: Audience
- Shape: Avoidance-first, gentle products second, FAQ

**Module order:**
1. `h2h3s` — "Ingredients to avoid during pregnancy" (3 H3s: retinoids / salicylic acid / essential oils in excess)
2. `ranked_list` — "Our pregnancy-friendly routine" (AM cleanse → tallow moisturize → gentle serum → sun protection note)
3. `scenario` — "Trimester-by-trimester skin guidance"
4. Medical disclaimer + FAQ (consult OBGYN, postpartum transitions, breastfeeding safety)

Disclaimer required: include `<em>This is not medical advice. Consult your healthcare provider.</em>` in intro and FAQ.

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.7: Build `/collections/seed-oil-free-skincare`

- `slug`: `seed-oil-free-skincare`
- `h1`: `Seed Oil-Free Skincare`
- `primary_keyword`: `seed oil free skincare`
- `meta_title`: `Seed Oil-Free Skincare — Tallow & Ancestral Formulas | Leaf & Bird`
- `meta_description`: `Seed oil-free skincare for moms avoiding inflammatory omega-6-heavy oils. Grass-fed tallow, clean PDRN, ancestral alternatives.` (≤160)
- `product_ids_to_include`: tallow creams (primary), Sleep Plus Collagen, Dead Sea Mud, check each SKU's INCI for seed-oil content before adding
- Intent: Audience/values
- Shape: Narrative intro (why seed oils) → ingredient audit approach → products → FAQ

**Module order:**
1. `intro` — narrative lead ("The seed oil conversation has reached skincare")
2. `h2h3s` — "The seed oil problem in skincare" (3 H3s)
3. `ingredient` — "What we use instead" (tallow, squalane if present, jojoba)
4. FAQ: "Is all tallow seed-oil-free?", "What about essential oils?", "Is this scientifically grounded?"

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.8: Build `/collections/clean-skincare-for-moms`

- `slug`: `clean-skincare-for-moms`
- `h1`: `Clean Skincare for Moms`
- `primary_keyword`: `skincare for moms`
- `meta_title`: `Clean Skincare for Moms — Postpartum, Busy, Health-Conscious | Leaf & Bird`
- `meta_description`: `Clean skincare made for moms — fast 2-step routines, pregnancy and breastfeeding safe, zero synthetic junk. Tallow cream + PDRN serum.` (≤160)
- `product_ids_to_include`: curated 4-6 SKUs that fit "busy clean mom" routine
- Intent: Audience/persona
- Shape: Persona-led intro → routine by life stage → curated picks → FAQ

**Module order:**
1. `scenario` — persona-led ("The 90-second routine for the mom who doesn't have 10 minutes")
2. `routine` — "The 2-step mom routine" (numbered, actionable)
3. `h2h3s` — "Life-stage adjustments" (pregnancy / postpartum / toddler-chaos / reclaiming-your-glow) — 4 H3s
4. FAQ: "Is this safe to use with kids around?", "Can I use this while breastfeeding?", "Minimum viable routine?"

- [ ] **Step 1-4: Draft → publish → verify → commit**

---

### Task T4.9: Cross-pillar internal linking verification

**Files:** (verification)

- [ ] **Step 1: Extend check_links.py to cover all 15 money pages**

Edit `scripts/check_links.py` to include all 15 slugs (7 PDRN + 4 tallow + 4 crunchy-mom):

```python
ALL_PAGES = [
    "/collections/pdrn-serum", "/collections/pdrn-skincare", "/collections/best-pdrn-serum",
    "/collections/pdrn-eye-cream", "/collections/pdrn-vs-retinol",
    "/collections/clean-korean-skincare", "/collections/vegan-pdrn-serum",
    "/collections/tallow-cream", "/collections/whipped-tallow-face-cream",
    "/collections/best-tallow-cream", "/collections/tallow-cream-for-eczema",
    "/collections/non-toxic-skincare", "/collections/pregnancy-safe-skincare",
    "/collections/seed-oil-free-skincare", "/collections/clean-skincare-for-moms",
]
```

Update the main function to print outbound link counts per page. Each page should have ≥2 intra-pillar links + ≥1 cross-pillar link + ≥1 article link (once P5 ships; for now, article links may be 0).

- [ ] **Step 2: Run and fix any gaps**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 check_links.py
```

Fix gaps by editing the affected collection's `body_modules` and republishing.

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/check_links.py
git commit -m "Extend link check to all 15 money pages and close gaps"
```

---

### Task T4.10: Full schema validation across 15 money pages + sitemap check

**Files:** (verification)

- [ ] **Step 1: Validator loop across all 15**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && for slug in \
  pdrn-serum pdrn-skincare best-pdrn-serum pdrn-eye-cream pdrn-vs-retinol \
  clean-korean-skincare vegan-pdrn-serum \
  tallow-cream whipped-tallow-face-cream best-tallow-cream tallow-cream-for-eczema \
  non-toxic-skincare pregnancy-safe-skincare seed-oil-free-skincare clean-skincare-for-moms; do
  python3 schema_validator.py collection "https://leaf-and-bird.com/collections/$slug" || echo "FAIL: $slug"
done
```

Expected: 15 OK lines. Fix any FAIL by editing the page's body/FAQ and republishing.

- [ ] **Step 2: Verify sitemap coverage**

```bash
curl -s https://leaf-and-bird.com/sitemap.xml | grep -oE "<loc>[^<]+</loc>" | grep collections | sort
```

Confirm all 15 new collection slugs appear in the sitemap output. If missing, wait 5-10 minutes (Shopify refreshes sitemap) and re-check. If still missing, check each collection is `published: true`.

- [ ] **Step 3: Commit phase marker**

```bash
cd /Users/skitch && git commit --allow-empty -m "P4 complete: 15 money pages shipped with schema + sitemap coverage"
```

---

## Phase P5 — Blog Articles (11 tasks)

### Shared pattern for article tasks (T5.2–T5.10)

**Operation A — Draft content locally**
Create `content/articles/<slug>.json`:

```json
{
  "slug": "",
  "blog_id": 91563098411,
  "title": "",
  "body_html": "",
  "excerpt": "",
  "meta_title": "",
  "meta_description": "",
  "primary_keyword": "",
  "faq_json": [{"question": "", "answer": ""}],
  "image_path": "",
  "image_alt": "",
  "tags": "",
  "author": "Leaf & Bird"
}
```

`body_html` structure varies by article shape (defined per task) but always includes:
- Direct-answer opening sentence (LLM extraction-friendly)
- Brand mention in first 300 words: "Leaf & Bird..."
- 3-5 internal links to money pages
- 1-2 internal links to other articles
- FAQ block near the end
- Call-to-action closing routing to a money page

**Operation B — Generate featured image via Gemini**
Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/gen_image.py --article <slug>
```
(See `gen_image.py` in Task T5.1.)

**Operation C — Publish via Admin API**
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 scripts/publish_article.py content/articles/<slug>.json
```
(See `publish_article.py` in Task T5.1.)

**Operation D — Verify on live site**
```bash
curl -sL https://leaf-and-bird.com/blogs/journal/<slug> | grep -oE '<h1[^>]*>[^<]*</h1>'
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 schema_validator.py article "https://leaf-and-bird.com/blogs/journal/<slug>"
```

**Operation E — Commit**
```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/articles/<slug>.json ClaudeCode/leaf-and-bird/images/articles/<slug>.*
git commit -m "Publish article: <slug>"
```

---

### Task T5.1: Create article helpers (`gen_image.py`, `publish_article.py`)

**Files:**
- Create: `scripts/gen_image.py`
- Create: `scripts/publish_article.py`

- [ ] **Step 1: Write Gemini image generator**

Create `scripts/gen_image.py`:

```python
"""Generate a featured image for a blog article using Google Gemini.

Uses Imagen 4.0 via the Gemini API for text-to-image. For product-photo-referenced
images, can also use Gemini 2.5 Flash Image multimodal (pass --ref <path>).
"""
import argparse
import base64
import json
import os
import pathlib
import urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
IMAGEN_MODEL = "imagen-4.0-generate-001"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "images" / "articles"


def generate_imagen(prompt, out_path):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict?key={API_KEY}"
    body = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "16:9"},
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    b64 = data["predictions"][0]["bytesBase64Encoded"]
    out_path.write_bytes(base64.b64decode(b64))
    print(f"Saved {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", required=True, help="Article slug")
    ap.add_argument("--prompt", help="Override prompt (default: derived from draft JSON)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    draft = pathlib.Path(__file__).resolve().parent.parent / "content" / "articles" / f"{args.article}.json"
    d = json.loads(draft.read_text(encoding="utf-8")) if draft.exists() else {}
    prompt = args.prompt or f"Editorial photography for a skincare blog article titled '{d.get('title', args.article)}'. Clean-beauty aesthetic, soft natural light, muted botanical green + warm gray palette, minimalist, luxurious. No text, no typography, no brand logos. 16:9 composition."
    out = OUT_DIR / f"{args.article}.png"
    generate_imagen(prompt, out)
    # Update draft with image_path + a default alt if missing
    if draft.exists():
        d["image_path"] = str(out.relative_to(draft.parent.parent))
        if not d.get("image_alt"):
            d["image_alt"] = f"{d.get('title', args.article)} — featured image"
        draft.write_text(json.dumps(d, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write article publisher**

Create `scripts/publish_article.py`:

```python
"""Publish a drafted article (body, meta, FAQ metafield, featured image) to Shopify blog."""
import base64
import json
import pathlib
import sys
import shopify_api


def publish(draft_path):
    d = json.loads(pathlib.Path(draft_path).read_text(encoding="utf-8"))
    blog_id = d["blog_id"]

    payload = {"article": {
        "title": d["title"],
        "handle": d["slug"],
        "body_html": d["body_html"],
        "author": d.get("author", "Leaf & Bird"),
        "tags": d.get("tags", ""),
        "summary_html": d.get("excerpt", ""),
        "published": True,
    }}

    if d.get("image_path"):
        img_path = pathlib.Path(draft_path).resolve().parent.parent / d["image_path"]
        img_bytes = img_path.read_bytes()
        payload["article"]["image"] = {
            "attachment": base64.b64encode(img_bytes).decode("ascii"),
            "filename": img_path.name,
            "alt": d.get("image_alt", d["title"]),
        }

    # Try create; if exists, update
    existing = shopify_api.get(f"/blogs/{blog_id}/articles.json", params={"handle": d["slug"]})
    articles = existing.get("articles", [])
    if articles:
        aid = articles[0]["id"]
        payload["article"]["id"] = aid
        resp = shopify_api.put(f"/blogs/{blog_id}/articles/{aid}.json", payload)
        print(f"Updated article {aid}: {d['slug']}")
    else:
        resp = shopify_api.post(f"/blogs/{blog_id}/articles.json", payload)
        aid = resp["article"]["id"]
        print(f"Created article {aid}: {d['slug']}")

    # Metafields
    if d.get("faq_json"):
        _upsert(aid, "articles", "seo", "faq_json", "json", json.dumps(d["faq_json"]))
    if d.get("primary_keyword"):
        _upsert(aid, "articles", "seo", "primary_keyword", "single_line_text_field", d["primary_keyword"])
    if d.get("meta_title"):
        _upsert(aid, "articles", "global", "title_tag", "single_line_text_field", d["meta_title"])
    if d.get("meta_description"):
        _upsert(aid, "articles", "global", "description_tag", "multi_line_text_field", d["meta_description"])


def _upsert(owner_id, owner_resource, namespace, key, type_, value):
    existing = shopify_api.get(f"/{owner_resource}/{owner_id}/metafields.json")["metafields"]
    for m in existing:
        if m["namespace"] == namespace and m["key"] == key:
            shopify_api.put(f"/metafields/{m['id']}.json",
                            {"metafield": {"id": m["id"], "value": value, "type": type_}})
            return
    shopify_api.post(f"/{owner_resource}/{owner_id}/metafields.json",
                     {"metafield": {"namespace": namespace, "key": key, "type": type_, "value": value}})


if __name__ == "__main__":
    publish(sys.argv[1])
```

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/gen_image.py ClaudeCode/leaf-and-bird/scripts/publish_article.py
git commit -m "Add Gemini image generator and blog article publisher"
```

---

### Task T5.2: Publish Article 1 — "What Is PDRN? The Complete Guide"

- `slug`: `what-is-pdrn-complete-guide`
- `title`: `What Is PDRN? The Complete Guide for Clean-Beauty Lovers`
- `primary_keyword`: `what is pdrn`
- `meta_title`: `What Is PDRN? A Clean-Beauty Guide (2026) | Leaf & Bird`
- `meta_description`: `PDRN explained: what it is, how it works, why most is salmon-derived (and ours isn't), and what it does for your skin. A complete guide.` (≤160)
- Length: ~1,800-2,200 words
- Shape: Long-form educational pillar
- Opening sentence (LLM-extractable): "PDRN — short for polydeoxyribonucleotide — is a skin-regenerating active originally developed in Korean dermatology and used in topical serums to stimulate fibroblast activity, support skin barrier repair, and boost brightness."
- Required sections (H2s): What is PDRN · How PDRN works on skin · The salmon DNA controversy · Vegan & plant-based PDRN (brand moment) · PDRN benefits · How to use PDRN in your routine · PDRN safety & pregnancy · PDRN vs other actives · FAQ
- Internal links (required): `/collections/pdrn-serum`, `/collections/vegan-pdrn-serum`, `/collections/pdrn-skincare`, `/products/pdrn-brightening-serum`, article #9 (vegan PDRN) — add placeholder if article #9 not yet published; update after T5.10
- FAQ seeds: at least 6 LLM-extraction-ready Q&As

- [ ] **Step 1-5: Draft → generate image → publish → verify → commit (Operations A-E)**

---

### Task T5.3: Publish Article 2 — "Is PDRN Salmon Sperm?"

- `slug`: `is-pdrn-salmon-sperm`
- `title`: `Is PDRN Salmon Sperm? Here's the Honest Answer`
- `primary_keyword`: `is pdrn salmon sperm`
- `meta_title`: `Is PDRN Salmon Sperm? The Honest Answer | Leaf & Bird`
- `meta_description`: `Is PDRN salmon sperm? The honest answer — yes, for most brands. Ours isn't. Here's why it matters and what vegan PDRN looks like.` (≤160)
- Length: ~900-1,100 words
- Shape: Direct-answer Q&A
- Opening sentence: "Yes — most PDRN on the market is derived from salmon DNA, but not all of it. Leaf & Bird's PDRN serum is vegan and salmon-free."
- Structure: Direct answer → salmon-derived PDRN landscape → why it works → the ick factor vs. the ethics/diet factor → our formulation → what to check on any PDRN product label → FAQ
- Internal links: `/collections/vegan-pdrn-serum`, `/collections/pdrn-serum`, `/collections/clean-korean-skincare`, article #1, article #9

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.4: Publish Article 3 — "PDRN vs Retinol"

- `slug`: `pdrn-vs-retinol`
- `title`: `PDRN vs Retinol: Which Is Right for You?`
- `primary_keyword`: `pdrn vs retinol`
- `meta_title`: `PDRN vs Retinol: Which Is Right for Your Skin? | Leaf & Bird`
- `meta_description`: `PDRN vs retinol: efficacy, safety, pregnancy considerations, and how to choose. Includes vegan PDRN alternatives.` (≤160)
- Length: ~1,200-1,500 words
- Shape: Comparison
- Opening: "Both PDRN and retinol improve skin texture and brightness — but they work through completely different mechanisms and suit different people. Here's the full comparison."
- Structure: Comparison table (top) → how each works → who should use each → side effects & risks → pregnancy & breastfeeding → how to choose → our vegan PDRN pick → FAQ
- Internal links: `/collections/pdrn-vs-retinol`, `/collections/pdrn-serum`, `/collections/pregnancy-safe-skincare`, article #1

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.5: Publish Article 4 — "PDRN Benefits for Skin"

- `slug`: `pdrn-benefits-for-skin`
- `title`: `PDRN Benefits for Skin: What the Science Actually Says`
- `primary_keyword`: `pdrn benefits`
- `meta_title`: `PDRN Benefits for Skin: Evidence-Based Guide | Leaf & Bird`
- `meta_description`: `PDRN skin benefits backed by clinical research — brightness, barrier repair, texture, fine-line smoothing, and more. What to expect.` (≤160)
- Length: ~1,100-1,400 words
- Shape: Evidence-based listicle
- Opening: "PDRN delivers five research-supported skin benefits: fibroblast activation, barrier repair, brightening, inflammation reduction, and textural smoothing."
- Structure: Numbered benefit list (5-6) with evidence per benefit + citations → who sees results fastest → application tips → FAQ
- Internal links: `/collections/pdrn-serum`, `/collections/pdrn-skincare`, `/products/pdrn-brightening-serum`, `/collections/pdrn-eye-cream`

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.6: Publish Article 5 — "How to Make Tallow Face Cream (And Why We Stopped)"

- `slug`: `how-to-make-tallow-face-cream`
- `title`: `How to Make Tallow Face Cream (And Why We Stopped Trying)`
- `primary_keyword`: `how to make tallow face cream`
- `meta_title`: `How to Make Tallow Face Cream + Why We Stopped | Leaf & Bird`
- `meta_description`: `A real tallow face cream recipe, plus the honest reason we stopped DIY-ing and started formulating professionally. Grass-fed, whipped, clean.` (≤160)
- Length: ~1,400-1,700 words
- Shape: Recipe-first + narrative pivot
- Opening: "Here's a working tallow face cream recipe: grass-fed tallow, a neutral carrier oil, a few drops of skin-safe essential oil, whipped. Yield: one small jar. Read for the step-by-step — and why we stopped making it at home."
- Structure: Complete recipe (ingredients + steps + shelf life) → what goes wrong at home (separation, rancidity, sourcing grass-fed tallow, food-safe kitchen sanitation) → when DIY makes sense vs. when professional formulation wins → our whipped tallow cream as the "we took the hassle off your plate" pivot → FAQ
- Internal links: `/collections/tallow-cream`, `/collections/whipped-tallow-face-cream`, `/products/tallow-cream-lemongrass-lavender`, `/collections/tallow-cream-for-eczema`

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.7: Publish Article 6 — "Beef Tallow for Skin: Benefits, Science, and What to Look For"

- `slug`: `beef-tallow-for-skin-guide`
- `title`: `Beef Tallow for Skin: Benefits, Science, and What to Look For`
- `primary_keyword`: `beef tallow for skin`
- `meta_title`: `Beef Tallow for Skin — Evidence-Based Guide | Leaf & Bird`
- `meta_description`: `Beef tallow for skin, explained: why it works (hint: lipid biology), what grass-fed means, safety, and how to pick a tallow cream that's actually clean.` (≤160)
- Length: ~1,600-1,900 words
- Shape: Authoritative evergreen guide
- Opening: "Beef tallow has been used on human skin for thousands of years — and modern lipid biology explains why it works so well. Tallow's fatty acid profile closely mirrors the lipids your own skin produces."
- Structure: Ancestral context → fatty acid biology (with citations) → grass-fed vs grain-fed sourcing → safety & allergens → how to choose a tallow product → our whipped approach → FAQ
- Internal links: all 4 tallow money pages, `/collections/non-toxic-skincare`

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.8: Publish Article 7 — "Pregnancy-Safe Skincare"

- `slug`: `pregnancy-safe-skincare-guide`
- `title`: `Pregnancy-Safe Skincare: The Complete Ingredient Avoidance Guide`
- `primary_keyword`: `pregnancy safe skincare`
- `meta_title`: `Pregnancy-Safe Skincare: The Complete Ingredient Guide | Leaf & Bird`
- `meta_description`: `Pregnancy-safe skincare guide: ingredients to avoid (retinoids, salicylic acid, essential oils), what's actually safe, and a trimester routine.` (≤160)
- Length: ~1,400-1,700 words
- Shape: Avoidance guide + recommendations
- Opening: "During pregnancy, avoid retinoids, high-percentage salicylic acid, hydroquinone, certain essential oils, and products with endocrine disruptors. Here's what's safe — and what to use instead."
- Structure: Avoid list with reasoning → safe-to-use list → trimester-by-trimester notes → postpartum & breastfeeding → curated products → FAQ + medical disclaimer
- Internal links: `/collections/pregnancy-safe-skincare`, `/collections/tallow-cream`, `/collections/pdrn-serum` (flag phenoxyethanol in FAQ honestly)

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.9: Publish Article 8 — "Is Korean Skincare Non-Toxic?"

- `slug`: `is-korean-skincare-non-toxic`
- `title`: `Is Korean Skincare Non-Toxic? An Honest Breakdown`
- `primary_keyword`: `non toxic korean skincare`
- `meta_title`: `Is Korean Skincare Non-Toxic? Honest Breakdown | Leaf & Bird`
- `meta_description`: `Is Korean skincare non-toxic? Honestly, it depends. A clean-beauty breakdown of fragrance, preservatives, and how to spot truly clean K-beauty.` (≤160)
- Length: ~1,200-1,500 words
- Shape: Myth-busting essay
- Opening: "Korean skincare isn't automatically non-toxic — it varies by brand and formula. Here's an honest look at fragrance, preservatives, and synthetic actives in K-beauty, plus what clean Korean skincare actually looks like."
- Structure: The complexity up front → fragrance issue → preservative issue → synthetic active question → clean K-beauty brands to know → our PDRN as the clean-K-beauty bridge → FAQ
- Internal links: `/collections/clean-korean-skincare`, `/collections/vegan-pdrn-serum`, `/collections/pdrn-serum`, `/collections/non-toxic-skincare`

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.10: Publish Article 9 — "Is PDRN Vegan?" (flagship)

- `slug`: `is-pdrn-vegan`
- `title`: `Is PDRN Vegan? The Honest Answer (and Why We're the Only One Doing It Clean)`
- `primary_keyword`: `is pdrn vegan`
- `meta_title`: `Is PDRN Vegan? The Honest Answer (2026) | Leaf & Bird`
- `meta_description`: `Is PDRN vegan? Most isn't — it's salmon-derived. Ours is vegan. Here's what vegan PDRN actually means, alternatives, and our honest formulation.` (≤160)
- Length: ~1,200-1,500 words
- Shape: Direct-answer flagship + positioning
- Opening: "Most PDRN is not vegan — it's derived from salmon DNA. Leaf & Bird's PDRN serum is vegan. Here's the full story."
- Structure: Direct answer → salmon-derived PDRN landscape → ethical considerations (ethical vegan / religious / crunchy-mom-clean angles) → plant-based & synthetic PDRN alternatives explained → our formulation → what to check on any label → FAQ → close with strong CTA
- Internal links: `/collections/vegan-pdrn-serum`, `/collections/pdrn-serum`, `/collections/clean-korean-skincare`, `/collections/non-toxic-skincare`, article #2 (salmon sperm)

**Superlative caveat:** If brand owner hasn't verified "the only" claim as of publish, soften title to "the only **clean** PDRN doing it this way" or "...and why vegan PDRN is so rare."

- [ ] **Step 1-5: Draft → image → publish → verify → commit**

---

### Task T5.11: Update article cross-links + pillar linking audit

**Files:**
- Modify: all 9 article JSON drafts (circular links between articles once all exist)

- [ ] **Step 1: Re-edit each article to ensure cross-article internal links point to published slugs**

For each article, add 1-2 internal links to related articles (e.g., article #1 links to #2 and #9; article #9 links to #1 and #2; etc.) if not already present. Update the JSON drafts and re-run `publish_article.py` for each changed file.

- [ ] **Step 2: Verify all 9 article URLs validate**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && for slug in \
  what-is-pdrn-complete-guide is-pdrn-salmon-sperm pdrn-vs-retinol \
  pdrn-benefits-for-skin how-to-make-tallow-face-cream \
  beef-tallow-for-skin-guide pregnancy-safe-skincare-guide \
  is-korean-skincare-non-toxic is-pdrn-vegan; do
  python3 schema_validator.py article "https://leaf-and-bird.com/blogs/journal/$slug" || echo "FAIL: $slug"
done
```

- [ ] **Step 3: Verify each money page now has ≥1 article link (update check_links.py threshold)**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 check_links.py
```

- [ ] **Step 4: Commit phase marker**

```bash
cd /Users/skitch && git commit --allow-empty -m "P5 complete: 9 cornerstone articles published with cross-linking"
```

---

## Phase P6 — Navigation, Submission, Final Checks (5 tasks)

### Task T6.1: Update main navigation with new money pages

**Files:** (uses Shopify Admin API — menus are JSON linksets)

- [ ] **Step 1: List current menus**

Run:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
import json
# Menu management via REST is limited in older API versions; use GraphQL for Online Store 2.0 menus.
# This snippet lists current menus for review.
q = {'query':'{ menus(first:20) { edges { node { id handle title items { title url } } } } }'}
print(json.dumps(s.post('/graphql.json' if False else '/../graphql.json', q), indent=2)[:2000])"
```

If REST GraphQL helper doesn't work, use the dedicated GraphQL endpoint: `https://leaf-and-bird.myshopify.com/admin/api/2024-10/graphql.json`. Add a helper function in `shopify_api.py` if needed:

```python
def graphql(query, variables=None):
    url = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

Then query:
```graphql
{ menus(first: 20) { edges { node { id handle title items { title url } } } } }
```

- [ ] **Step 2: Add key money pages to main-menu**

Using GraphQL `menuUpdate` mutation (or the Shopify Admin UI — acceptable fallback if GraphQL mutation is gated behind scopes), add these menu items under the Shop/Collections parent:

- PDRN Serum → `/collections/pdrn-serum`
- Vegan PDRN → `/collections/vegan-pdrn-serum`
- Tallow Cream → `/collections/tallow-cream`
- Non-Toxic Skincare → `/collections/non-toxic-skincare`
- Pregnancy-Safe → `/collections/pregnancy-safe-skincare`

And under a Blog menu item (if present), link The Journal → `/blogs/journal`.

- [ ] **Step 3: Verify live nav**

```bash
curl -sL https://leaf-and-bird.com/ | grep -oE 'href="/collections/[^"]+"' | sort -u
```

Expected: the 5 new nav collections appear at minimum.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git commit --allow-empty -m "Update main nav to surface key money pages"
```

---

### Task T6.2: IndexNow ping (Bing + Yandex)

**Files:**
- Create: `scripts/indexnow_ping.py`

- [ ] **Step 1: Generate an IndexNow key**

Generate a 32-char hex key:
```bash
python3 -c "import secrets; print(secrets.token_hex(16))"
```

Record the key in `NOTES.md` (do not commit to git — store in local notes only). Then create a Shopify page or asset hosting this key as plain text at `/<key>.txt`.

Simplest: upload to theme assets:
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird && python3 -c "
import scripts.shopify_api as s
key = '<your-key-here>'
# Create asset at assets/<key>.txt (accessible via CDN)
body = {'asset': {'key': f'assets/{key}.txt', 'value': key}}
print(s.put('/themes/186309509419/assets.json', body))"
```

Note: Shopify CDN asset URLs include a hash — IndexNow requires the exact key file at `<host>/<key>.txt`. If Shopify asset URLs don't satisfy this, instead create a Shopify Page whose URL is `/pages/<key>-txt` and redirect `/<key>.txt` → `/pages/<key>-txt`. Or use a simpler alternative: submit via search engine webmaster tools directly.

- [ ] **Step 2: Write the ping script**

Create `scripts/indexnow_ping.py`:

```python
"""Ping IndexNow with our new URLs."""
import json
import os
import urllib.request

KEY = os.environ.get("INDEXNOW_KEY", "")  # never hardcode
HOST = "leaf-and-bird.com"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

URLS = [
    # 15 money pages
    "https://leaf-and-bird.com/collections/pdrn-serum",
    "https://leaf-and-bird.com/collections/pdrn-skincare",
    "https://leaf-and-bird.com/collections/best-pdrn-serum",
    "https://leaf-and-bird.com/collections/pdrn-eye-cream",
    "https://leaf-and-bird.com/collections/pdrn-vs-retinol",
    "https://leaf-and-bird.com/collections/clean-korean-skincare",
    "https://leaf-and-bird.com/collections/vegan-pdrn-serum",
    "https://leaf-and-bird.com/collections/tallow-cream",
    "https://leaf-and-bird.com/collections/whipped-tallow-face-cream",
    "https://leaf-and-bird.com/collections/best-tallow-cream",
    "https://leaf-and-bird.com/collections/tallow-cream-for-eczema",
    "https://leaf-and-bird.com/collections/non-toxic-skincare",
    "https://leaf-and-bird.com/collections/pregnancy-safe-skincare",
    "https://leaf-and-bird.com/collections/seed-oil-free-skincare",
    "https://leaf-and-bird.com/collections/clean-skincare-for-moms",
    # 9 articles
    "https://leaf-and-bird.com/blogs/journal/what-is-pdrn-complete-guide",
    "https://leaf-and-bird.com/blogs/journal/is-pdrn-salmon-sperm",
    "https://leaf-and-bird.com/blogs/journal/pdrn-vs-retinol",
    "https://leaf-and-bird.com/blogs/journal/pdrn-benefits-for-skin",
    "https://leaf-and-bird.com/blogs/journal/how-to-make-tallow-face-cream",
    "https://leaf-and-bird.com/blogs/journal/beef-tallow-for-skin-guide",
    "https://leaf-and-bird.com/blogs/journal/pregnancy-safe-skincare-guide",
    "https://leaf-and-bird.com/blogs/journal/is-korean-skincare-non-toxic",
    "https://leaf-and-bird.com/blogs/journal/is-pdrn-vegan",
    # Key pages
    "https://leaf-and-bird.com/llms.txt",
    "https://leaf-and-bird.com/llms-full.txt",
]


def ping():
    body = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URLS,
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/IndexNow",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        print(f"HTTP {resp.status}  |  {resp.read().decode('utf-8', errors='replace')[:200]}")


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("Set INDEXNOW_KEY env var first.")
    ping()
```

- [ ] **Step 3: Run ping**

```bash
export INDEXNOW_KEY="<your-key>"
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 indexnow_ping.py
```

Expected: `HTTP 200` or `HTTP 202`. If 403: key file is unreachable at `https://leaf-and-bird.com/<key>.txt` — fix hosting.

- [ ] **Step 4: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/indexnow_ping.py
git commit -m "Add IndexNow ping for Bing/Yandex discovery of new URLs"
```

---

### Task T6.3: Google Search Console sitemap resubmission (user action)

**Files:**
- Create: `content/gsc-submission-instructions.md`

- [ ] **Step 1: Write submission instructions for the user**

Create `content/gsc-submission-instructions.md`:

```markdown
# Google Search Console Resubmission — Action Required

## 1. Verify property ownership
- Open https://search.google.com/search-console/
- Confirm `leaf-and-bird.com` (or `https://leaf-and-bird.com/`) is listed as a verified property
- If not, add it and verify via DNS TXT or Shopify-provided HTML file

## 2. Submit the sitemap
- In Search Console → Sitemaps → "Add a new sitemap"
- Enter: `sitemap.xml`
- Click Submit

## 3. Request indexing on 5 priority pages
For each URL below, use URL Inspection → "Request Indexing":

- https://leaf-and-bird.com/collections/pdrn-serum
- https://leaf-and-bird.com/collections/vegan-pdrn-serum
- https://leaf-and-bird.com/collections/tallow-cream
- https://leaf-and-bird.com/collections/non-toxic-skincare
- https://leaf-and-bird.com/blogs/journal/what-is-pdrn-complete-guide

## 4. Check indexation (7-14 days later)
- Coverage report → "Pages" tab
- Confirm all 15 money pages + 9 articles show "Indexed"
- If any show "Discovered — currently not indexed," request indexing manually
```

- [ ] **Step 2: Surface to user explicitly**

Print in the agent's output:
> "Phase P6 requires your manual action: follow `content/gsc-submission-instructions.md` to submit the sitemap to Google Search Console. Ping me when done."

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/gsc-submission-instructions.md
git commit -m "Document Google Search Console submission steps for user"
```

---

### Task T6.4: Final site-wide schema + SEO sanity sweep

**Files:**
- Create: `scripts/site_sanity.py`

- [ ] **Step 1: Write the sanity-check script**

Create `scripts/site_sanity.py`:

```python
"""Crawl the 24 new Leaf & Bird URLs and run a battery of SEO/schema checks."""
import re
import sys
import urllib.request
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema_validator import validate_collection_page, validate_article_page, validate_product_page

URLS = [
    ("collection", "https://leaf-and-bird.com/collections/pdrn-serum"),
    ("collection", "https://leaf-and-bird.com/collections/pdrn-skincare"),
    ("collection", "https://leaf-and-bird.com/collections/best-pdrn-serum"),
    ("collection", "https://leaf-and-bird.com/collections/pdrn-eye-cream"),
    ("collection", "https://leaf-and-bird.com/collections/pdrn-vs-retinol"),
    ("collection", "https://leaf-and-bird.com/collections/clean-korean-skincare"),
    ("collection", "https://leaf-and-bird.com/collections/vegan-pdrn-serum"),
    ("collection", "https://leaf-and-bird.com/collections/tallow-cream"),
    ("collection", "https://leaf-and-bird.com/collections/whipped-tallow-face-cream"),
    ("collection", "https://leaf-and-bird.com/collections/best-tallow-cream"),
    ("collection", "https://leaf-and-bird.com/collections/tallow-cream-for-eczema"),
    ("collection", "https://leaf-and-bird.com/collections/non-toxic-skincare"),
    ("collection", "https://leaf-and-bird.com/collections/pregnancy-safe-skincare"),
    ("collection", "https://leaf-and-bird.com/collections/seed-oil-free-skincare"),
    ("collection", "https://leaf-and-bird.com/collections/clean-skincare-for-moms"),
    ("article", "https://leaf-and-bird.com/blogs/journal/what-is-pdrn-complete-guide"),
    ("article", "https://leaf-and-bird.com/blogs/journal/is-pdrn-salmon-sperm"),
    ("article", "https://leaf-and-bird.com/blogs/journal/pdrn-vs-retinol"),
    ("article", "https://leaf-and-bird.com/blogs/journal/pdrn-benefits-for-skin"),
    ("article", "https://leaf-and-bird.com/blogs/journal/how-to-make-tallow-face-cream"),
    ("article", "https://leaf-and-bird.com/blogs/journal/beef-tallow-for-skin-guide"),
    ("article", "https://leaf-and-bird.com/blogs/journal/pregnancy-safe-skincare-guide"),
    ("article", "https://leaf-and-bird.com/blogs/journal/is-korean-skincare-non-toxic"),
    ("article", "https://leaf-and-bird.com/blogs/journal/is-pdrn-vegan"),
]


def checks_for(kind, url):
    html = urllib.request.urlopen(url).read().decode("utf-8", errors="replace")
    probs = []
    # Schema
    try:
        if kind == "collection": validate_collection_page(html)
        elif kind == "article": validate_article_page(html)
        elif kind == "product": validate_product_page(html)
    except Exception as e:
        probs.append(f"schema: {e}")
    # H1 present, 1 only
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if len(h1s) != 1:
        probs.append(f"h1 count = {len(h1s)}")
    # Meta description present
    if not re.search(r'<meta name="description" content="[^"]{20,}"', html):
        probs.append("missing or short meta description")
    # Canonical present
    if not re.search(r'rel="canonical"[^>]+href="[^"]+"', html):
        probs.append("missing canonical")
    # OG image is HTTPS
    if re.search(r'property="og:image"[^>]+content="http://', html):
        probs.append("og:image is http://")
    # At least 2 internal collection links
    collection_links = set(re.findall(r'href="(/collections/[^"#?]+)"', html))
    if len(collection_links) < 2:
        probs.append(f"only {len(collection_links)} internal collection links")
    return probs


def main():
    any_problems = False
    for kind, url in URLS:
        probs = checks_for(kind, url)
        status = "OK" if not probs else "ISSUES"
        print(f"{status:8}  {url}")
        for p in probs:
            print(f"          - {p}")
            any_problems = True
    sys.exit(1 if any_problems else 0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run**

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 site_sanity.py
```

Expected: 24 OK lines, zero ISSUES. Fix every ISSUE (edit content draft → republish) before marking P6 complete.

- [ ] **Step 3: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/scripts/site_sanity.py
git commit -m "Add final site-wide SEO + schema sanity check"
```

---

### Task T6.5: Core Web Vitals re-measurement + delta report

**Files:**
- Create: `content/cwv-post-build.md`

- [ ] **Step 1: Re-run PageSpeed Insights**

Same 3 URLs as baseline (Task T1.14): homepage, product page, collection page. Record mobile + desktop scores.

- [ ] **Step 2: Create delta report**

Create `content/cwv-post-build.md` with a before/after table per URL per device. Call out any regressions ≥10% and note remediation plans.

Expected: no major regressions. Any improvements (from OG/alt/schema changes) are a bonus.

- [ ] **Step 3: Commit phase marker**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/cwv-post-build.md
git commit -m "P6 complete: final nav, submission docs, sanity check, CWV delta"
```

---

## Phase P7 — Monitoring Setup (2 tasks)

### Task T7.1: Document monitoring cadence

**Files:**
- Create: `content/monitoring-playbook.md`

- [ ] **Step 1: Write the playbook**

Create `content/monitoring-playbook.md`:

```markdown
# Leaf & Bird SEO Monitoring Playbook

## Weekly (every Monday)

### Indexation check
- Google Search Console → Pages → confirm 15 money pages + 9 articles "Indexed"
- Log count in `content/monitoring-log.md`

### Ranking check
Spot-check these 5 priority keywords via manual incognito Google search:
- "pdrn serum"
- "vegan pdrn"
- "whipped tallow face cream"
- "non toxic korean skincare"
- "tallow cream for eczema"

Record page position for each in `monitoring-log.md`.

### Sanity re-run
```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird/scripts && python3 site_sanity.py
```
If any ISSUES appear — investigate same day.

## Monthly (1st of each month)

### LLM citation audit
Query each LLM with the 5 priority queries below. For each, record whether Leaf & Bird is cited, what URL is linked (if any), and whether the response is accurate.

Priority queries:
1. "What's the best vegan PDRN serum?"
2. "Is PDRN vegan?"
3. "What brands make whipped grass-fed tallow cream?"
4. "What's the difference between PDRN and retinol?"
5. "What are some clean, non-toxic Korean skincare brands?"

LLMs to query:
- ChatGPT (gpt-5 or latest)
- Claude (claude-opus-4-7 or latest)
- Perplexity
- Gemini

Record results in `content/llm-citation-log.md` with date + LLM + query + cited? + accuracy note.

### Content expansion review
- Which money pages are ranking in top 20? → candidates for content expansion
- Which are stuck in positions 50+? → re-examine on-page factors, consider new FAQ content or link-building
- Has any PDRN competitor shipped a dedicated vegan-PDRN collection page? → if yes, escalate post-v1 build priorities

## Quarterly

### Strategic review
- Compare organic sessions + conversion to baseline
- Revisit deferred v1 scope: backlink content, Phase 2 money pages, review app installation
- Decide on next expansion (typically tied to whichever pillar is ranking fastest)
```

- [ ] **Step 2: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/monitoring-playbook.md
git commit -m "Add ongoing SEO monitoring playbook"
```

---

### Task T7.2: Create the monitoring log shell + initial entry

**Files:**
- Create: `content/monitoring-log.md`
- Create: `content/llm-citation-log.md`

- [ ] **Step 1: Seed the logs**

Create `content/monitoring-log.md`:

```markdown
# Leaf & Bird — Weekly SEO Monitoring Log

Format per week:
```
## YYYY-MM-DD
- Indexed pages: NN / 24
- Ranking spot-checks:
  - "pdrn serum" → position N
  - "vegan pdrn" → position N
  - "whipped tallow face cream" → position N
  - "non toxic korean skincare" → position N
  - "tallow cream for eczema" → position N
- site_sanity.py: OK / N issues
- Notes:
```

## 2026-04-16 (build-completion snapshot)
- Indexed pages: 0 / 24 (just published — allow 7-14 days)
- Ranking spot-checks: N/A (too early)
- site_sanity.py: OK (24 URLs)
- Notes: v1 build complete. First ranking check scheduled for 2026-04-23.
```

Create `content/llm-citation-log.md`:

```markdown
# Leaf & Bird — Monthly LLM Citation Audit Log

Format per month (one heading per LLM × query):
```
## YYYY-MM (LLM name)
- "What's the best vegan PDRN serum?" → cited YES/NO, URL: ..., accuracy: (notes)
- "Is PDRN vegan?" → cited YES/NO, URL: ..., accuracy: (notes)
- "What brands make whipped grass-fed tallow cream?" → ...
- "What's the difference between PDRN and retinol?" → ...
- "What are some clean, non-toxic Korean skincare brands?" → ...
```

## 2026-05-01 (target — first audit, 2 weeks post-launch)
_To be filled._
```

- [ ] **Step 2: Commit**

```bash
cd /Users/skitch && git add ClaudeCode/leaf-and-bird/content/monitoring-log.md ClaudeCode/leaf-and-bird/content/llm-citation-log.md
git commit -m "Seed monitoring + LLM citation logs"
```

---

## Self-Review (completed inline by planning author)

**Spec coverage check:**
- §1 Executive Summary → covered by the entire plan (P0-P7)
- §2 Goals → tracked by success metrics in P7 monitoring
- §3 Strategic Overview → embedded in task content specs (voice, brand identity line, approach A)
- §4 Money Page Architecture → Tasks T3.1-T3.7 + T4.1-T4.8 (all 15 pages)
- §5 Product Page Optimization → Tasks T2.1-T2.9 (all 9 products) + T2.10 (schema verify) + T2.0 (publisher)
- §6 Blog Content Strategy → Tasks T5.2-T5.10 (all 9 articles) + T5.1 (helpers) + T5.11 (cross-links)
- §7 Tech SEO + Schema Strategy → Tasks T0.4 (audit), T1.1-T1.9, T1.12, T1.13
- §8 AI/LLM Discoverability → Tasks T1.8 (robots.txt), T1.10 (/llms.txt), T1.11 (/llms-full.txt), T1.1 (schema entity anchoring)
- §9 Content Production Workflow → plan header + README (T0.7) + helpers (T2.0, T3.0, T5.1)
- §10 Sequencing → reflected in task ordering P0→P7
- §11 Success Metrics → Task T7.1 monitoring playbook
- §12 Out of Scope → not implemented (correctly omitted)

**Placeholder scan:** No "TBD", "implement later", "fill in details" remain. Every task has explicit values (slugs, keywords, meta text, module orders, product IDs).

**Type consistency:**
- Metafield namespaces (`seo.faq_json`, `seo.h1`, `seo.intro`, `seo.body_modules`, `seo.meta_title`, `seo.meta_description`, `seo.primary_keyword`, `seo.free_from`) are consistent between T0.6 (creation), T1.1 (snippet consumption), T1.9 (section rendering), T2.0 (product publisher), T3.0 (collection publisher), T5.1 (article publisher).
- Module types in `body_modules` (`h2h3s`, `table`, `ingredient`, `routine`, `myths`, `scenario`, `quote`, `ranked_list`, `prosCons`, `trust`, `intro`) are consistently referenced across task-level module-order prescriptions. The Liquid snippet in T1.9 renders whatever `module.type` resolves to as a CSS class — any typed module will render, so diversity is enforced at the draft level, not the rendering level.
- Live theme ID `186309509419` referenced consistently in `pull_theme.py` (T0.2), `upload_asset.py` (T1.2), `indexnow_ping.py` asset step (T6.2).
- Blog ID `91563098411` referenced in publish_article.py (T5.1) — matches the audit output from preflight.

**Scope check:** 68 tasks, scoped to a single cohesive v1. No decomposition needed — phases interdepend tightly, multi-plan split would cause thrash.

**Known gaps explicitly deferred (per spec §12):** backlink distribution, Phase-2 money pages, email capture, review app installation. Not plan gaps.

---

## Execution Handoff

Plan complete and saved to `/Users/skitch/ClaudeCode/leaf-and-bird/docs/superpowers/plans/2026-04-16-leaf-and-bird-seo-v1.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — Each task runs in a fresh subagent; two-stage review between tasks; fastest iteration on content quality and fastest catch for bugs.

**2. Inline Execution** — Tasks run in this session using `superpowers:executing-plans`; batch checkpoints for your review.

Which approach do you want to use?



