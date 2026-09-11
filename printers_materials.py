"""Printer + material database with real-world specs."""
from __future__ import annotations

PRINTERS = [
    {"id": "bambu_x1c", "name": "Bambu Lab X1 Carbon", "tech": "FDM", "build": [256, 256, 256],
     "nozzle": 0.4, "enclosed": True, "hourly_rate_usd": 2.50, "max_temp": 300,
     "notes": "Fast enclosed CoreXY. Handles ABS/ASA/Nylon."},
    {"id": "bambu_p1s", "name": "Bambu Lab P1S", "tech": "FDM", "build": [256, 256, 256],
     "nozzle": 0.4, "enclosed": True, "hourly_rate_usd": 1.90, "max_temp": 300,
     "notes": "Workhorse enclosed printer."},
    {"id": "prusa_mk4s", "name": "Prusa MK4S", "tech": "FDM", "build": [250, 210, 220],
     "nozzle": 0.4, "enclosed": False, "hourly_rate_usd": 1.50, "max_temp": 300,
     "notes": "Open frame. Best with PLA/PETG/TPU."},
    {"id": "ender3_v3", "name": "Creality Ender 3 V3", "tech": "FDM", "build": [220, 220, 250],
     "nozzle": 0.4, "enclosed": False, "hourly_rate_usd": 1.00, "max_temp": 260,
     "notes": "Budget open printer. PLA/PETG only recommended."},
    {"id": "voron_24", "name": "Voron 2.4 (350mm)", "tech": "FDM", "build": [350, 350, 350],
     "nozzle": 0.4, "enclosed": True, "hourly_rate_usd": 2.20, "max_temp": 300,
     "notes": "Large enclosed. Great for big ABS/ASA parts."},
    {"id": "kobra3", "name": "Anycubic Kobra 3 Combo", "tech": "FDM", "build": [250, 250, 260],
     "nozzle": 0.4, "enclosed": False, "hourly_rate_usd": 1.40, "max_temp": 260,
     "notes": "Multicolor capable, open frame."},
    {"id": "mars4", "name": "Elegoo Mars 4 (Resin MSLA)", "tech": "MSLA", "build": [153, 77, 165],
     "nozzle": 0.0, "enclosed": True, "hourly_rate_usd": 2.00, "max_temp": 0,
     "notes": "High-detail resin. Small build volume."},
    {"id": "k2plus", "name": "Creality K2 Plus", "tech": "FDM", "build": [350, 350, 350],
     "nozzle": 0.4, "enclosed": True, "hourly_rate_usd": 2.40, "max_temp": 300,
     "notes": "Large enclosed multicolor."},
]

MATERIALS = [
    {"id": "pla", "name": "PLA", "density_g_cm3": 1.24, "price_usd_kg": 22.0,
     "shrinkage_pct": 0.3, "tech": ["FDM"], "needs_enclosure": False,
     "print_temp": 210, "strength": 6, "finish": "Matte/silk options, easy print",
     "desc": "Best default for sellable products. Low warp, crisp details."},
    {"id": "petg", "name": "PETG", "density_g_cm3": 1.27, "price_usd_kg": 24.0,
     "shrinkage_pct": 0.5, "tech": ["FDM"], "needs_enclosure": False,
     "print_temp": 240, "strength": 8, "finish": "Glossy, tough, weather resistant",
     "desc": "Functional + outdoor-safe. Slightly harder than PLA."},
    {"id": "abs", "name": "ABS", "density_g_cm3": 1.04, "price_usd_kg": 26.0,
     "shrinkage_pct": 1.5, "tech": ["FDM"], "needs_enclosure": True,
     "print_temp": 250, "strength": 8, "finish": "Strong, acetone-smoothable",
     "desc": "Needs enclosed printer. Strong functional parts."},
    {"id": "asa", "name": "ASA", "density_g_cm3": 1.07, "price_usd_kg": 32.0,
     "shrinkage_pct": 1.4, "tech": ["FDM"], "needs_enclosure": True,
     "print_temp": 255, "strength": 9, "finish": "UV-stable, outdoor king",
     "desc": "Outdoor/automotive grade. Needs enclosure."},
    {"id": "tpu", "name": "TPU 95A", "density_g_cm3": 1.21, "price_usd_kg": 30.0,
     "shrinkage_pct": 0.6, "tech": ["FDM"], "needs_enclosure": False,
     "print_temp": 225, "strength": 7, "finish": "Flexible rubber-like",
     "desc": "Flexible parts: grips, feet, phone cases. Print slow."},
    {"id": "nylon", "name": "Nylon PA12", "density_g_cm3": 1.14, "price_usd_kg": 55.0,
     "shrinkage_pct": 1.8, "tech": ["FDM"], "needs_enclosure": True,
     "print_temp": 260, "strength": 10, "finish": "Extremely tough, gears/tools",
     "desc": "Premium engineering. Dry box + enclosure required."},
    {"id": "wood", "name": "Wood PLA", "density_g_cm3": 1.15, "price_usd_kg": 34.0,
     "shrinkage_pct": 0.3, "tech": ["FDM"], "needs_enclosure": False,
     "print_temp": 205, "strength": 5, "finish": "Real wood look, stainable",
     "desc": "Decor/vases with premium feel. Sells at higher price."},
    {"id": "resin", "name": "Standard Resin", "density_g_cm3": 1.15, "price_usd_kg": 38.0,
     "shrinkage_pct": 0.8, "tech": ["MSLA"], "needs_enclosure": False,
     "print_temp": 0, "strength": 6, "finish": "Ultra-high detail, smooth",
     "desc": "Miniatures, jewelry, detailed decor. Resin printer only."},
]

QUALITY = {
    "draft": {"label": "Draft 0.28mm", "layer_h": 0.28, "speed_mm3_s": 18.0, "time_mult": 0.6, "fail_rate": 0.03},
    "standard": {"label": "Standard 0.20mm", "layer_h": 0.20, "speed_mm3_s": 12.0, "time_mult": 1.0, "fail_rate": 0.05},
    "fine": {"label": "Fine 0.12mm", "layer_h": 0.12, "speed_mm3_s": 7.0, "time_mult": 1.7, "fail_rate": 0.07},
    "ultra": {"label": "Ultra 0.08mm (resin-like)", "layer_h": 0.08, "speed_mm3_s": 4.5, "time_mult": 2.6, "fail_rate": 0.10},
}


def get_printer(pid: str) -> dict:
    for p in PRINTERS:
        if p["id"] == pid:
            return p
    return PRINTERS[0]


def get_material(mid: str) -> dict:
    for m in MATERIALS:
        if m["id"] == mid:
            return m
    return MATERIALS[0]


def compatibility(printer: dict, material: dict) -> tuple[bool, str]:
    if material["id"] == "resin" and printer["tech"] != "MSLA":
        return False, f'{material["name"]} needs a resin (MSLA) printer — {printer["name"]} is {printer["tech"]}.'
    if printer["tech"] == "MSLA" and material["id"] != "resin":
        return False, f'{printer["name"]} is resin-only. Select Standard Resin.'
    if material.get("needs_enclosure") and not printer.get("enclosed"):
        return False, (f'{material["name"]} needs an enclosed printer ({printer["name"]} is open). '
                        'Pick Bambu X1C / P1S / Voron / K2 Plus, or switch to PLA/PETG.')
    return True, "Compatible: printer + material + temps OK."
