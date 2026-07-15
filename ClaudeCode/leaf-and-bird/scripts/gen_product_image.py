"""Generate product PDP images via Nano Banana (Gemini 2.5 multimodal).

Takes a product reference photo + text prompt, produces a new image with the
exact bottle preserved but in a new scene (lifestyle, texture, etc.).

Usage:
  GEMINI_API_KEY=... python3 gen_product_image.py \
      --handle pdrn-brightening-serum \
      --preset lifestyle-linen \
      --ref /Users/skitch/ClaudeCode/leaf-and-bird/images/products/pdrn-brightening-serum/hero.jpg \
      --prompt "Place this bottle on a soft pale linen surface..."
"""
import argparse, base64, json, os, pathlib, subprocess, sys, urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash-image"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "images" / "products"


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
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def extract_image_bytes(response):
    for cand in response.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part and part["inlineData"].get("mimeType", "").startswith("image/"):
                return base64.b64decode(part["inlineData"]["data"])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", required=True, help="Product handle, e.g. pdrn-brightening-serum")
    ap.add_argument("--preset", required=True, help="Preset name for filename, e.g. lifestyle-linen, texture-drop")
    ap.add_argument("--ref", required=True, help="Path to reference product image (JPEG)")
    ap.add_argument("--prompt", required=True, help="Generation prompt")
    args = ap.parse_args()

    out_dir = OUT_DIR / args.handle
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.preset}.jpg"

    ref_bytes = pathlib.Path(args.ref).read_bytes()
    response = call_nano_banana(ref_bytes, args.prompt)
    img_bytes = extract_image_bytes(response)
    if not img_bytes:
        print(f"ERROR no image in response for {args.handle}/{args.preset}")
        print(json.dumps(response, indent=2)[:600])
        sys.exit(1)

    png_path = out_path.with_suffix(".png")
    png_path.write_bytes(img_bytes)
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png_path), "--out", str(out_path)],
        check=True, capture_output=True,
    )
    png_path.unlink()
    print(f"Saved {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
