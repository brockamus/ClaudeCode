"""Enable cart_progress_bar block in cart drawer with amber fill + clean copy."""
import json, urllib.request

THEME_ID = 186951631147
TOKEN = "SHOPIFY_TOKEN_REDACTED"
URL = f"https://leaf-and-bird.myshopify.com/admin/api/2024-10/themes/{THEME_ID}/assets.json"

def fetch(key: str) -> str:
    req = urllib.request.Request(
        f"{URL}?asset%5Bkey%5D={key.replace('/', '%2F')}",
        headers={"X-Shopify-Access-Token": TOKEN},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["asset"]["value"]

def push(key: str, value: str):
    req = urllib.request.Request(
        URL,
        data=json.dumps({"asset": {"key": key, "value": value}}).encode(),
        method="PUT",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
        return r.status, d["asset"]["size"], d["asset"]["updated_at"]

# Pull current settings_data
sd_raw = fetch("config/settings_data.json")
sd = json.loads(sd_raw)
cart_drawer = sd["current"]["sections"]["cart-drawer"]
print("Existing cart-drawer block_order:", cart_drawer.get("block_order", []))

# Build the progress_bar block settings — amber fill, no free-product, hide icons (cleaner)
progress_bar_id = "lb_cart_progress_bar"
progress_bar_block = {
    "type": "cart_progress_bar",
    "settings": {
        "shipping_away_text": "You're [missingAmount] away from FREE shipping",
        "free_product_away_text": "",
        "shipping_earn_text": "🎉 Free shipping unlocked!",
        "free_product_earn_text": "",
        "product_free_shipping": 50,
        "product_free_amount": 0,
        "hide_icons_single_goal": True,
        "hide_icons_container_padding": 12,
        "hide_icons_text_padding": 8,
        "hide_icons_progress_bar_height": 8,
        "hide_icons_progress_bar_margin_top": 4,
        "hide_icons_progress_bar_active_color": "#FFBA46",
        "hide_icons_progress_bar_inactive_color": "#F2F2F2",
        "hide_icons_enable_gradient": False,
        "progress_text_font_size": 14,
        "reward_name_font_size": 10,
        "cart_drawer_progress_active_color": "#FFBA46",
        "cart_drawer_progress_inactive_color": "#F2F2F2",
        "cart_drawer_progress_active_icon_fill_color": "#1A1A1A",
        "enable_progress_bar_gradient": False,
        "enable_progress_bar_border": False,
    },
}

# Add the block + put it FIRST so it shows at top of drawer
cart_drawer.setdefault("blocks", {})[progress_bar_id] = progress_bar_block
new_order = [progress_bar_id] + [k for k in cart_drawer.get("block_order", []) if k != progress_bar_id]
cart_drawer["block_order"] = new_order

print("New cart-drawer block_order:", cart_drawer["block_order"])

# Push
status, size, updated = push("config/settings_data.json", json.dumps(sd, indent=2))
print(f"\nsettings_data.json: {status}  size={size}  updated={updated}")
