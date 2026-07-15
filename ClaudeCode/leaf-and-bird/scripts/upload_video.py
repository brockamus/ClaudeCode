"""Upload a local video to Shopify Files (VIDEO) and print the playable mp4 source URL.

Usage: python upload_video.py <local.mp4> [filename-on-shopify.mp4]
"""
import os, sys, time, json, mimetypes
import requests

SHOP = os.environ["SHOPIFY_SHOP"]
TOKEN = os.environ["SHOPIFY_TOKEN"]
API = "2024-10"
GQL = f"https://{SHOP}/admin/api/{API}/graphql.json"
HEAD = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def gql(query, variables=None):
    r = requests.post(GQL, headers=HEAD, json={"query": query, "variables": variables or {}})
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise SystemExit("GraphQL errors: " + json.dumps(data["errors"], indent=2))
    return data["data"]


def upload(local_path, target_name):
    size = str(os.path.getsize(local_path))
    staged = gql(
        """
        mutation stage($input:[StagedUploadInput!]!){
          stagedUploadsCreate(input:$input){
            stagedTargets{ url resourceUrl parameters{ name value } }
            userErrors{ field message }
          }
        }""",
        {"input": [{"filename": target_name, "mimeType": "video/mp4",
                    "resource": "VIDEO", "httpMethod": "POST", "fileSize": size}]},
    )
    errs = staged["stagedUploadsCreate"]["userErrors"]
    if errs:
        raise SystemExit("stage errors: " + json.dumps(errs))
    tgt = staged["stagedUploadsCreate"]["stagedTargets"][0]

    files = {p["name"]: (None, p["value"]) for p in tgt["parameters"]}
    with open(local_path, "rb") as fh:
        files["file"] = (target_name, fh, "video/mp4")
        up = requests.post(tgt["url"], files=files)
    if up.status_code not in (200, 201, 204):
        raise SystemExit(f"staged upload failed {up.status_code}: {up.text[:500]}")

    created = gql(
        """
        mutation create($files:[FileCreateInput!]!){
          fileCreate(files:$files){
            files{ id fileStatus alt }
            userErrors{ field message }
          }
        }""",
        {"files": [{"originalSource": tgt["resourceUrl"], "contentType": "VIDEO", "alt": target_name}]},
    )
    errs = created["fileCreate"]["userErrors"]
    if errs:
        raise SystemExit("fileCreate errors: " + json.dumps(errs))
    fid = created["fileCreate"]["files"][0]["id"]
    print(f"file id: {fid}  (transcoding...)", flush=True)

    # Poll until READY, then read mp4 source
    for i in range(120):
        node = gql(
            """query($id:ID!){ node(id:$id){ ... on Video {
                 fileStatus
                 sources{ url format mimeType height width }
                 preview{ image{ url } }
               } } }""",
            {"id": fid},
        )["node"]
        status = node.get("fileStatus")
        if status == "READY":
            sources = node.get("sources") or []
            mp4s = [s for s in sources if (s.get("mimeType") == "video/mp4" or s.get("format") == "mp4")]
            mp4s.sort(key=lambda s: s.get("height") or 0, reverse=True)
            best = (mp4s or sources)[0] if (mp4s or sources) else None
            poster = (node.get("preview") or {}).get("image") or {}
            print(json.dumps({
                "id": fid,
                "status": status,
                "mp4_url": best.get("url") if best else None,
                "height": best.get("height") if best else None,
                "poster": poster.get("url"),
                "all_sources": [s.get("url") for s in sources],
            }, indent=2))
            return
        if status == "FAILED":
            raise SystemExit(f"video processing FAILED: {json.dumps(node)}")
        time.sleep(5)
    raise SystemExit("timed out waiting for video to process")


if __name__ == "__main__":
    local = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local)
    upload(local, name)
