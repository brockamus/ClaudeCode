"""Body HTML drafts for all 8 bundles. Will be applied after the bundle products
exist (script /tmp/lb_build_bundles.py creates them). Prices are fetched live to
avoid rounding mismatch with the API-set values.
"""
import json, urllib.request

TOKEN = "SHOPIFY_TOKEN_REDACTED"
SHOP = "leaf-and-bird.myshopify.com"
REST = f"https://{SHOP}/admin/api/2024-10"


def rest_get(path):
    req = urllib.request.Request(f"{REST}{path}", headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def rest_put(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{REST}{path}", data=data, method="PUT",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read())


# Body templates — uses {{price}} {{compare_at}} {{savings}} {{savings_pct}} placeholders
BODIES = {
    "first-drop-duo": """
<p>For the curious skeptic who reads every label. Two of our most-loved staples — a gentle multi-active brightener plus heritage-fed tallow nourishment — paired so first-timers (and gift-givers) get the full L&amp;B feel without committing to a full ritual.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/vitamin-glow-serum"><strong>Vitamin Glow Serum</strong></a> — daily brightening with 3-O-ethyl ascorbic acid (the gentle vitamin C that doesn't sting)</li>
  <li><a href="/products/tallow-cream-lemongrass-lavender"><strong>Whipped Grass-Fed Tallow Cream — Lemongrass &amp; Lavender</strong></a> — 3-ingredient ancestral moisture seal, pregnancy-safe</li>
</ul>

<h3>The ritual</h3>
<p>Apply Vitamin Glow first to clean skin, AM and/or PM. Seal with a small swipe of Tallow Cream while skin still feels slightly damp. Twice-a-day takes under 60 seconds.</p>

<h3>Why these two</h3>
<p>Vit Glow lifts pigment and supports collagen with a non-irritating active. Tallow's lipid profile — saturated and omega-rich, zero seed oils — holds that hydration in without the occlusive heaviness of petroleum-based moisturizers. Together: visible glow without the irritation cycle that drives so many people away from "actives."</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this duo. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "radiance-bundle": """
<p>Glow you can wake up to. A nighttime ritual that pulls dullness out, layers gentle actives, and seals in overnight cellular renewal — so the moment you open your eyes, your skin already looks rested.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/dead-sea-mud"><strong>Dead Sea Mud Mask</strong></a> — 3-ingredient mineral mask. 10-minute weekly reset that draws out without stripping</li>
  <li><a href="/products/vitamin-glow-serum"><strong>Vitamin Glow Serum</strong></a> — daily multi-active brightener (gentle, no L-AA sting)</li>
  <li><a href="/products/sleep-plus-collagen-cream"><strong>Sleep Plus Collagen Cream</strong></a> — plant-derived collagen + lavender + a touch of melatonin for overnight repair</li>
</ul>

<h3>The ritual</h3>
<ul>
  <li><strong>1-2× per week</strong> — mask first, 10 minutes on damp skin, rinse</li>
  <li><strong>Every night</strong> — clean skin → Vit Glow → Sleep Plus Collagen Cream</li>
</ul>

<h3>Why these three</h3>
<p>Dead Sea minerals draw out impurities and prep the skin to absorb. Vit Glow lifts pigment and signals collagen support. Sleep Plus restores while you sleep — peak repair window. The cycle compounds: most users feel new-skin softness in the first week and see even-toned glow in 3-4.</p>

<p><strong>Pregnancy note:</strong> Sleep Plus Collagen Cream contains low-dose melatonin and lavender oil — if you're pregnant, see <a href="/products/pregnancy-safe-edit">The Pregnancy-Safe Edit</a> instead.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this bundle. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "hydrate-and-restore": """
<p>The daily ritual when your skin needs more than moisturizer. Repair-grade hydration with cellular signaling, ancestral lipid restoration, and gentle peptide eye care — for skin that's tired, dry, reactive, or recovering.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/pdrn-brightening-serum"><strong>Vegan PDRN Brightening Serum</strong></a> — non-salmon-derived PDRN cellular renewal signaling. Korean-grade efficacy, plant-derived</li>
  <li><a href="/products/tallow-cream-lemongrass-lavender"><strong>Whipped Grass-Fed Tallow Cream — Lemongrass &amp; Lavender</strong></a> — heritage moisture lock, zero seed oils, pregnancy-safe</li>
  <li><a href="/products/peptide-eye-gel-cream"><strong>Peptide Eye Gel-Cream</strong></a> — Acetyl Tetrapeptide-5. No caffeine, no fragrance, no botanical actives that surprise reactive skin</li>
</ul>

<h3>The ritual</h3>
<p>AM and PM — apply PDRN serum to clean skin (a few drops, press in). Eye gel-cream around the orbital bone with a fingertip. Seal with Tallow Cream while still damp.</p>

<h3>Why these three</h3>
<p>PDRN signals cellular turnover (the K-beauty mechanism, made vegan and pregnancy-safe). Tallow restores the lipid barrier with a saturated/omega match no plant cream can mimic. Eye gel addresses the thinnest, most reactive skin with peptides — not the stimulants that puff and rebound.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this bundle. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "brightening-set": """
<p>Built for evening dark spots, melasma, and post-inflammatory marks — without the irritation cycle that comes from going too hard, too fast. Three forms of brightening evidence in one ritual.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/pdrn-brightening-serum"><strong>Vegan PDRN Brightening Serum</strong></a> — daily cellular renewal signal, the foundational brightener</li>
  <li><a href="/products/vitamin-glow-serum"><strong>Vitamin Glow Serum</strong></a> — gentle 3-O-ethyl ascorbic acid for daily-use brightening</li>
  <li><a href="/products/vitamin-c-serum"><strong>Vitamin C Serum</strong></a> — L-AA + MAP + 3-glyceryl ascorbate + ferulic. More intensive — for established marks</li>
</ul>

<h3>The ritual</h3>
<p>AM only. Start with Vit Glow on every-day basis. Once your skin builds tolerance (2-3 weeks), rotate or alternate-day with Vitamin C Serum. Layer PDRN underneath. Always finish with SPF.</p>

<h3>Why three different forms</h3>
<p>Brightening works via different mechanisms — pigment-lift, melanin inhibition, cellular turnover. This trio gives you each. Start gentle (Vit Glow), graduate as tolerated (L-AA Vitamin C). PDRN provides the cellular foundation that makes the other two more effective.</p>

<p><strong>Tolerance note:</strong> Vitamin C Serum contains L-AA — if your skin is reactive, start with 2-3 days/week and build up.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this set. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "pregnancy-safe-edit": """
<p>The skincare ritual built for pregnancy, postpartum, breastfeeding — and for anyone who reacts badly to retinoids, hydroquinone, or unstable actives. Zero off-limits ingredients. Maximum nourishment.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/tallow-cream-lemongrass-lavender"><strong>Whipped Grass-Fed Tallow Cream — Lemongrass &amp; Lavender</strong></a> — 3-ingredient ancestral moisture, no essential-oil concerns at this dose, no seed oils</li>
  <li><a href="/products/peptide-eye-gel-cream"><strong>Peptide Eye Gel-Cream</strong></a> — Acetyl Tetrapeptide-5. No caffeine, no fragrance, no retinoids</li>
  <li><a href="/products/vitamin-glow-serum"><strong>Vitamin Glow Serum</strong></a> — gentle 3-O-ethyl ascorbic acid (not L-AA). Safe for pregnancy and reactive skin</li>
</ul>

<h3>The ritual</h3>
<p>AM and PM. Vit Glow Serum on clean skin → eye gel-cream → tallow seal. The full ritual takes 90 seconds and addresses brightening, eye care, and barrier repair without anything you'd cross off a pregnancy-safe list.</p>

<h3>Why this is the safer choice during pregnancy</h3>
<p>Most "clean" bundles still contain retinoids, salicylic acid above 2%, hydroquinone, or essential-oil concentrations that obstetricians avoid. This trio uses non-stimulating peptides, a non-L-AA vitamin C derivative, and a 3-ingredient tallow cream with no salicylates and zero seed oils. We removed the Sleep Plus Collagen Cream (contains low-dose melatonin) from our standard Radiance bundle specifically for this audience.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this set. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise · Always confirm with your OB before introducing new actives during pregnancy.</em></p>
""",

    "tallow-trio": """
<p>All three of our whipped grass-fed tallow creams in one set — for the ancestral-skincare collector, the scent-loyal, and the curious. Same 3-ingredient formula, three different moods.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/tallow-cream-lemongrass-lavender"><strong>Lemongrass &amp; Lavender</strong></a> — the all-rounder. Sensitive-skin-friendly, lightly herbal</li>
  <li><a href="/products/tallow-cream-orange-bergamot"><strong>Orange &amp; Bergamot</strong></a> — the daytime cream. Citrus-bright. (Bergamot can photosensitize — wear SPF)</li>
  <li><a href="/products/tallow-cream-peaceful-night"><strong>Peaceful Night</strong></a> — the nighttime ritual. Fir + lavender, woodsy and grounding</li>
</ul>

<h3>The ritual</h3>
<p>Match the scent to the moment. Bergamot in the morning, Lemongrass &amp; Lavender any time, Peaceful Night before bed. All three are interchangeable as moisture-seal moisturizers — pick what your nose wants that day.</p>

<h3>Why grass-fed tallow</h3>
<p>Three ingredients: grass-fed beef tallow, organic jojoba oil, essential oils. Saturated fats and omega-3s your skin recognizes. No seed oils (no soy, sunflower, canola — the ones modern skin tends to react to). No emulsifiers, no preservatives, no synthetic fragrance. The skincare your great-grandmother might have made.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this trio. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "anti-aging-stack": """
<p>For 35+ skin asking more from its routine. Three products targeting the cellular signaling, peptide repair, and overnight-restoration windows that compound over months — not the harsh-active route.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/pdrn-brightening-serum"><strong>Vegan PDRN Brightening Serum</strong></a> — cellular renewal signaling. The foundation</li>
  <li><a href="/products/peptide-eye-gel-cream"><strong>Peptide Eye Gel-Cream</strong></a> — Acetyl Tetrapeptide-5 for the orbital area where lines settle first</li>
  <li><a href="/products/sleep-plus-collagen-cream"><strong>Sleep Plus Collagen Cream</strong></a> — plant collagen + lavender + low-dose melatonin for the 10pm-2am peak repair window</li>
</ul>

<h3>The ritual</h3>
<p>AM — PDRN under sunscreen. PM — PDRN → eye gel → Sleep Plus Collagen Cream. The compound effect shows in 6-8 weeks of consistent use.</p>

<h3>Why peptides + signaling > harsh actives</h3>
<p>The aggressive-actives route (high-strength retinoids, acids stacked on acids) drives short-term gains but creates barrier damage that catches up. Cellular signaling (PDRN) and peptide repair work in the body's own repair pathways — slower visible change but more durable, less rebound.</p>

<p><strong>Pregnancy note:</strong> Sleep Plus contains melatonin — see <a href="/products/pregnancy-safe-edit">The Pregnancy-Safe Edit</a> if pregnant.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this stack. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",

    "full-ritual": """
<p>The full Leaf &amp; Bird routine. Five products covering cellular signaling, multi-active brightening, peptide eye care, ancestral barrier repair, and overnight restoration — every base covered in one set.</p>

<h3>What's in it</h3>
<ul>
  <li><a href="/products/pdrn-brightening-serum"><strong>Vegan PDRN Brightening Serum</strong></a> — daily cellular renewal</li>
  <li><a href="/products/vitamin-glow-serum"><strong>Vitamin Glow Serum</strong></a> — gentle daily brightening</li>
  <li><a href="/products/peptide-eye-gel-cream"><strong>Peptide Eye Gel-Cream</strong></a> — Acetyl Tetrapeptide-5 for the eye area</li>
  <li><a href="/products/tallow-cream-lemongrass-lavender"><strong>Whipped Grass-Fed Tallow Cream — Lemongrass &amp; Lavender</strong></a> — daily moisture seal</li>
  <li><a href="/products/sleep-plus-collagen-cream"><strong>Sleep Plus Collagen Cream</strong></a> — overnight repair</li>
</ul>

<h3>The ritual</h3>
<ul>
  <li><strong>AM:</strong> Vit Glow → PDRN → eye gel → Tallow → SPF</li>
  <li><strong>PM:</strong> PDRN → eye gel → Sleep Plus Collagen Cream</li>
</ul>

<h3>Why the full set saves more than individual purchases</h3>
<p>This is the founder's recommendation — the routine we'd hand a friend asking "where do I start?" Five products at one bundle price beats five PDP single-product orders by ${savings}. It's also the most-gifted set for milestone occasions (Mother's Day, milestone birthdays, postpartum gifts).</p>

<p><strong>Pregnancy note:</strong> Sleep Plus contains melatonin — see <a href="/products/pregnancy-safe-edit">The Pregnancy-Safe Edit</a> if pregnant. Or swap Sleep Plus out at checkout if you'd like a custom version.</p>

<h3>Save by buying together</h3>
<p>${total_separately} separately → <strong>${bundle_price}</strong> in this ritual. You save <strong>${savings} ({savings_pct}%)</strong>.</p>

<p><em>Free shipping on orders $50+ · 30-day Clean-Skin Promise</em></p>
""",
}


def apply_bodies():
    """Pull each bundle's pricing from live API, format the body, and PUT it."""
    handles = list(BODIES.keys())
    print(f"Applying body HTML to {len(handles)} bundles…")
    for handle in handles:
        # Look up product by handle
        d = rest_get(f"/products.json?handle={handle}&fields=id,handle,variants")
        products = d.get("products", [])
        if not products:
            print(f"  ✗ {handle}: not found, skipping")
            continue
        p = products[0]
        v = p["variants"][0]
        price = float(v["price"])
        compare_at = float(v.get("compare_at_price") or v["price"])
        savings = round(compare_at - price, 2)
        savings_pct = round(100 * savings / compare_at) if compare_at > 0 else 0

        body = BODIES[handle].format(
            total_separately=f"{compare_at:.2f}",
            bundle_price=f"{price:.2f}",
            savings=f"{savings:.2f}",
            savings_pct=savings_pct,
        ).strip()

        status, _ = rest_put(f"/products/{p['id']}.json", {
            "product": {"id": p["id"], "body_html": body}
        })
        print(f"  ✓ {handle} ({status}): list=${compare_at} bundle=${price} save=${savings} ({savings_pct}%)")


if __name__ == "__main__":
    apply_bodies()
