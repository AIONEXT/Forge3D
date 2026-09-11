"""AI designer — interprets free-text product description into a build spec.

Runs fully offline with a rule-based engine. If OPENAI_API_KEY is set and
`openai` package is installed, it will optionally refine the spec via LLM.
"""
from __future__ import annotations
import os
import re
import hashlib

CATEGORY_KEYWORDS = {
    "vase": ["vase", "flower", "bouquet"],
    "planter": ["planter", "plant pot", "succulent", "herb garden"],
    "phone_stand": ["phone stand", "phone holder", "mobile stand", "iphone stand", "smartphone"],
    "headphone_stand": ["headphone", "headset stand"],
    "organizer": ["organizer", "organiser", "desk tidy", "storage box", "pen holder", "drawer"],
    "hook": ["hook", "hanger", "wall hook", "coat"],
    "shelf": ["shelf", "wall shelf", "display shelf"],
    "lamp": ["lamp", "lampshade", "light shade", "lantern"],
    "gear": ["gear", "cog", "mechanical"],
    "bracket": ["bracket", "mount", "holder", "gopro"],
    "coaster": ["coaster", "cup mat", "drink mat"],
    "keychain": ["keychain", "keyring", "key chain"],
    "dice": ["dice", "d20", "board game"],
    "toy": ["toy", "figurine", "dragon", "robot toy", "car toy", "figur"],
    "soap_dish": ["soap dish", "sponge holder"],
    "cable_holder": ["cable", "cord holder", "wire clip"],
}

STYLE_KEYWORDS = {
    "minimalist": ["minimal", "clean", "simple", "scandi"],
    "modern": ["modern", "sleek", "contemporary"],
    "organic": ["organic", "wavy", "nature", "flowing"],
    "geometric": ["geometric", "hex", "honeycomb", "low poly", "faceted"],
    "artdeco": ["art deco", "luxury", "elegant", "premium"],
    "industrial": ["industrial", "rugged", "mechanical"],
    "cute": ["cute", "kawaii", "fun", "kids", "children"],
}

SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(mm|cm|inch|in|cm)?", re.IGNORECASE)


def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in t for k in kws):
            return cat
    # fallback heuristics
    if any(w in t for w in ["stand", "dock"]):
        return "phone_stand"
    if any(w in t for w in ["box", "tray", "container"]):
        return "organizer"
    if any(w in t for w in ["ring", "jewelry", "pendant"]):
        return "keychain"
    return "generic_decor"


def detect_style(text: str) -> str:
    t = text.lower()
    for style, kws in STYLE_KEYWORDS.items():
        if any(k in t for k in kws):
            return style
    return "modern"


def extract_size_mm(text: str, category: str) -> list[float]:
    nums = SIZE_RE.findall(text)
    vals = []
    for n, unit in nums:
        v = float(n)
        u = (unit or "").lower()
        if u in ("cm",):
            v *= 10
        elif u in ("inch", "in"):
            v *= 25.4
        elif v < 3:  # likely cm given bare like "12cm vase" missed
            pass
        vals.append(v)
    defaults = {
        "vase": [110, 110, 180], "planter": [120, 120, 110],
        "phone_stand": [90, 110, 80], "headphone_stand": [140, 160, 240],
        "organizer": [150, 100, 70], "hook": [60, 40, 70],
        "shelf": [180, 90, 60], "lamp": [140, 140, 180],
        "gear": [80, 80, 20], "bracket": [80, 60, 50],
        "coaster": [100, 100, 8], "keychain": [50, 30, 6],
        "dice": [20, 20, 20], "toy": [90, 60, 110],
        "soap_dish": [120, 90, 25], "cable_holder": [60, 30, 20],
        "generic_decor": [100, 100, 60],
    }
    base = defaults.get(category, [100, 100, 60])
    if len(vals) >= 3:
        return [max(8, min(340, vals[0])), max(8, min(340, vals[1])), max(5, min(340, vals[2]))]
    if len(vals) == 1:
        s = max(8, min(340, vals[0]))
        # scale proportionally
        bx, by, bz = base
        m = max(bx, by, bz)
        return [round(bx / m * s, 1), round(by / m * s, 1), round(bz / m * s, 1)]
    return base


def _seed(text: str) -> int:
    return int(hashlib.md5(text.lower().encode()).hexdigest()[:8], 16)


def build_spec(description: str, printer_id: str, material_id: str,
               style_hint: str = "", size_hint: str = "") -> dict:
    text = f"{description} {style_hint} {size_hint}".strip()
    category = detect_category(text)
    style = detect_style(style_hint + " " + description) if style_hint or description else "modern"
    dims = extract_size_mm(text, category)

    seed = _seed(description + printer_id + material_id)

    features = []
    tl = text.lower()
    if "honeycomb" in tl or "hex" in tl:
        features.append("honeycomb texture")
    if "drain" in tl or category == "planter":
        features.append("drainage hole + drip tray")
    if "cable" in tl or category in ("phone_stand", "organizer"):
        features.append("cable routing slot")
    if "wall" in tl or category in ("hook", "shelf"):
        features.append("keyhole wall-mount + screw recess")
    if "lid" in tl or "box" in tl:
        features.append("snap-fit lid")
    if "logo" in tl or "text" in tl or "name" in tl:
        features.append("embossed branding plate")
    if not features:
        features = {
            "vase": ["water-tight spiral profile", "felt-safe base"],
            "planter": ["drainage hole + drip tray", "soil ribbing"],
            "phone_stand": ["62° ergonomic angle", "cable routing slot", "anti-slip base"],
            "coaster": ["heat-resistant profile", "stackable rim", "cork-pad recess"],
            "organizer": ["modular grid compartments", "stackable", "label plates"],
            "hook": ["45kg-rated ribbed core", "keyhole mount", "fillet-reinforced neck"],
            "lamp": ["E27-safe vented shell", "diffuser-optimized wall 1.6mm"],
            "gear": ["involute teeth", "5mm shaft bore", "printed-place ready"],
            "generic_decor": ["display-ready finish", "weighted base", "felt-pad recess"],
        }.get(category, ["display-ready finish", "weighted base"])

    complexity = "medium"
    if len(description.split()) > 40 or len(features) > 3:
        complexity = "high"
    elif len(description.split()) < 8:
        complexity = "low"

    # Human readable product name from description
    words = re.sub(r"[^a-zA-Z0-9 ]", "", description).split()[:5]
    title_core = " ".join(w.title() for w in words) if words else category.replace("_", " ").title()

    spec = {
        "product_name": title_core,
        "category": category,
        "style": style,
        "dimensions_mm": [round(float(d), 1) for d in dims],
        "features": features,
        "complexity": complexity,
        "seed": seed,
        "wall_mm": 1.6 if category in ("vase", "lamp") else 2.0,
        "infill_pct": 12 if category in ("vase", "lamp", "coaster") else 20,
        "supports": category in ("hook", "shelf", "headphone_stand", "lamp"),
        "notes": f"Auto-designed from: '{description[:160]}'",
    }

    # Optional LLM refinement (graceful fallback)
    llm_used = False
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            import json as _json, urllib.request as _url
            prompt = (
                "You are a 3D-print product designer. Given product description, return JSON with keys: "
                "product_name, features (list of <=5 short strings), wall_mm, infill_pct, supports(bool). "
                f"Description: {description} Category:{category} Style:{style} Dims:{dims}"
            )
            req = _url.Request(
                "https://api.openai.com/v1/chat/completions",
                data=_json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5, "max_tokens": 300,
                    "response_format": {"type": "json_object"},
                }).encode(),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
            with _url.urlopen(req, timeout=20) as r:
                out = _json.loads(r.read().decode())
            content = out["choices"][0]["message"]["content"]
            refined = _json.loads(content)
            for k in ("product_name", "features", "wall_mm", "infill_pct", "supports"):
                if k in refined:
                    spec[k] = refined[k]
            llm_used = True
        except Exception:
            pass
    spec["llm_refined"] = llm_used
    return spec
