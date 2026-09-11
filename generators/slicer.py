"""Slicer-style estimation: weight, time, cost from mesh volume."""
from __future__ import annotations
import math


def estimate(mesh, spec: dict, printer: dict, material: dict, quality: str = "standard") -> dict:
    vol_solid = mesh.volume_cm3()
    infill = spec.get("infill_pct", 15) / 100.0
    wall = spec.get("wall_mm", 2.0)
    mn, mx = mesh.bbox()
    dims = (mx - mn)
    height = float(dims[2])

    # hollow-ish correction for vase/lamp spiral mode
    hollow_factor = 0.35 if spec["category"] in ("vase", "lamp") else 1.0
    eff_vol = vol_solid * (0.25 + 0.75 * infill) * hollow_factor + float(dims[0] * dims[1]) / 100 * 0.06
    weight_g = eff_vol * material["density_g_cm3"]

    layer_h = {"draft": 0.28, "standard": 0.2, "fine": 0.12, "ultra": 0.05}.get(quality, 0.2)
    if printer["type"] == "SLA":
        layer_h = {"draft": 0.1, "standard": 0.05, "fine": 0.025, "ultra": 0.025}.get(quality, 0.05)
        layers = max(1, height / layer_h)
        hours = layers * 0.035 + weight_g * 0.02  # resin cure model
    else:
        layers = max(1, height / layer_h)
        flow_mms = printer["avg_speed_mms"] * layer_h * printer.get("nozzle_mm", 0.4)  # mm^3/s approx
        flow_mms = max(flow_mms, 1.0)
        vol_mm3 = eff_vol * 1000
        hours = vol_mm3 / flow_mms / 3600 + layers * 4 / 3600 + 0.15  # heat-up + travel

    mat_cost = weight_g / 1000 * material["cost_usd_kg"]
    machine_cost = hours * printer["hourly_rate_usd"]
    energy_cost = printer["power_w"] / 1000 * hours * printer["energy_usd_kwh"]
    fail_allowance = (mat_cost + machine_cost) * 0.07
    total_cost = mat_cost + machine_cost + energy_cost + fail_allowance

    fits = all(d <= b + 1e-6 for d, b in zip(dims, printer["build_volume_mm"]))
    fit_note = "Fits build volume." if fits else "WARNING: exceeds build volume — auto-scaled to fit." 

    return {
        "volume_cm3": round(vol_solid, 2),
        "effective_cm3": round(eff_vol, 2),
        "weight_g": round(weight_g, 1),
        "layers": int(layers),
        "layer_height_mm": layer_h,
        "print_hours": round(hours, 2),
        "material_cost_usd": round(mat_cost, 2),
        "machine_cost_usd": round(machine_cost, 2),
        "energy_cost_usd": round(energy_cost, 2),
        "total_cost_usd": round(total_cost, 2),
        "fits_printer": bool(fits),
        "fit_note": fit_note,
        "supports_needed": bool(spec.get("supports")),
        "triangles": int(len(mesh.faces)),
    }
