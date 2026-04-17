"""Generate a featured image for a blog article using Google Gemini.

Uses Imagen 4.0 via the Gemini API for text-to-image.
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
    png_path = out_path.with_suffix(".png")
    png_path.write_bytes(base64.b64decode(b64))
    # Convert PNG -> JPEG @ 85% for smaller file size (sips is macOS-native).
    import subprocess
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png_path), "--out", str(out_path)],
        check=True, capture_output=True,
    )
    png_path.unlink()
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
    out = OUT_DIR / f"{args.article}.jpg"
    generate_imagen(prompt, out)
    # Update draft with image_path + a default alt if missing.
    # publish_article.py resolves image_path relative to content/ (draft.parent.parent),
    # so write the path with a ../ prefix to walk from content/ up to project root.
    if draft.exists():
        content_dir = draft.resolve().parent.parent
        rel_from_content = os.path.relpath(out.resolve(), content_dir)
        d["image_path"] = rel_from_content
        if not d.get("image_alt"):
            d["image_alt"] = f"{d.get('title', args.article)} — featured image"
        draft.write_text(json.dumps(d, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
