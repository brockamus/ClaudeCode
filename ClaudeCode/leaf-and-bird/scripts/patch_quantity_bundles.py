"""
Patch the 3 product templates to use discount_pct + correct bundle config.
- product.serum.json: replace hardcoded price_2/price_3 with discount_pct_2/3
- product.tallow-body.json: same
- product.specialty.json: add new quantity_bundle block before add_to_cart
"""
import json
from pathlib import Path

TPL_DIR = Path("/Users/skitch/ClaudeCode/leaf-and-bird/theme-working/templates")

# Sensible defaults shared across all bundle blocks (mirrors existing serum/tallow look-and-feel)
BUNDLE_DEFAULTS = {
    "layout_type": "horizontal",
    "grid_show_images": True,
    "horizontal_show_images": False,
    "horizontal_image_height_desktop": 60,
    "horizontal_image_height_mobile": 45,
    "grid_image_width_desktop": 90,
    "grid_image_width_mobile": 60,
    "grid_image_max_height": 80,
    "quantity_1": 1,
    "title_1": "Single",
    "description_1": "",
    "show_badge_1": False,
    "badge_1": "",
    "quantity_2": 2,
    "title_2": "Bundle of 2",
    "compare_price_2": 0,
    "discount_pct_2": 10,
    "description_2": "",
    "show_badge_2": True,
    "badge_2": "POPULAR",
    "quantity_3": 3,
    "title_3": "Bundle of 3",
    "compare_price_3": 0,
    "discount_pct_3": 15,
    "description_3": "",
    "show_badge_3": True,
    "badge_3": "BEST VALUE",
    "quantity_4": 4,
    "title_4": "Bundle of 4",
    "description_4": "",
    "show_badge_4": True,
    "badge_4": "BEST VALUE",
    "card_width_desktop": 180,
    "card_min_height_desktop": 50,
    "card_min_height_mobile": 50,
    "card_margin_bottom": 40,
    "card_background": "#ffffff",
    "card_border_color": "#e5e5e5",
    "card_hover_border_color": "#FFBA46",  # use brand amber
    "selected_card_border_color": "#FFBA46",
    "selected_card_background": "#FFF8E8",
    "card_padding": 12,
    "card_border_width": 2,
    "selected_card_border_width": 2,
    "card_gap": 8,
    "border_radius": 8,
    "selected_card_inner_shadow": False,
    "selected_card_inner_shadow_color": "#000000",
    "no_image_content_gap": 12,
    "no_image_content_padding": 12,
    "badge_position_horizontal": "top-center",
    "badge_position_grid": "top-center",
    "badge_1_bg_color": "#22c55e", "badge_1_text_color": "#ffffff",
    "badge_1_use_gradient": False, "badge_1_gradient_start": "#22c55e", "badge_1_gradient_end": "#16a34a",
    "badge_1_enable_border": False, "badge_1_border_color": "#000000", "badge_1_border_width": 1, "badge_1_border_radius": 4,
    "badge_1_enable_shadow": False, "badge_1_shadow_blur": 8, "badge_1_shadow_offset": 2, "badge_1_shadow_opacity": 0.6,
    "badge_2_bg_color": "#FFBA46", "badge_2_text_color": "#1A1A1A",  # brand amber for POPULAR
    "badge_2_use_gradient": False, "badge_2_gradient_start": "#FFBA46", "badge_2_gradient_end": "#E59B1F",
    "badge_2_enable_border": False, "badge_2_border_color": "#000000", "badge_2_border_width": 1, "badge_2_border_radius": 4,
    "badge_2_enable_shadow": False, "badge_2_shadow_blur": 8, "badge_2_shadow_offset": 2, "badge_2_shadow_opacity": 0.6,
    "badge_3_bg_color": "#1A1A1A", "badge_3_text_color": "#FFBA46",  # inverse for BEST VALUE
    "badge_3_use_gradient": False, "badge_3_gradient_start": "#1A1A1A", "badge_3_gradient_end": "#000000",
    "badge_3_enable_border": False, "badge_3_border_color": "#000000", "badge_3_border_width": 1, "badge_3_border_radius": 4,
    "badge_3_enable_shadow": False, "badge_3_shadow_blur": 8, "badge_3_shadow_offset": 2, "badge_3_shadow_opacity": 0.6,
    "badge_4_bg_color": "#10b981", "badge_4_text_color": "#ffffff",
    "badge_4_use_gradient": False, "badge_4_gradient_start": "#10b981", "badge_4_gradient_end": "#059669",
    "badge_4_enable_border": False, "badge_4_border_color": "#000000", "badge_4_border_width": 1, "badge_4_border_radius": 4,
    "badge_4_enable_shadow": False, "badge_4_shadow_blur": 8, "badge_4_shadow_offset": 2, "badge_4_shadow_opacity": 0.6,
    "show_title": True, "show_description": True, "show_current_price": True,
    "show_original_price": True, "show_per_item_price": True,
    "title_color": "#333333", "title_font_size": 14,
    "description_color": "#666666", "description_font_size": 11,
    "current_price_color": "#333333", "current_price_font_size": 16,
    "original_price_color": "#999999", "original_price_font_size": 11,
    "title_font_size_mobile": 12, "description_font_size_mobile": 10,
    "current_price_font_size_mobile": 14, "original_price_font_size_mobile": 10,
    "per_item_price_suffix": "/each", "per_item_price_font_size": 14,
    "per_item_price_font_size_mobile": 12, "per_item_price_color": "#666666",
    "per_item_price_weight": "500", "per_item_price_opacity": 1,
    "per_item_enable_container": False, "per_item_container_bg": "#f5f5f5",
    "per_item_container_border_radius": 4, "per_item_container_padding_vertical": 4,
    "per_item_container_padding_horizontal": 8,
    "margin_top": 0, "margin_bottom": 0,
}

def patch_existing_block(path: Path):
    """Strip hardcoded price_2/price_3 from existing quantity_bundle and add discount_pct + amber styling."""
    with open(path) as f:
        data = json.load(f)
    sec_key = next(iter(data["sections"]))
    sec = data["sections"][sec_key]
    target_block_key = None
    for bk, bv in sec.get("blocks", {}).items():
        if bv.get("type") == "quantity_bundle":
            target_block_key = bk
            break
    if not target_block_key:
        raise RuntimeError(f"No quantity_bundle in {path.name}")
    block = sec["blocks"][target_block_key]
    settings = block.get("settings", {})
    # Drop hardcoded explicit prices
    for key in ("price_2", "price_3", "price_4"):
        settings.pop(key, None)
    # Apply new defaults (will overwrite color settings, add discount_pct_*)
    settings.update(BUNDLE_DEFAULTS)
    block["settings"] = settings
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return target_block_key

def add_block_to_specialty(path: Path):
    """Add a new quantity_bundle block to product.specialty.json before add_to_cart."""
    with open(path) as f:
        data = json.load(f)
    sec_key = next(iter(data["sections"]))
    sec = data["sections"][sec_key]
    new_block_key = "quantity_bundle_lb01"
    if new_block_key in sec.get("blocks", {}):
        raise RuntimeError("specialty already has block; aborting")
    sec.setdefault("blocks", {})[new_block_key] = {
        "type": "quantity_bundle",
        "settings": dict(BUNDLE_DEFAULTS),
    }
    bo = sec.get("block_order", [])
    # Insert before add_to_cart (a8)
    insert_idx = bo.index("a8") if "a8" in bo else len(bo)
    bo.insert(insert_idx, new_block_key)
    sec["block_order"] = bo
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return new_block_key

print("Patching product.serum.json…")
k = patch_existing_block(TPL_DIR / "product.serum.json")
print(f"  block {k}: removed price_2/price_3, added discount_pct + amber theming")

print("Patching product.tallow-body.json…")
k = patch_existing_block(TPL_DIR / "product.tallow-body.json")
print(f"  block {k}: removed price_2/price_3, added discount_pct + amber theming")

print("Adding bundle block to product.specialty.json…")
k = add_block_to_specialty(TPL_DIR / "product.specialty.json")
print(f"  added block {k} before a8 (add_to_cart)")

print("\nDone.")
