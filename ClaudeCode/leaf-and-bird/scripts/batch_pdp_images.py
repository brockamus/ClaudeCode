"""Batch-generate lifestyle + texture PDP images for all L&B products via Nano Banana.

Uses each product's hero photo as the bottle reference, and (where applicable)
its lid-open photo as the contents-color reference. Saves outputs locally;
upload to Shopify happens via a separate step after review.
"""
import base64, json, os, pathlib, subprocess, sys, time, urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash-image"
OUT_ROOT = pathlib.Path("/Users/skitch/ClaudeCode/leaf-and-bird/images/products")
REFS_ROOT = OUT_ROOT / "_refs_audit"


# (preset_name, ref_image_filename_in_audit_dir, prompt)
JOBS = {
    "vitamin-glow-serum": [
        ("lifestyle-linen", "img-1.jpg",
         "Place this exact white skincare dropper bottle (preserve the bottle shape, label, all text/typography exactly) on a soft pale natural linen surface. Editorial flat-lay shot from above, slightly angled. Add a fresh slice of citrus and a small jade gua sha to the side, a folded soft cotton washcloth in corner, soft warm morning light from upper left, gentle natural shadows, neutral cream + sage palette, premium clean-beauty editorial aesthetic. The bottle is the focal point with all label text readable. No people, no overlays, no other logos. Premium magazine quality."),
        ("lifestyle-in-hand", "img-1.jpg",
         "Place this exact white skincare dropper bottle (preserve bottle shape, label, all typography) being gently held in a feminine hand with neutral natural skin tone, against a soft cream and sage colored bathroom or vanity background slightly out of focus. The bottle is fully readable, the focal point, with clean clinical-feeling clean beauty editorial aesthetic. Soft warm window light from the side, gentle natural shadows. No face visible, no overlay text, no other logos. Premium magazine quality."),
        ("texture-drop", "img-3.jpg",
         "Macro close-up of a single drop of milky-white skincare serum on a clean fingertip — fingertip with neutral natural skin tone, the droplet is dewy and reflects soft warm window light. The serum has a slightly opaque milky white color matching the reference. Background is softly out-of-focus pale cream and sage tones. The bottle does NOT need to appear. Focus is entirely on the droplet showing the formula's lightweight milky texture. Premium beauty editorial, magazine quality, ultra-detailed dewy skin."),
    ],
    "vitamin-c-serum": [
        ("lifestyle-linen", "img-1.jpg",
         "Place this exact AMBER GLASS skincare dropper bottle with white label (preserve the amber/dark brown bottle color, the label shape and all text/typography exactly) on a warm natural wood surface. Editorial flat-lay shot from above, slightly angled. Add a few golden petals and a folded soft cotton round to the side, soft warm morning light from upper left, gentle natural shadows, warm cream and gold palette echoing the amber bottle, premium clean-beauty editorial aesthetic. The bottle is the focal point with all label text readable. The bottle MUST remain amber/dark brown glass — do NOT change it to white or any other color. No people, no overlays, no other logos."),
        ("lifestyle-in-hand", "img-1.jpg",
         "Place this exact AMBER GLASS skincare dropper bottle with white label (preserve the dark amber bottle color, label, all typography exactly) being gently held in a feminine hand with neutral natural skin tone, against a warm cream and gold colored bathroom background slightly out of focus. The bottle is fully readable, the focal point. The bottle MUST remain amber/dark brown glass. Soft warm window light, gentle natural shadows. No face visible, no overlay text, no other logos. Premium magazine quality."),
        ("texture-drop", "img-3.jpg",
         "Macro close-up of a single drop of golden-amber clear skincare serum on a clean fingertip — fingertip with neutral natural skin tone, the droplet is dewy and reflects warm light, with subtle golden-orange tint matching a high-potency Vitamin C serum. Background is softly out-of-focus warm cream and gold tones. The bottle does NOT need to appear. Focus is entirely on the droplet showing the formula's lightweight golden-tinted clear texture. Premium beauty editorial, magazine quality, ultra-detailed dewy skin."),
    ],
    "peptide-eye-gel-cream": [
        ("lifestyle-marble", "img-1.jpg",
         "Place this exact white skincare pump bottle / airless pump container (preserve the bottle shape, label, all text/typography exactly) on a clean white marble bathroom counter. Editorial flat-lay slightly angled. Add a single small fresh leaf and a clean cotton round to the side, soft cool morning light from above, gentle shadows, neutral white and sage palette, clinical clean-beauty editorial aesthetic. The pump is the focal point with all label text readable. No people, no overlays, no other logos. Premium magazine quality."),
        ("lifestyle-in-hand", "img-1.jpg",
         "Place this exact white skincare pump bottle / airless pump container (preserve bottle shape, label, all typography) being gently held in a feminine hand with neutral natural skin tone, against a soft cream and sage colored bedside or vanity background slightly out of focus. The pump is fully readable, the focal point. Soft warm bedside lamp light, gentle natural shadows. No face visible, no overlays. Premium magazine quality."),
        ("texture-dollop", "img-3.jpg",
         "Macro close-up of a small pea-sized dollop of pure white creamy gel-cream on a clean fingertip — fingertip with neutral natural skin tone, the cream is silky and reflects soft warm window light, fluffy and lightweight texture. Background is softly out-of-focus pale cream and white tones. The pump bottle does NOT need to appear. Focus is entirely on the dollop showing the cream's pure white silky texture. Premium beauty editorial, magazine quality, ultra-detailed."),
    ],
    "sleep-plus-collagen-cream": [
        ("lifestyle-bedside", "img-1.jpg",
         "Place this exact white skincare jar (preserve jar shape, label, all text/typography exactly) on a softly lit bedside table with cream linen sheets visible in soft focus, a dim warm lamp glow nearby, a small sprig of lavender on the side. Cozy nighttime bedroom aesthetic, warm amber + cream palette, premium clean-beauty editorial. The jar is the focal point with all label text readable. No people, no overlays, no other logos. Magazine quality."),
        ("lifestyle-with-lid-off", "img-4.jpg",
         "Place this exact white skincare jar (preserve jar shape, label, all typography) on a clean cream surface with the lid removed and placed beside it, the ivory-colored cream visible inside the jar. Slightly angled editorial shot, soft warm window light from upper left, gentle shadows, neutral cream and sage palette. The ivory cream contents must be clearly visible inside. The jar is the focal point with label readable. No people, no overlays, no other logos."),
        ("texture-swirl", "img-4.jpg",
         "Macro close-up of a swirl of rich ivory-cream colored night cream on a clean fingertip — fingertip with neutral natural skin tone, the cream is rich and slightly velvety with a slight ivory/pale-yellow undertone matching a collagen-rich night moisturizer. Background is softly out-of-focus warm cream tones. The jar does NOT need to appear. Focus is entirely on the swirl showing the cream's rich ivory texture. Premium beauty editorial, magazine quality, ultra-detailed."),
    ],
    "tallow-cream-peaceful-night": [
        ("lifestyle-bedside", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM PEACEFUL NIGHT' (preserve jar shape, label, all text/typography exactly) on a softly lit bedside table with cream linen sheets in soft focus, a dim warm lamp glow, a small sprig of fir or fresh lavender. Cozy moody nighttime aesthetic, warm amber + cream palette, premium clean-beauty editorial. The jar is the focal point. No people, no overlays."),
        ("lifestyle-in-palm", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM PEACEFUL NIGHT' (preserve jar shape, label, all typography) being gently cradled in an open palm with neutral natural skin tone, against a soft warm bedroom or candlelit background slightly out of focus. Moody warm light, gentle shadows. The jar is fully readable, focal point. No face visible, no overlays."),
        ("texture-swirl", "img-1.jpg",
         "Macro close-up of a finger swiping through whipped ivory-colored tallow balm — the texture is rich whipped buttery balm with a creamy ivory color (slightly more pale yellow than white). Fingertip with neutral skin tone, soft warm window light. Background is softly out-of-focus cream tones. Focus is entirely on the whipped tallow texture showing its rich balm consistency. Premium beauty editorial, magazine quality, ultra-detailed."),
    ],
    "tallow-cream-lemongrass-lavender": [
        ("lifestyle-linen", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM LEMONGRASS & LAVENDER' (preserve jar shape, label, all text/typography exactly) on a soft pale natural linen surface. Add a fresh lemongrass stalk and a small sprig of lavender to the side, a folded cotton washcloth in corner, soft warm morning light from upper left, gentle shadows, sage and cream palette, premium clean-beauty editorial flat-lay aesthetic. The jar is the focal point. No people, no overlays."),
        ("lifestyle-in-palm", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM LEMONGRASS & LAVENDER' (preserve jar shape, label, all typography) being gently cradled in an open palm with neutral natural skin tone, against a soft sage-and-cream bathroom morning light background slightly out of focus. Bright airy aesthetic, gentle shadows. The jar fully readable, focal point. No face visible, no overlays."),
        ("texture-swirl", "img-1.jpg",
         "Macro close-up of a finger swiping through whipped ivory-colored tallow balm — texture is rich whipped buttery balm with creamy ivory color (slightly pale yellow). A few small lavender buds nearby. Fingertip with neutral skin tone, soft bright morning light. Background softly out-of-focus sage and cream tones. Focus on the whipped tallow texture. Premium beauty editorial, magazine quality, ultra-detailed."),
    ],
    "tallow-cream-orange-bergamot": [
        ("lifestyle-linen", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM ORANGE & BERGAMOT' (preserve jar shape, label, all text/typography exactly) on a soft pale natural linen surface. Add a fresh orange slice and a curl of bergamot peel to the side, a folded cotton washcloth in corner, bright warm morning light, gentle shadows, citrus + cream palette, premium clean-beauty editorial flat-lay aesthetic. The jar is the focal point. No people, no overlays."),
        ("lifestyle-in-palm", "img-1.jpg",
         "Place this exact white skincare jar labeled 'TALLOW CREAM ORANGE & BERGAMOT' (preserve jar shape, label, all typography) being gently cradled in an open palm with neutral natural skin tone, against a soft golden-citrus morning light background with blurred fresh oranges. Bright airy citrus aesthetic. The jar fully readable, focal point. No face visible, no overlays."),
        ("texture-swirl", "img-3.jpg",
         "Macro close-up of a finger swiping through whipped ivory-colored tallow balm — texture is rich whipped buttery balm with creamy ivory color (slightly pale yellow). A small orange peel curl nearby. Fingertip with neutral skin tone, warm golden morning light. Background softly out-of-focus golden citrus and cream tones. Focus on the whipped tallow texture. Premium beauty editorial, magazine quality, ultra-detailed."),
    ],
    "dead-sea-mud": [
        ("lifestyle-spa", "img-1.jpg",
         "Place this exact white skincare jar with a BLACK twist-off lid, labeled 'DEAD SEA MUD ALL-NATURAL' (preserve jar shape, label, all text/typography, AND the dark/black lid color exactly) on a soft natural linen surface in a calm spa-like setting. Add a small wooden facial brush beside it, a folded white cotton washcloth, a single small smooth river stone for spa aesthetic, soft warm window light, gentle shadows, neutral cream and stone palette, premium spa editorial. The jar is the focal point with the black lid clearly visible. No people, no overlays, no other logos."),
        ("lifestyle-in-hand", "img-1.jpg",
         "Place this exact white skincare jar with BLACK twist-off lid, labeled 'DEAD SEA MUD ALL-NATURAL' (preserve jar shape, label, all typography, AND the dark/black lid exactly) being gently held in an open palm with neutral natural skin tone, against a softly textured stone or concrete background slightly out of focus. Spa-like, calm, neutral palette. The jar fully readable, focal point. The BLACK LID must remain dark/black. No face visible, no overlays."),
        ("texture-swirl", "img-1.jpg",
         "Macro close-up of dark gray-brown Dead Sea mud being swirled with a finger inside an open jar — the mud is wet, smooth, dark gray-brown clay-like texture, glistening from soft warm light. Background is softly out-of-focus cream and stone tones. The closed jar does NOT need to appear; focus is on the actual mud texture inside an open jar with the brown-gray mud clearly visible. Premium spa editorial, magazine quality, ultra-detailed wet clay texture."),
    ],
}


def call_nano_banana(ref_image_bytes, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    body = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(ref_image_bytes).decode()}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def extract_image_bytes(response):
    for cand in response.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("image/"):
                return base64.b64decode(part["inlineData"]["data"])
    return None


def main():
    total = sum(len(v) for v in JOBS.values())
    print(f"Generating {total} images across {len(JOBS)} products...")
    done = 0
    for handle, jobs in JOBS.items():
        out_dir = OUT_ROOT / handle
        out_dir.mkdir(parents=True, exist_ok=True)
        for preset, ref_filename, prompt in jobs:
            done += 1
            ref_path = REFS_ROOT / handle / ref_filename
            out_path = out_dir / f"{preset}.jpg"
            if out_path.exists():
                print(f"  [{done}/{total}] {handle}/{preset} (skip — exists)")
                continue
            if not ref_path.exists():
                print(f"  [{done}/{total}] {handle}/{preset} (FAIL — ref missing: {ref_path})")
                continue
            print(f"  [{done}/{total}] {handle}/{preset}...", end=" ", flush=True)
            try:
                response = call_nano_banana(ref_path.read_bytes(), prompt)
                img_bytes = extract_image_bytes(response)
                if not img_bytes:
                    print("NO IMAGE in response")
                    continue
                png_path = out_path.with_suffix(".png")
                png_path.write_bytes(img_bytes)
                subprocess.run(
                    ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png_path), "--out", str(out_path)],
                    check=True, capture_output=True,
                )
                png_path.unlink()
                print(f"OK ({out_path.stat().st_size // 1024}KB)")
            except urllib.error.HTTPError as e:
                print(f"HTTP {e.code}: {e.read().decode()[:200]}")
            except Exception as e:
                print(f"ERR: {e}")
            time.sleep(3)  # rate limit


if __name__ == "__main__":
    main()
