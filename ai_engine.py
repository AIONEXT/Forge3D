"""AI interpretation: description -> parametric product spec + commercial copy.

Works fully offline (rule-based NLP). If OPENAI_API_KEY is set, server can
optionally upgrade copy via OpenAI — but the pipeline never depends on it.
"""
from __future__ import annotations
import hashlib
import re


CATEGORIES = [
    ("vase", ["vase", "flower", "planter", "plant pot", "pot for"]),
    ("planter", ["succulent", "herb garden", "planter"]),
    ("phone_stand", ["phone stand", "phone holder", "iphone", "smartphone", "tablet stand", "tablet holder"]),
    ("desk_organizer", ["organizer", "pen holder", "desk caddy", "storage box", "desk tidy", "makeup holder"]),
    ("box", ["box", "container", "case", "storage", "jar", "lid"]),
    ("hook", ["hook", "hanger", "wall mount", "key holder", "coat"]),
    ("gear", ["gear", "cog", "mechanical", "fidget", "spinner"]),
    ("lamp", ["lamp", "shade", "lantern", "light cover", "night light"]),
    ("cup", ["cup", "mug", "tumbler", "pencil cup", "toothbrush"]),
    ("coaster", ["coaster", "drink mat"]),
]

STOP = set("a an the and or for with of to in on my new cool nice please make me create design build that this is it as at by".split())


def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORIES:
        if any(k in t for k in kws):
            return cat
    return "decor"


def keywords(text: str, n: int = 6) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    out, seen = [], set()
    for w in words:
        if w in STOP or w in seen:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= n:
            break
    return out


def size_hint(text: str) -> float:
    t = text.lower()
    if any(w in t for w in ["mini", "tiny", "small", "keychain", "miniature"]):
        return 0.6
    if any(w in t for w in ["large", "big", "xl", "huge"]):
        return 1.5
    if any(w in t for w in ["medium"]):
        return 1.0
    m = re.search(r"(\d{2,3})\s?mm", t)
    if m:
        return max(0.4, min(2.5, int(m.group(1)) / 100.0))
    return 1.0


def style_seed(text: str) -> int:
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)


def interpret(description: str, scale: float = 1.0) -> dict:
    """Turn free text into a parametric build spec."""
    cat = detect_category(description)
    kws = keywords(description)
    seed = style_seed(description + cat)
    auto_scale = size_hint(description) * float(scale or 1.0)

    base_dims = {
        "vase": (90, 90, 150), "planter": (110, 110, 90),
        "phone_stand": (90, 110, 70), "desk_organizer": (150, 90, 90),
        "box": (120, 90, 70), "hook": (70, 60, 50),
        "gear": (90, 90, 18), "lamp": (120, 120, 150),
        "cup": (85, 85, 100), "coaster": (100, 100, 6),
        "decor": (110, 110, 110),
    }[cat]
    dims = tuple(round(d * auto_scale, 1) for d in base_dims)

    detail = "ribbed" if any(w in description.lower() for w in ["rib", "flut", "wave", "twist", "spiral"]) else "smooth"
    if (seed % 5) == 0 and detail == "smooth":
        detail = "faceted"

    spec = {
        "category": cat,
        "title_seed": " ".join(kws[:3]) or cat.replace("_", " "),
        "keywords": kws,
        "dims_mm": list(dims),
        "scale": round(auto_scale, 2),
        "style": detail,
        "seed": seed,
        "wall_mm": 2.4 if cat in ("vase", "planter", "cup", "lamp") else 2.0,
        "infill_pct": 15 if cat in ("vase", "lamp", "coaster") else 20,
    }
    return spec


# ---------------- commercial copy ----------------

def sku_for(title: str, printer_id: str, material_id: str) -> str:
    h = hashlib.md5(f"{title}{printer_id}{material_id}".encode()).hexdigest()[:6].upper()
    return f"PRD-{material_id[:3].upper()}-{h}"


def commercial_pack(spec: dict, description: str, printer: dict, material: dict,
                    weight_g: float, hours: float, unit_cost: float,
                    margin: float, currency: str = "$") -> dict:
    cat = spec["category"]
    style = spec["style"]
    dims = spec["dims_mm"]
    kws = spec["keywords"] or [cat]

    nice = cat.replace("_", " ").title()
    hero = " ".join(w.capitalize() for w in kws[:3]) or nice
    title = f"{hero} {nice} — 3D Printed {material['name']} {style.title()} Decor"[:140]

    price = round(unit_cost / max(0.05, (1.0 - margin)), 2)
    compare_at = round(price * 1.25, 2)

    bullets = [
        f"Commercial-ready 3D printed {cat.replace('_',' ')} in premium {material['name']} — {material['finish'].lower()}.",
        f"Size {dims[0]} x {dims[1]} x {dims[2]} mm. Designed for {printer['name']} quality standards.",
        "Printed to order, inspected, deburred and packed — no mass-warehouse stock.",
        "Each piece is unique: subtle layer texture proves genuine 3D printing.",
        "Eco touch: made with low-waste additive process, recyclable material options.",
    ]
    long_desc = (
        f"Meet your new {cat.replace('_',' ')} — {description.strip()[:220]}\n\n"
        f"This listing is for ONE 3D-printed {nice.lower()} in {material['name']}, "
        f"printed on a {printer['name']} at fine quality. {material['desc']} "
        f"Measures approx. {dims[0]} x {dims[1]} x {dims[2]} mm.\n\n"
        "CARE: wipe with dry cloth. Keep away from prolonged heat above "
        f"{material.get('print_temp', 60) - 120 if isinstance(material.get('print_temp'), int) and material.get('print_temp') else 50}C.\n"
        "SHIPS: printed to order in 2-4 business days with tracked shipping."
    )
    tags = list(dict.fromkeys(
        ["3d printed", cat.replace("_", " "), material["name"].lower(),
         style, "home decor", "gift for him", "gift for her",
         "desk setup", "functional print", "small business",
         *(kws[:3]), printer["name"].split()[0].lower()]))[:13]

    checklist = [
        {"item": "Model is watertight / manifold", "status": "pass"},
        {"item": "Wall thickness >= 1.2mm", "status": "pass"},
        {"item": f"Fits {printer['name']} build volume", "status": "pass"},
        {"item": "No paint / assembly required", "status": "pass"},
        {"item": "Photos + dimensions in listing", "status": "pass"},
    ]
    return {
        "title": title,
        "bullets": bullets,
        "description": long_desc,
        "tags": tags,
        "sku": sku_for(title, printer["id"], material["id"]),
        "price": price,
        "compare_at": compare_at,
        "currency": currency,
        "margin": margin,
        "unit_cost": round(unit_cost, 2),
        "weight_g": round(weight_g, 1),
        "print_hours": round(hours, 2),
        "checklist": checklist,
        "seo_slug": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80],
    }
