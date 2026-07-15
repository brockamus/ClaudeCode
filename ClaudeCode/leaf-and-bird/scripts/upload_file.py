"""Upload local image(s) to Shopify Files (shop_images) via GraphQL staged upload.

Usage: python upload_file.py <local.png> [<filename-on-shopify.png>] ...
Prints the shopify://shop_images/<name> reference and CDN url for each.
"""
import os, sys, time, json, mimetypes, urllib.request
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
    mime = mimetypes.guess_type(local_path)[0] or "image/png"
    size = str(os.path.getsize(local_path))

    staged = gql(
        """
        mutation stage($input:[StagedUploadInput!]!){
          stagedUploadsCreate(input:$input){
            stagedTargets{ url resourceUrl parameters{ name value } }
            userErrors{ field message }
          }
        }""",
        {"input": [{"filename": target_name, "mimeType": mime, "resource": "IMAGE",
                    "httpMethod": "POST", "fileSize": size}]},
    )
    errs = staged["stagedUploadsCreate"]["userErrors"]
    if errs:
        raise SystemExit("stage errors: " + json.dumps(errs))
    tgt = staged["stagedUploadsCreate"]["stagedTargets"][0]

    # POST the file to the staged target
    files = {p["name"]: (None, p["value"]) for p in tgt["parameters"]}
    with open(local_path, "rb") as fh:
        files["file"] = (target_name, fh, mime)
        up = requests.post(tgt["url"], files=files)
    if up.status_code not in (200, 201, 204):
        raise SystemExit(f"staged upload failed {up.status_code}: {up.text[:500]}")

    created = gql(
        """
        mutation create($files:[FileCreateInput!]!){
          fileCreate(files:$files){
            files{ id alt fileStatus
              ... on MediaImage { image { url } } }
            userErrors{ field message }
          }
        }""",
        {"files": [{"originalSource": tgt["resourceUrl"], "contentType": "IMAGE",
                    "alt": target_name}]},
    )
    errs = created["fileCreate"]["userErrors"]
    if errs:
        raise SystemExit("fileCreate errors: " + json.dumps(errs))
    fid = created["fileCreate"]["files"][0]["id"]

    # Poll until READY to get the CDN url
    url = None
    for _ in range(20):
        node = gql(
            """query($id:ID!){ node(id:$id){ ... on MediaImage { fileStatus image{ url } } } }""",
            {"id": fid},
        )["node"]
        if node and node.get("fileStatus") == "READY" and node.get("image"):
            url = node["image"]["url"]
            break
        time.sleep(1.5)

    fname = (url or target_name).split("/")[-1].split("?")[0]
    ref = f"shopify://shop_images/{fname}"
    print(json.dumps({"local": local_path, "id": fid, "cdn": url, "ref": ref}))
    return ref


if __name__ == "__main__":
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        local = args[i]
        name = args[i + 1] if i + 1 < len(args) and not os.path.exists(args[i + 1]) else os.path.basename(local)
        if name != os.path.basename(local):
            i += 2
        else:
            i += 1
        upload(local, name)
