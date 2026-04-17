"""Shared Shopify Admin API client for Leaf & Bird SEO project."""
import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error

SHOP = os.environ["SHOPIFY_SHOP"]
TOKEN = os.environ["SHOPIFY_TOKEN"]
API_VERSION = "2024-10"
BASE = f"https://{SHOP}/admin/api/{API_VERSION}"


def _request(method, path, body=None, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code} on {method} {url}: {body_text}")


def get(path, params=None):
    return _request("GET", path, params=params)


def post(path, body):
    return _request("POST", path, body=body)


def put(path, body):
    return _request("PUT", path, body=body)


def delete(path):
    return _request("DELETE", path)


def shop():
    return get("/shop.json")["shop"]


if __name__ == "__main__":
    s = shop()
    print(f"Connected to: {s['name']} ({s['myshopify_domain']})")
    print(f"Plan: {s.get('plan_name')}  |  Currency: {s['currency']}  |  Timezone: {s['iana_timezone']}")
