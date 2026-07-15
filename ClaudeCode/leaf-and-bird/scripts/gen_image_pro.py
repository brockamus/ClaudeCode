"""Generate a complete PDP card via Nano Banana Pro (gemini-3-pro-image-preview).

Pro can handle text, layout, icons, and composition natively — no PIL hybrid needed.
Pass a single comprehensive prompt that describes the full card.
"""
import argparse, base64, json, os, pathlib, subprocess, sys, urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-pro-image-preview"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "images" / "products"


def call_pro(ref_image_bytes_list, prompt, aspect="1:1"):
    """Pro endpoint — supports multiple reference images + text prompt."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    parts = []
    for b in ref_image_bytes_list:
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(b).decode()}})
    parts.append({"text": prompt})
    body = {
        "contents": [{"parts": parts}],
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", required=True)
    ap.add_argument("--preset", required=True)
    ap.add_argument("--refs", nargs="+", required=True, help="Paths to reference images")
    ap.add_argument("--prompt", required=True)
    args = ap.parse_args()

    out_dir = OUT_DIR / args.handle
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.preset}.jpg"

    refs = [pathlib.Path(p).read_bytes() for p in args.refs]
    response = call_pro(refs, args.prompt)
    img_bytes = extract_image_bytes(response)
    if not img_bytes:
        print("NO IMAGE in response. Full response:")
        print(json.dumps(response, indent=2)[:2000])
        sys.exit(1)

    png_path = out_path.with_suffix(".png")
    png_path.write_bytes(img_bytes)
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png_path), "--out", str(out_path)],
        check=True, capture_output=True,
    )
    png_path.unlink()
    print(f"Saved {out_path} ({out_path.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
