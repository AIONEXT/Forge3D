"""Commercial kit: pricing, SEO listing, compliance checklist."""
from __future__ import annotations


def build_kit(spec: dict, est: dict, printer: dict, material: dict) -> dict:
    cost = est["total_cost_usd"]
    # pricing ladder
    wholesale = round(cost * 2.2 + 1.5, 2)
    etsy = round(cost * 4.0 + 4.0, 2)
    amazon = round(cost * 4.6 + 5.0, 2)
    premium = round(cost * 6.0 + 6.0, 2)
    margin_etsy = round((etsy - cost) / etsy * 100, 1) if etsy else 0

    name = spec["product_name"]
    cat = spec["category"].replace("_", " ").title()
    dims = spec["dimensions_mm"]
    dim_str = f"{dims[0]:.0f} x {dims[1]:.0f} x {dims[2]:.0f} mm"

    seo_title = f"{name} — 3D Printed {cat} | {material['name']} | {dim_str} | Modern {spec['style'].title()} Decor"
    bullets = [
        f"Commercial-grade 3D print in {material['name']} on {printer['name']} — {spec['style']} {cat.lower()} design.",
        f"Size {dim_str}, {est['weight_g']}g, {est['layers']} precision layers at {est['layer_height_mm']}mm.",
        f"Features: {', '.join(spec['features'][:4])}.",
        "Printed to order, inspected, deburred & QC-checked — supports removed, edges eased.",
        "Eco-conscious made-to-order manufacturing: no warehousing, minimal waste.",
    ]
    description = (
        f"Meet the {name} — a made-to-order 3D printed {cat.lower()} designed for modern homes and workspaces.\n\n"
        f"SIZE: {dim_str}\nMATERIAL: {material['name']} ({material['blurb']})\n"
        f"PRINTER: {printer['name']}\nPRINT TIME: ~{est['print_hours']}h | WEIGHT: {est['weight_g']}g\n\n"
        f"FEATURES\n- " + "\n- ".join(spec["features"]) + "\n\n"
        "CARE: Wipe with damp cloth. Keep away from prolonged heat above "
        f"{material.get('nozzle_c', 200) - 120}C. Indoor use recommended unless PETG/ASA.\n\n"
        "Each piece is printed to order in small batches — slight layer-line texture is the signature of authentic 3D manufacture."
    )
    tags = list(dict.fromkeys([
        "3d printed", cat.lower(), material["name"].lower(), spec["style"] + " decor",
        "desk organizer" if "organiz" in cat.lower() else cat.lower(),
        "gift for him", "gift for her", "home decor", "small business",
        "made to order", "minimalist home", "office accessory",
    ]))[:13]

    hs_code = "3926.40" if material["compatible"] == ["FDM"] else "3926.90"
    checklist = [
        {"item": "Wall thickness ≥ 1.2mm verified", "ok": spec.get("wall_mm", 2) >= 1.2},
        {"item": "Fits printer build volume", "ok": est["fits_printer"]},
        {"item": "No food-contact claims (unless certified)", "ok": True},
        {"item": "No sharp edges — deburr step included", "ok": True},
        {"item": "Photos: 5 angles + scale reference required", "ok": False},
        {"item": "Add suffocation/child-safety label if small parts", "ok": True},
        {"item": f"HS code {hs_code} for customs", "ok": True},
    ]
    photo_prompts = [
        f"Studio product photo of {name.lower()}, {spec['style']} style, soft daylight, white background, 45° angle",
        "Lifestyle shot on wooden desk next to plant and laptop, cozy morning light",
        "Close-up macro of layer texture showing premium finish",
        "Scale shot with hand / coin for size reference",
        "Packaging flat-lay: kraft box, thank-you card, care instructions",
    ]
    return {
        "pricing": {"wholesale_usd": wholesale, "etsy_usd": etsy,
                    "amazon_usd": amazon, "premium_usd": premium,
                    "unit_cost_usd": cost, "margin_etsy_pct": margin_etsy},
        "seo_title": seo_title[:140],
        "bullets": bullets,
        "description": description,
        "tags": tags,
        "hs_code": hs_code,
        "checklist": checklist,
        "photo_prompts": photo_prompts,
    }
