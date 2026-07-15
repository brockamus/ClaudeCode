"""Wire up rich bundle PDPs:
1. Push 3 new sections to live theme
2. Define lb_bundle metafield definitions (components, ritual, synergy_html)
3. Populate per-bundle data
4. Update product.bundle.json to include the 3 new sections
"""
import os
import json, urllib.request, copy

TOKEN = os.environ["SHOPIFY_TOKEN"]  # source scripts/.env first
SHOP = "leaf-and-bird.myshopify.com"
GQL = f"https://{SHOP}/admin/api/2024-10/graphql.json"
THEME_REST = f"https://{SHOP}/admin/api/2024-10/themes/186951631147/assets.json"


def gql(q, v=None):
    body = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(GQL, data=body, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def push_asset(key, value):
    body = json.dumps({"asset": {"key": key, "value": value}}).encode()
    req = urllib.request.Request(THEME_REST, data=body, method="PUT",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def fetch_asset(key):
    req = urllib.request.Request(f"{THEME_REST}?asset%5Bkey%5D={key.replace('/','%2F')}",
        headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["asset"]["value"]


# ─── Phase 1: push new sections ───
print("Phase 1: pushing new sections…")
for fname in ("lb-bundle-components.liquid", "lb-bundle-ritual.liquid", "lb-bundle-synergy.liquid"):
    content = open(f"/Users/skitch/ClaudeCode/leaf-and-bird/theme-working/sections/{fname}").read()
    s = push_asset(f"sections/{fname}", content)
    print(f"  sections/{fname}  status={s}")

# ─── Phase 2: define metafields ───
print("\nPhase 2: defining metafield definitions…")
defs = [
    ("components", "list.single_line_text_field", "Components",
     "Ordered list of component product handles (e.g., pdrn-brightening-serum)"),
    ("ritual", "json", "Ritual",
     'JSON: {"am":[{product,label,action}],"pm":[...],"notes":"..."}'),
    ("synergy_html", "multi_line_text_field", "Synergy HTML",
     "How they work together — rich HTML allowed via <p>, <strong>, etc."),
]

m = """mutation ($d: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $d) {
    createdDefinition { id key namespace name }
    userErrors { field message code }
  }
}"""
for key, ftype, name, desc in defs:
    r = gql(m, {"d": {
        "namespace": "lb_bundle", "key": key, "name": name, "description": desc,
        "ownerType": "PRODUCT", "type": ftype,
    }})
    res = r["data"]["metafieldDefinitionCreate"]
    if res["userErrors"]:
        # Already exists — that's fine
        if any("TAKEN" in (e.get("code") or "") for e in res["userErrors"]):
            print(f"  lb_bundle.{key}: already exists ✓")
        else:
            print(f"  lb_bundle.{key}: ERR {res['userErrors']}")
    else:
        print(f"  lb_bundle.{key}: created ({res['createdDefinition']['id']})")

# ─── Phase 3: populate per-bundle data ───
print("\nPhase 3: populating per-bundle metafields…")

BUNDLE_DATA = {
    10356476838187: {  # First Drop Duo
        "components": ["vitamin-glow-serum", "tallow-cream-lemongrass-lavender"],
        "ritual": {
            "am": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "2-3 drops on clean skin, press in until absorbed."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "Small swipe over still-damp skin to seal in hydration."}
            ],
            "pm": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "Same routine as morning — gentle enough for twice-daily."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "Layer on, especially on dry patches around the nose, mouth, jaw."}
            ],
            "notes": "Both pregnancy-safe. The whole routine takes under 60 seconds."
        },
        "synergy_html": "<p>Vit Glow lifts pigment and supports collagen with a non-irritating multi-active (3-O-ethyl ascorbic acid). Tallow's saturated and omega-rich profile rebuilds the lipid barrier and locks the active in.</p><p>Together: visible glow without the irritation cycle that drives so many people away from \"actives.\" Two products, four ingredients between them, real result.</p>",
    },
    10355718947115: {  # Radiance Bundle
        "components": ["dead-sea-mud", "vitamin-glow-serum", "sleep-plus-collagen-cream"],
        "ritual": {
            "am": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "2-3 drops on clean skin. Always finish with SPF."}
            ],
            "pm": [
                {"product": "dead-sea-mud", "label": "Dead Sea Mud Mask",
                 "action": "1-2x per week — apply to damp skin, leave 10 minutes, rinse."},
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "On non-mask nights (or after rinsing the mask off), apply 2-3 drops."},
                {"product": "sleep-plus-collagen-cream", "label": "Sleep Plus Collagen Cream",
                 "action": "Press over the serum. The 10pm-2am peak repair window does the work."}
            ],
            "notes": "Pregnancy note: Sleep Plus contains low-dose melatonin and lavender oil. If you're pregnant, see The Pregnancy-Safe Edit instead."
        },
        "synergy_html": "<p><strong>Mask, brighten, restore.</strong> Dead Sea minerals draw out impurities and prime the skin to absorb. Vit Glow lifts pigment overnight without irritation. Sleep Plus does the cellular work in your peak repair window.</p><p>The cycle compounds. Most users feel new-skin softness in week one and see even-toned glow in 3-4 weeks.</p>",
    },
    10356516913451: {  # Hydrate & Restore
        "components": ["pdrn-brightening-serum", "tallow-cream-lemongrass-lavender", "peptide-eye-gel-cream"],
        "ritual": {
            "am": [
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "3-4 drops on clean skin. Press in, don't rub."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Pea-sized amount, tap around the orbital bone with a fingertip."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "Small swipe over still-damp skin to seal. Then SPF."}
            ],
            "pm": [
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "Same as AM — cellular renewal works overnight."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Tap around the orbital bone."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "More generous than AM. The barrier rebuilds while you sleep."}
            ],
            "notes": "Whole routine is pregnancy-safe at this dosage."
        },
        "synergy_html": "<p>PDRN signals cellular turnover (the K-beauty mechanism, made vegan and pregnancy-safe). Tallow restores the lipid barrier with a saturated/omega match no plant cream can mimic. Eye gel addresses the thinnest, most reactive skin with peptides — not the stimulants that puff and rebound.</p><p>The trio handles repair (PDRN), barrier (tallow), and the eye area (peptide gel) without overlap or conflict. Layer in this order — thinnest to thickest — and you won't pill or compete.</p>",
    },
    10356479787307: {  # Brightening Set
        "components": ["pdrn-brightening-serum", "vitamin-glow-serum", "vitamin-c-serum"],
        "ritual": {
            "am": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "Start here daily. 2-3 drops on clean skin."},
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "Layer over the Vit Glow. Press in."},
                {"label": "SPF (always)",
                 "action": "Vitamin C derivatives are sun-sensitive. Don't skip the sunscreen."}
            ],
            "pm": [
                {"product": "vitamin-c-serum", "label": "Vitamin C Serum (2-3x/week)",
                 "action": "Once skin is tolerant, swap Vit Glow for Vit C in the evening 2-3 nights/week. L-AA + ferulic does intensive spot work."},
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "Layer over. Cellular signaling pairs well with vitamin C."}
            ],
            "notes": "Build tolerance gradually. Start with Vit Glow daily for 2-3 weeks before introducing Vit C. If you flush or sting, drop the L-AA for a week and resume slowly."
        },
        "synergy_html": "<p>Brightening works through three different mechanisms: pigment-lift, melanin inhibition, and cellular turnover. This trio gives you each.</p><p>Vit Glow (3-O-ethyl ascorbic acid) is the daily-tolerant entry. Vit C Serum (L-AA + MAP + 3-glyceryl ascorbate + ferulic) is the heavy-hitter for established marks. PDRN underneath provides the cellular foundation that makes the other two more effective.</p><p>Start gentle, graduate as tolerated. SPF every morning is non-negotiable — vitamin C derivatives oxidize in UV.</p>",
    },
    10356481655083: {  # Pregnancy-Safe Edit
        "components": ["tallow-cream-lemongrass-lavender", "peptide-eye-gel-cream", "vitamin-glow-serum"],
        "ritual": {
            "am": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "2-3 drops on clean skin. Press in, don't rub."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Pea-sized amount around the orbital bone."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "Small swipe over still-damp skin. Finish with SPF."}
            ],
            "pm": [
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Tap around the orbital bone."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "More generous than AM. Barrier-repair while you sleep."}
            ],
            "notes": "Always confirm with your OB before introducing new actives during pregnancy. We've avoided retinoids, salicylates above 2%, hydroquinone, and L-AA in this edit, but every body is different."
        },
        "synergy_html": "<p><strong>Built around what's pregnancy-safe by every common standard.</strong></p><p>3-O-ethyl ascorbic acid (Vitamin Glow) instead of L-AA — same brightening pathway, no irritation. Acetyl Tetrapeptide-5 (Eye Gel-Cream) instead of retinoids — addresses fine lines without the off-limits actives. 3-ingredient grass-fed tallow — saturated/omega-rich barrier repair, no salicylates, no seed oils.</p><p>This is the routine we'd hand a pregnant friend asking \"what can I actually use?\"</p>",
    },
    10356483391787: {  # Tallow Trio
        "components": ["tallow-cream-lemongrass-lavender", "tallow-cream-orange-bergamot", "tallow-cream-peaceful-night"],
        "ritual": {
            "am": [
                {"product": "tallow-cream-orange-bergamot", "label": "Orange & Bergamot",
                 "action": "Bright citrus scent for daytime. Apply to damp skin. SPF afterward (bergamot can be photosensitizing)."}
            ],
            "pm": [
                {"product": "tallow-cream-lemongrass-lavender", "label": "Lemongrass & Lavender",
                 "action": "The all-rounder. Apply generously to damp skin before bed if Lemongrass is your mood."},
                {"product": "tallow-cream-peaceful-night", "label": "Peaceful Night",
                 "action": "Fir + lavender, woodsy and grounding. Apply before bed when you want a deeper repair scent."}
            ],
            "notes": "Match the scent to the moment. All three are interchangeable as moisture seals — pick what your nose wants that day. Same 3-ingredient formula across all three."
        },
        "synergy_html": "<p><strong>Same formula. Three moods.</strong></p><p>Three ingredients: grass-fed beef tallow, organic jojoba oil, essential oils. The differences are the scent profile and use case. Bergamot is the daytime brightener. Lemongrass &amp; Lavender is the universal all-rounder. Peaceful Night is the woodsy overnight repair.</p><p>No seed oils (no soy, sunflower, canola). No emulsifiers, no preservatives, no synthetic fragrance. The skincare your great-grandmother might have made.</p>",
    },
    10356485128491: {  # Anti-Aging Stack
        "components": ["pdrn-brightening-serum", "peptide-eye-gel-cream", "sleep-plus-collagen-cream"],
        "ritual": {
            "am": [
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "3-4 drops on clean skin. Press in."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Tap around the orbital bone — where lines settle first."},
                {"label": "SPF (always)",
                 "action": "UV undoes everything else. Don't skip."}
            ],
            "pm": [
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "Same as AM."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Around the orbital bone."},
                {"product": "sleep-plus-collagen-cream", "label": "Sleep Plus Collagen Cream",
                 "action": "Press over the serum. Plant collagen + lavender + a touch of melatonin for the 10pm-2am repair window."}
            ],
            "notes": "Pregnancy note: Sleep Plus contains low-dose melatonin. See The Pregnancy-Safe Edit if pregnant."
        },
        "synergy_html": "<p><strong>Anti-aging via signaling and repair, not aggressive actives.</strong></p><p>The high-strength retinoid + acid stack route drives short-term gains but creates barrier damage that catches up. Cellular signaling (PDRN) and peptide repair (Eye Gel, Sleep Plus) work in the body's own repair pathways — slower visible change but more durable, less rebound.</p><p>Most users see meaningful change in 6-8 weeks of consistent use, not 2 weeks of glow that costs you skin barrier.</p>",
    },
    10356487029035: {  # Full Ritual
        "components": ["vitamin-glow-serum", "pdrn-brightening-serum", "peptide-eye-gel-cream",
                       "tallow-cream-lemongrass-lavender", "sleep-plus-collagen-cream"],
        "ritual": {
            "am": [
                {"product": "vitamin-glow-serum", "label": "Vitamin Glow Serum",
                 "action": "2-3 drops on clean skin."},
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "Layer over the Vit Glow."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Tap around the orbital bone."},
                {"product": "tallow-cream-lemongrass-lavender", "label": "Tallow Cream",
                 "action": "Small swipe over damp skin to seal."},
                {"label": "SPF (always)",
                 "action": "Antioxidants + sunscreen is the daytime defense layer."}
            ],
            "pm": [
                {"product": "pdrn-brightening-serum", "label": "PDRN Serum",
                 "action": "3-4 drops on clean skin."},
                {"product": "peptide-eye-gel-cream", "label": "Peptide Eye Gel-Cream",
                 "action": "Around the orbital bone."},
                {"product": "sleep-plus-collagen-cream", "label": "Sleep Plus Collagen Cream",
                 "action": "Layered over. Restoration phase."}
            ],
            "notes": "Pregnancy note: Sleep Plus contains melatonin. If pregnant, swap to The Pregnancy-Safe Edit. Want a custom version? Email us — we'll pull Sleep Plus and credit the difference."
        },
        "synergy_html": "<p><strong>The founder's complete routine.</strong></p><p>Five products covering the full daily arc — antioxidant brightening (Vit Glow), cellular signaling (PDRN), peptide eye care (Eye Gel-Cream), ancestral barrier seal (Tallow), and overnight collagen support (Sleep Plus).</p><p>Designed to compound over 8-12 weeks. Brightness comes first, then evenness, then barrier-strength, then the fine-line work. This is what a good routine produces — durable change, not 2-week glow that costs your skin.</p>",
    },
}

# Set metafields via productUpdate mutation
m = """mutation ($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id key namespace ownerType }
    userErrors { field message code }
  }
}"""

for pid, data in BUNDLE_DATA.items():
    metas = [
        {"ownerId": f"gid://shopify/Product/{pid}", "namespace": "lb_bundle",
         "key": "components", "type": "list.single_line_text_field",
         "value": json.dumps(data["components"])},
        {"ownerId": f"gid://shopify/Product/{pid}", "namespace": "lb_bundle",
         "key": "ritual", "type": "json",
         "value": json.dumps(data["ritual"])},
        {"ownerId": f"gid://shopify/Product/{pid}", "namespace": "lb_bundle",
         "key": "synergy_html", "type": "multi_line_text_field",
         "value": data["synergy_html"]},
    ]
    r = gql(m, {"metafields": metas})
    res = r["data"]["metafieldsSet"]
    errs = res.get("userErrors") or []
    if errs:
        print(f"  pid={pid} ERR {errs[:3]}")
    else:
        print(f"  pid={pid}  set {len(res.get('metafields') or [])} fields")

# ─── Phase 4: update product.bundle.json template ───
print("\nPhase 4: updating product.bundle.json to add new sections…")
raw = fetch_asset("templates/product.bundle.json")
tpl = json.loads(raw)

# Insert 3 new sections after shop-product-details, before scrolling-features-bar
new_sections = {
    "lb_bundle_components_lb01": {
        "type": "lb-bundle-components",
        "settings": {"heading": "What's in this set", "subheading": "Layer-tested for the ritual."},
    },
    "lb_bundle_synergy_lb01": {
        "type": "lb-bundle-synergy",
        "settings": {"eyebrow": "WHY THIS COMBINATION", "heading": "How they work together"},
    },
    "lb_bundle_ritual_lb01": {
        "type": "lb-bundle-ritual",
        "settings": {"heading": "Your ritual", "subheading": "When and how to use each product."},
    },
}

# Add to sections dict
for k, v in new_sections.items():
    tpl["sections"][k] = v

# Reorder: shop-product-details → components → synergy → ritual → scrolling-features-bar → store-faq → sticky
new_order = []
for k in tpl["order"]:
    new_order.append(k)
    if tpl["sections"][k]["type"] == "shop-product-details":
        new_order += ["lb_bundle_components_lb01", "lb_bundle_synergy_lb01", "lb_bundle_ritual_lb01"]

# Dedupe just in case
seen = set(); deduped = []
for k in new_order:
    if k not in seen:
        seen.add(k); deduped.append(k)
tpl["order"] = deduped

print("  new template order:")
for k in tpl["order"]:
    print(f"    {tpl['sections'][k]['type']}")

s = push_asset("templates/product.bundle.json", json.dumps(tpl, indent=2))
print(f"\n  pushed templates/product.bundle.json: status={s}")

# Save locally
with open("/Users/skitch/ClaudeCode/leaf-and-bird/theme-working/templates/product.bundle.json", "w") as f:
    f.write(json.dumps(tpl, indent=2))
print("  local copy updated")
print("\nDONE")
