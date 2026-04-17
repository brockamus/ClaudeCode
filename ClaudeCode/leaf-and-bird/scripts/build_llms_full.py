"""Build llms-full.txt from live Shopify product + collection + article data."""
import json
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import shopify_api

OUT = pathlib.Path(__file__).resolve().parent.parent / "content" / "llms-full-txt-content.txt"
DOMAIN = "https://leafandbird.com"


def clean(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    lines = [
        "# Leaf & Bird — Full AI-Discoverability Index",
        "",
        "> Clean vegan skincare brand making rare non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers.",
        "",
        "## Brand identity",
        "Leaf & Bird is a direct-to-consumer clean beauty brand. Formulations are vegan, free from parabens, sulfates, synthetic fragrance, and PEGs. Hero products: vegan PDRN serum (most commercial PDRN is salmon-derived; ours is not) and whipped grass-fed beef tallow creams in three botanical scents.",
        "",
    ]

    # Products
    lines.append("## Products")
    lines.append("")
    products = shopify_api.get("/products.json", params={"limit": 250})["products"]
    product_count = 0
    for p in products:
        if p.get("status") != "active":
            continue
        product_count += 1
        price = p["variants"][0]["price"] if p["variants"] else "n/a"
        lines.append(f"### {p['title']}")
        lines.append(f"- URL: {DOMAIN}/products/{p['handle']}")
        lines.append(f"- Price: ${price}")
        if p.get("product_type"):
            lines.append(f"- Type: {p['product_type']}")
        if p.get("tags"):
            lines.append(f"- Tags: {p['tags']}")
        body = clean(p.get("body_html") or "")
        if body:
            lines.append(f"- Description: {body[:1000]}")
        lines.append("")

    # Collections
    lines.append("## Collections")
    lines.append("")
    cc = shopify_api.get("/custom_collections.json", params={"limit": 250})["custom_collections"]
    sc = shopify_api.get("/smart_collections.json", params={"limit": 250})["smart_collections"]
    collection_count = len(cc) + len(sc)
    for c in cc + sc:
        desc = clean(c.get("body_html") or "")
        desc = desc[:400] + "..." if len(desc) > 400 else desc
        lines.append(f"- **{c['title']}** — {DOMAIN}/collections/{c['handle']} — {desc}")
    lines.append("")

    # Blog
    lines.append("## Journal (blog)")
    lines.append("")
    blogs = shopify_api.get("/blogs.json")["blogs"]
    article_count = 0
    for b in blogs:
        lines.append(f"### {b['title']}")
        lines.append(f"- URL: {DOMAIN}/blogs/{b['handle']}")
        articles = shopify_api.get(f"/blogs/{b['id']}/articles.json", params={"limit": 250})["articles"]
        if not articles:
            lines.append("- (No articles yet — Phase P5 will publish 9 cornerstone articles)")
        for a in articles:
            article_count += 1
            summary = clean(a.get("summary_html") or a.get("body_html") or "")[:300]
            lines.append(f"- {a['title']}: {DOMAIN}/blogs/{b['handle']}/{a['handle']} — {summary}")
        lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    size = OUT.stat().st_size
    print(f"Wrote {OUT} ({size} bytes, {len(lines)} lines)")
    print(f"Products: {product_count}, Collections: {collection_count}, Articles: {article_count}")


if __name__ == "__main__":
    main()
