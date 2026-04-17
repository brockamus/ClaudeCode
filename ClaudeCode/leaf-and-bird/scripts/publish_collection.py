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
