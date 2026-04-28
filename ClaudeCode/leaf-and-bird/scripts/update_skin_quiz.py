"""Update /pages/skin-quiz with current pricing + 3-tier commitment + bundle routing."""
import json, urllib.request

TOKEN = "SHOPIFY_TOKEN_REDACTED"
PAGE_ID = 171665359147

NEW_BODY = '''<style>
.lb-quiz { max-width: 680px; margin: 24px auto; font-family: inherit; color: #25282a; }
.lb-quiz__intro { text-align: center; margin-bottom: 32px; }
.lb-quiz__intro p { color: #4a4a4a; font-size: 16px; }
.lb-quiz__card { background: #f7f7f5; border-radius: 12px; padding: 32px 24px; margin-bottom: 16px; }
.lb-quiz__q { font-size: 20px; font-weight: 600; margin: 0 0 20px 0; }
.lb-quiz__opts { display: flex; flex-direction: column; gap: 10px; }
.lb-quiz__opt { display: block; padding: 14px 18px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; font-size: 15px; transition: all 0.15s; text-align: left; width: 100%; }
.lb-quiz__opt:hover { border-color: #4f6f5d; background: #eef5ef; }
.lb-quiz__opt.lb-quiz__opt--active { border-color: #4f6f5d; background: #dde8e1; font-weight: 600; }
.lb-quiz__progress { text-align: center; font-size: 13px; color: #888; letter-spacing: 1px; margin-bottom: 12px; text-transform: uppercase; }
.lb-quiz__nav { display: flex; justify-content: space-between; margin-top: 24px; }
.lb-quiz__btn { padding: 12px 28px; font-size: 15px; border-radius: 4px; border: none; cursor: pointer; font-weight: 600; letter-spacing: 0.5px; }
.lb-quiz__btn--primary { background: #4f6f5d; color: white; }
.lb-quiz__btn--primary:hover { background: #3f5a4c; }
.lb-quiz__btn--primary:disabled { background: #ccc; cursor: not-allowed; }
.lb-quiz__btn--ghost { background: transparent; color: #4f6f5d; }
.lb-result { background: white; border: 2px solid #4f6f5d; border-radius: 12px; padding: 32px; text-align: center; }
.lb-result__badge { display: inline-block; background: #4f6f5d; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; letter-spacing: 1px; margin-bottom: 12px; }
.lb-result__title { font-size: 28px; margin: 0 0 8px 0; }
.lb-result__price { font-size: 24px; margin: 16px 0; }
.lb-result__price s { color: #999; font-size: 18px; margin-right: 8px; }
.lb-result__price strong { color: #4f6f5d; }
.lb-result__why { color: #4a4a4a; font-size: 15px; margin: 16px 0 24px 0; padding: 16px; background: #f7f7f5; border-radius: 8px; text-align: left; }
.lb-result__cta { display: inline-block; background: #FFBA46; color: #1A1A1A; padding: 16px 40px; text-decoration: none; border-radius: 4px; font-weight: 600; letter-spacing: 0.5px; }
.lb-result__cta:hover { background: #E59B1F; }
.lb-result__pair { margin-top: 24px; font-size: 14px; color: #666; }
.lb-result__restart { display: inline-block; margin-top: 24px; color: #4f6f5d; font-size: 13px; text-decoration: underline; cursor: pointer; }
</style>

<div class="lb-quiz" id="lb-quiz">
  <div class="lb-quiz__intro">
    <p>Four questions. We&rsquo;ll match you to the vegan PDRN, tallow, peptide product &mdash; or the curated bundle &mdash; that fits your skin and your life stage. <strong>Takes about 30 seconds.</strong></p>
  </div>
  <div id="lb-quiz-card"></div>
</div>

<script>
(function(){
  var QS = [
    { id: 'concern', q: "What's your #1 skin concern right now?", opts: [
      { v: 'brightness', label: 'Brightness & even tone' },
      { v: 'firmness',   label: 'Fine lines & firmness' },
      { v: 'dryness',    label: 'Dryness or damaged barrier' },
      { v: 'eyes',       label: 'Puffy or tired-looking eyes' },
      { v: 'deepclean',  label: 'Congestion or weekly deep cleanse' }
    ]},
    { id: 'stage', q: 'Are you pregnant, nursing, or trying to conceive?', opts: [
      { v: 'expecting', label: 'Yes — pregnant, nursing, or TTC' },
      { v: 'sensitive', label: 'No, but my skin is sensitive or reactive' },
      { v: 'general',   label: 'No — tolerant skin, general anti-aging goals' }
    ]},
    { id: 'texture', q: 'Serum or cream?', opts: [
      { v: 'serum',  label: 'Serum — lightweight, layerable actives' },
      { v: 'cream',  label: 'Cream — rich, barrier-nourishing' },
      { v: 'both',   label: 'Both — I want a routine, not one product' }
    ]},
    { id: 'tier', q: "How committed are you?", opts: [
      { v: 'hero',    label: 'Test the waters — one hero product to start' },
      { v: 'routine', label: 'Build a routine — curated 2-3 product set' },
      { v: 'full',    label: 'Go all in — full ritual or premium set' }
    ]}
  ];

  var answers = {};
  var stepIdx = 0;

  function el(tag, attrs, children){
    var e = document.createElement(tag);
    if(attrs) for(var k in attrs){ if(k==='class')e.className=attrs[k]; else if(k==='html')e.innerHTML=attrs[k]; else e.setAttribute(k,attrs[k]); }
    if(children) children.forEach(function(c){ e.appendChild(typeof c==='string'?document.createTextNode(c):c); });
    return e;
  }

  function render(){
    var card = document.getElementById('lb-quiz-card');
    card.innerHTML = '';
    if(stepIdx >= QS.length){ return renderResult(card); }
    var q = QS[stepIdx];
    var wrap = el('div', { class: 'lb-quiz__card' });
    wrap.appendChild(el('div', { class: 'lb-quiz__progress' }, ['Question ' + (stepIdx+1) + ' of ' + QS.length]));
    wrap.appendChild(el('h2', { class: 'lb-quiz__q' }, [q.q]));
    var opts = el('div', { class: 'lb-quiz__opts' });
    q.opts.forEach(function(o){
      var btn = el('button', { class: 'lb-quiz__opt' + (answers[q.id]===o.v?' lb-quiz__opt--active':''), type: 'button' }, [o.label]);
      btn.addEventListener('click', function(){ answers[q.id] = o.v; render(); });
      opts.appendChild(btn);
    });
    wrap.appendChild(opts);
    var nav = el('div', { class: 'lb-quiz__nav' });
    if(stepIdx > 0){
      var back = el('button', { class: 'lb-quiz__btn lb-quiz__btn--ghost', type: 'button' }, ['\\u2190 Back']);
      back.addEventListener('click', function(){ stepIdx--; render(); });
      nav.appendChild(back);
    } else { nav.appendChild(el('span')); }
    var next = el('button', { class: 'lb-quiz__btn lb-quiz__btn--primary', type: 'button' }, [stepIdx === QS.length-1 ? 'See my match \\u2192' : 'Next \\u2192']);
    if(!answers[q.id]) next.disabled = true;
    next.addEventListener('click', function(){ stepIdx++; render(); });
    nav.appendChild(next);
    wrap.appendChild(nav);
    card.appendChild(wrap);
  }

  // Single-product catalog (current pricing — sale + compare-at)
  var PRODUCTS = {
    'pdrn':    { name: 'Vegan PDRN Brightening Serum',          url: '/products/pdrn-brightening-serum',           price: 26.99, wasPrice: 32.00 },
    'vc':      { name: 'Vitamin C Serum',                       url: '/products/vitamin-c-serum',                  price: 16.99, wasPrice: 20.00 },
    'vglow':   { name: 'Vitamin Glow Serum',                    url: '/products/vitamin-glow-serum',               price: 20.99, wasPrice: 24.90 },
    'eye':     { name: 'Peptide Eye Gel-Cream',                 url: '/products/peptide-eye-gel-cream',            price: 30.99, wasPrice: 35.99 },
    'tallowL': { name: 'Tallow Cream — Lemongrass & Lavender',  url: '/products/tallow-cream-lemongrass-lavender', price: 22.99, wasPrice: 27.00 },
    'tallowN': { name: 'Tallow Cream — Peaceful Night',         url: '/products/tallow-cream-peaceful-night',      price: 22.99, wasPrice: 27.00 },
    'tallowO': { name: 'Tallow Cream — Orange & Bergamot',      url: '/products/tallow-cream-orange-bergamot',     price: 22.99, wasPrice: 27.00 },
    'mud':     { name: 'Dead Sea Mud Mask',                     url: '/products/dead-sea-mud',                     price: 26.99, wasPrice: 31.90 },
    'sleep':   { name: 'Sleep Plus Collagen Cream',             url: '/products/sleep-plus-collagen-cream',        price: 27.99, wasPrice: 32.99 },
    // Bundles
    'firstdrop':{ name: 'The First Drop Duo',         url: '/products/first-drop-duo',        price: 36.85, wasPrice: 51.90, isBundle: true },
    'radiance': { name: 'Radiance Bundle',            url: '/products/radiance-bundle',       price: 67.34, wasPrice: 89.79, isBundle: true },
    'hydrate':  { name: 'Hydrate & Restore',          url: '/products/hydrate-and-restore',   price: 71.24, wasPrice: 94.99, isBundle: true },
    'bright':   { name: 'The Brightening Set',        url: '/products/brightening-set',       price: 53.83, wasPrice: 76.90, isBundle: true },
    'preg':     { name: 'The Pregnancy-Safe Edit',    url: '/products/pregnancy-safe-edit',   price: 57.13, wasPrice: 87.89, isBundle: true },
    'tallow3':  { name: 'The Tallow Trio',            url: '/products/tallow-trio',           price: 56.70, wasPrice: 81.00, isBundle: true },
    'aging':    { name: 'The Anti-Aging Stack',       url: '/products/anti-aging-stack',      price: 70.69, wasPrice: 100.98, isBundle: true },
    'full':     { name: 'The Full Ritual',            url: '/products/full-ritual',           price: 102.43, wasPrice: 152.88, isBundle: true }
  };

  // Routing matrix: (concern, stage) → { hero, routine, full }
  // For "expecting" stage we always route routine/full to Pregnancy-Safe Edit
  // (we don't yet have a pregnancy-specific 5-piece set).
  var MATRIX = {
    'brightness': {
      'expecting': { hero: 'vglow',   routine: 'preg',     full: 'preg' },
      'sensitive': { hero: 'vglow',   routine: 'bright',   full: 'full' },
      'general':   { hero: 'vc',      routine: 'bright',   full: 'full' }
    },
    'firmness': {
      'expecting': { hero: 'eye',     routine: 'preg',     full: 'preg' },
      'sensitive': { hero: 'pdrn',    routine: 'hydrate',  full: 'aging' },
      'general':   { hero: 'pdrn',    routine: 'aging',    full: 'full' }
    },
    'dryness': {
      'expecting': { hero: 'tallowL', routine: 'preg',     full: 'preg' },
      'sensitive': { hero: 'tallowL', routine: 'hydrate',  full: 'tallow3' },
      'general':   { hero: 'tallowN', routine: 'hydrate',  full: 'full' }
    },
    'eyes': {
      'expecting': { hero: 'eye',     routine: 'preg',     full: 'preg' },
      'sensitive': { hero: 'eye',     routine: 'aging',    full: 'aging' },
      'general':   { hero: 'eye',     routine: 'aging',    full: 'full' }
    },
    'deepclean': {
      'expecting': { hero: 'mud',     routine: 'mud',      full: 'preg' },
      'sensitive': { hero: 'mud',     routine: 'radiance', full: 'full' },
      'general':   { hero: 'mud',     routine: 'radiance', full: 'full' }
    }
  };

  // "Why this match" copy keyed by primary product/bundle key
  var WHY = {
    'pdrn':    'PDRN signals fibroblast activity and cellular renewal — the structural-repair layer of a serious anti-aging routine. Non-salmon-derived (rare in the category), vegan, and barrier-friendly. No purge phase.',
    'vc':      'L-ascorbic acid + MAP + ferulic + 3-glyceryl ascorbate — four forms of vitamin C in one serum. The daily antioxidant layer for tolerant skin. Pair with SPF every morning.',
    'vglow':   'Stable 3-O-ethyl ascorbic acid handles tone and dullness without the tingling of pure L-AA. Pregnancy-aware and sensitive-skin friendly.',
    'eye':     'Acetyl Tetrapeptide-5 targets under-eye puffiness and microcirculation. Fragrance-free, caffeine-free, gel-cream texture that sits under makeup without creasing.',
    'tallowL': "Grass-fed tallow's fatty acid profile mirrors human sebum — rebuilds the barrier without occlusion. Lemongrass & Lavender is our pregnancy-safe all-day all-rounder.",
    'tallowN': 'Same 3-ingredient grass-fed tallow base as our daytime cream, with fir + lavender for an overnight repair scent profile.',
    'mud':     'Three ingredients, weekly use: Dead Sea minerals, kaolin, and bentonite. Pore reset without acids, fillers, or stripping. Pregnancy-safe.',
    'firstdrop':'Vit Glow + Tallow Lemongrass — the gentle multi-active brightener and the heritage moisture seal. Pregnancy-safe entry point. Saves 29% vs buying separately.',
    'radiance': 'Dead Sea Mud + Vit Glow + Sleep Plus Collagen Cream. Mask, brighten, restore — the nighttime ritual that compounds. Saves 25% vs separate.',
    'hydrate':  'PDRN + Tallow Lemongrass + Eye Gel — repair-grade hydration with cellular signaling, ancestral lipid restoration, and gentle peptide eye care. Saves 25%.',
    'bright':   'PDRN + Vit Glow + Vitamin C Serum — three forms of brightening evidence (cellular renewal, gentle daily, and L-AA spot work) in one ritual. Saves 30%.',
    'preg':     'Tallow Lemongrass + Eye Gel + Vit Glow — zero off-limits ingredients, peptides instead of retinoids, gentle 3-O-ethyl Vitamin C instead of L-AA. Built for pregnancy, postpartum, and reactive skin. Saves 35%.',
    'tallow3':  'All three of our whipped grass-fed tallow creams: Lemongrass & Lavender, Orange & Bergamot, Peaceful Night. Same 3-ingredient formula, three moods. Saves 30%.',
    'aging':    'PDRN + Eye Gel + Sleep Plus — cellular signaling, peptide repair, and overnight collagen support. Three actives that compound rather than compete. Saves 30%.',
    'full':     "The founder's full routine: PDRN + Vit Glow + Eye Gel + Tallow + Sleep Plus. Five products covering AM and PM, brightening to barrier repair to overnight restoration. Saves 33% vs separate."
  };

  function recommend(a){
    var key = (MATRIX[a.concern] && MATRIX[a.concern][a.stage] && MATRIX[a.concern][a.stage][a.tier]) || 'pdrn';
    return { primary: key, why: WHY[key] || '' };
  }

  function renderResult(card){
    var rec = recommend(answers);
    var p = PRODUCTS[rec.primary];
    var pct = Math.round((1 - p.price/p.wasPrice) * 100);
    var result = el('div', { class: 'lb-result' });
    result.appendChild(el('div', { class: 'lb-result__badge' }, [p.isBundle ? 'YOUR MATCH — BUNDLE' : 'YOUR MATCH']));
    result.appendChild(el('h2', { class: 'lb-result__title' }, [p.name]));
    result.appendChild(el('div', { class: 'lb-result__price', html: '<s>$' + p.wasPrice.toFixed(2) + '</s> <strong>$' + p.price.toFixed(2) + '</strong> &mdash; ' + pct + '% off' }));
    result.appendChild(el('div', { class: 'lb-result__why' }, [rec.why]));
    var cta = el('a', { class: 'lb-result__cta', href: p.url }, [p.isBundle ? 'SHOP THE BUNDLE \\u2192' : 'TRY IT RISK-FREE \\u2192']);
    result.appendChild(cta);
    result.appendChild(el('p', { class: 'lb-result__pair', html: '<strong>The Clean-Skin Promise:</strong> 30 days, full refund, no returns required. Free shipping on $50+.' }));
    var restart = el('a', { class: 'lb-result__restart' }, ['\\u21ba Retake the quiz']);
    restart.addEventListener('click', function(){ answers = {}; stepIdx = 0; render(); });
    result.appendChild(restart);
    card.appendChild(result);
  }

  render();
})();
</script>

<p style="text-align:center; margin-top:40px; font-size:14px; color:#4a4a4a;">Prefer to browse? See all <a href="/collections/bundles" style="color:#4f6f5d; font-weight:600; text-decoration:underline;">bundles &amp; sets</a>, the <a href="/collections/all" style="color:#4f6f5d; font-weight:600; text-decoration:underline;">full catalog</a>, the <a href="/blogs/journal" style="color:#4f6f5d; font-weight:600; text-decoration:underline;">clean-beauty journal</a>, or read <a href="/pages/why-we-stopped-using-retinol" style="color:#4f6f5d; font-weight:600; text-decoration:underline;">why we stopped using retinol</a>.</p>'''

# Note: \u escapes in the JS body need to be literal \u, not Python escape sequences.
# We wrote them as \\u above — Python triple-quoted-string escapes one slash, so Liquid sees \u.
# Verify by checking a known marker survives.
assert '\\u2192' in NEW_BODY  # arrow
assert 'preg' in NEW_BODY
assert 'pregnancy-safe-edit' in NEW_BODY

# PUT to Shopify
body = json.dumps({"page": {"id": PAGE_ID, "body_html": NEW_BODY}}).encode()
req = urllib.request.Request(
    f"https://leaf-and-bird.myshopify.com/admin/api/2024-10/pages/{PAGE_ID}.json",
    data=body, method="PUT",
    headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=60) as r:
    d = json.loads(r.read())
    print(f"PUT status={r.status}")
    print(f"  body_html length: {len(d['page']['body_html'])}")
    print(f"  updated_at: {d['page']['updated_at']}")
print("Done.")
