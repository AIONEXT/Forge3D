"""Printer + material database with real-world profiles for cost/time estimation."""
from __future__ import annotations

PRINTERS = {
    "bambu_x1c": {
        "id": "bambu_x1c", "name": "Bambu Lab X1 Carbon", "type": "FDM",
        "build_volume_mm": [256, 256, 256], "nozzle_mm": 0.4,
        "max_speed_mms": 500, "avg_speed_mms": 180, "power_w": 350,
        "hourly_rate_usd": 2.50, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.08, 0.12, 0.16, 0.2, 0.28],
        "notes": "Fast CoreXY, best for commercial PLA/PETG production."
    },
    "prusa_mk4": {
        "id": "prusa_mk4", "name": "Prusa MK4", "type": "FDM",
        "build_volume_mm": [250, 210, 220], "nozzle_mm": 0.4,
        "max_speed_mms": 200, "avg_speed_mms": 90, "power_w": 240,
        "hourly_rate_usd": 1.75, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.1, 0.15, 0.2, 0.3],
        "notes": "Workhorse, great dimensional accuracy for functional parts."
    },
    "ender3_v3": {
        "id": "ender3_v3", "name": "Creality Ender 3 V3", "type": "FDM",
        "build_volume_mm": [220, 220, 250], "nozzle_mm": 0.4,
        "max_speed_mms": 300, "avg_speed_mms": 120, "power_w": 350,
        "hourly_rate_usd": 1.25, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.12, 0.2, 0.28],
        "notes": "Budget high-volume farm printer."
    },
    "voron_24": {
        "id": "voron_24", "name": "Voron 2.4 350", "type": "FDM",
        "build_volume_mm": [350, 350, 350], "nozzle_mm": 0.4,
        "max_speed_mms": 400, "avg_speed_mms": 160, "power_w": 800,
        "hourly_rate_usd": 2.00, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.1, 0.2, 0.3],
        "notes": "Large format, enclosed — ideal for ABS/ASA/Nylon."
    },
    "elegoo_mars4": {
        "id": "elegoo_mars4", "name": "Elegoo Mars 4 (MSLA)", "type": "SLA",
        "build_volume_mm": [153, 77, 165], "nozzle_mm": 0.0,
        "max_speed_mms": 0, "avg_speed_mms": 0, "power_w": 60,
        "hourly_rate_usd": 2.00, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.025, 0.05, 0.1],
        "notes": "High-detail resin, best for miniatures/jewelry."
    },
    "formlabs_3": {
        "id": "formlabs_3", "name": "Formlabs Form 3+ (SLA)", "type": "SLA",
        "build_volume_mm": [145, 145, 185], "nozzle_mm": 0.0,
        "max_speed_mms": 0, "avg_speed_mms": 0, "power_w": 150,
        "hourly_rate_usd": 4.50, "energy_usd_kwh": 0.15,
        "layer_options_mm": [0.025, 0.05, 0.1],
        "notes": "Pro resin, engineering + commercial finish."
    },
}

MATERIALS = {
    "pla": {"id": "pla", "name": "PLA", "compatible": ["FDM"],
            "density_g_cm3": 1.24, "cost_usd_kg": 22.0, "shrinkage_pct": 0.3,
            "nozzle_c": 210, "bed_c": 60, "strength": 6, "finish": 8,
            "food_safe": False, "outdoor": False,
            "blurb": "Easiest, best surface for decorative products."},
    "petg": {"id": "petg", "name": "PETG", "compatible": ["FDM"],
             "density_g_cm3": 1.27, "cost_usd_kg": 25.0, "shrinkage_pct": 0.5,
             "nozzle_c": 240, "bed_c": 80, "strength": 8, "finish": 7,
             "food_safe": False, "outdoor": True,
             "blurb": "Strong + weather resistant, great for functional sale items."},
    "abs": {"id": "abs", "name": "ABS", "compatible": ["FDM"],
            "density_g_cm3": 1.04, "cost_usd_kg": 24.0, "shrinkage_pct": 1.5,
            "nozzle_c": 250, "bed_c": 100, "strength": 8, "finish": 7,
            "food_safe": False, "outdoor": True,
            "blurb": "Tough, acetone-smoothable. Needs enclosure."},
    "asa": {"id": "asa", "name": "ASA", "compatible": ["FDM"],
            "density_g_cm3": 1.07, "cost_usd_kg": 32.0, "shrinkage_pct": 1.4,
            "nozzle_c": 255, "bed_c": 100, "strength": 8, "finish": 8,
            "food_safe": False, "outdoor": True,
            "blurb": "UV-stable ABS upgrade for outdoor commercial products."},
    "tpu": {"id": "tpu", "name": "TPU 95A", "compatible": ["FDM"],
            "density_g_cm3": 1.21, "cost_usd_kg": 34.0, "shrinkage_pct": 0.6,
            "nozzle_c": 230, "bed_c": 50, "strength": 9, "finish": 6,
            "food_safe": False, "outdoor": True,
            "blurb": "Flexible — phone cases, grips, seals."},
    "nylon": {"id": "nylon", "name": "Nylon PA12", "compatible": ["FDM"],
              "density_g_cm3": 1.14, "cost_usd_kg": 58.0, "shrinkage_pct": 1.8,
              "nozzle_c": 270, "bed_c": 90, "strength": 10, "finish": 6,
              "food_safe": False, "outdoor": True,
              "blurb": "Engineering-grade, premium pricing."},
    "resin_std": {"id": "resin_std", "name": "Standard Resin", "compatible": ["SLA"],
                  "density_g_cm3": 1.15, "cost_usd_kg": 38.0, "shrinkage_pct": 0.4,
                  "nozzle_c": 0, "bed_c": 0, "strength": 5, "finish": 10,
                  "food_safe": False, "outdoor": False,
                  "blurb": "Ultra detail for miniatures & jewelry."},
    "resin_tough": {"id": "resin_tough", "name": "Tough/ABS-like Resin", "compatible": ["SLA"],
                    "density_g_cm3": 1.18, "cost_usd_kg": 55.0, "shrinkage_pct": 0.5,
                    "nozzle_c": 0, "bed_c": 0, "strength": 8, "finish": 9,
                    "food_safe": False, "outdoor": False,
                    "blurb": "Functional resin parts, premium finish."},
}


def get_printer(pid: str) -> dict:
    return PRINTERS.get(pid, PRINTERS["bambu_x1c"])


def get_material(mid: str) -> dict:
    return MATERIALS.get(mid, MATERIALS["pla"])


def compatibility_warning(printer: dict, material: dict) -> str | None:
    if material["compatible"] and printer["type"] not in material["compatible"]:
        return (
            f"{material['name']} is { '/'.join(material['compatible'])}-only but "
            f"{printer['name']} is {printer['type']}. Auto-switched profile applied — "
            f"for best results pick a matching printer/material pair."
        )
    return None
