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
