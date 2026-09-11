"""Forge3D — AI product factory.

Run locally with:
    python app.py

Production WSGI entry point:
    gunicorn wsgi:app
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request

from flask import Flask, jsonify, render_template, request, send_from_directory

from ai_engine import commercial_pack, interpret
from config import AppConfig
from mesh_engine import build, mesh_volume_cm3, write_binary_stl
from providers import call_ai_provider
from printers_materials import (
    MATERIALS,
    PRINTERS,
    QUALITY,
    compatibility,
    get_material,
    get_printer,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:50] or "product"


def slice_estimate(vol_cm3: float, spec: dict, printer: dict, material: dict, quality_id: str):
    q = QUALITY.get(quality_id, QUALITY["standard"])
    infill = spec.get("infill_pct", 20)
    filament_cm3 = vol_cm3 * (0.30 + 0.70 * (infill / 100.0)) + vol_cm3 * 0.06
    if printer["tech"] == "MSLA":
        filament_cm3 = vol_cm3 * 1.02

    density = material["density_g_cm3"]
    weight_g = filament_cm3 * density * (1 + material["shrinkage_pct"] / 100.0 * 0.2)
    speed = q["speed_mm3_s"] * (0.45 if material["id"] == "tpu" else 1.0)
    hours = filament_cm3 * 1000 / speed / 3600 * q["time_mult"] + 0.25
    mat_cost = weight_g / 1000 * material["price_usd_kg"]
    machine_cost = hours * printer["hourly_rate_usd"]
    fail = q["fail_rate"]
    unit_cost = (mat_cost + machine_cost + 1.00) * (1 + fail)

    return {
        "filament_cm3": round(filament_cm3, 1),
        "weight_g": round(weight_g, 1),
        "hours": round(hours, 2),
        "material_cost": round(mat_cost, 2),
        "machine_cost": round(machine_cost, 2),
        "unit_cost": round(unit_cost, 2),
        "layer_h": q["layer_h"],
        "quality_label": q["label"],
    }


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    app.config["JSON_SORT_KEYS"] = False
    app.config["OUTPUT_DIR"] = OUTPUT_DIR

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({
            "ok": True,
            "service": "forge3d",
            "environment": app.config.get("ENV", "production"),
            "outputs_dir": os.path.isdir(OUTPUT_DIR),
        })

    @app.get("/ready")
    def ready():
        return jsonify({"ok": True, "status": "ready", "outputs_dir": os.path.isdir(OUTPUT_DIR)})

    @app.get("/api/printers")
    def api_printers():
        return jsonify(PRINTERS)

    @app.get("/api/materials")
    def api_materials():
        return jsonify(MATERIALS)

    @app.post("/api/run")
    def api_run():
        data = request.get_json(force=True) or {}
        description = (data.get("description") or "").strip()
        if len(description) < 4:
            return jsonify({"error": "Please enter a product description (min 4 chars)."}), 400

        try:
            scale = float(data.get("scale", 1.0) or 1.0)
            margin = float(data.get("margin", 0.55))
        except (TypeError, ValueError):
            return jsonify({"error": "Scale and margin must be numeric values."}), 400

        if not 0.25 <= scale <= 2.5:
            return jsonify({"error": "Scale must be between 0.25 and 2.5."}), 400

        margin = max(0.1, min(0.9, margin))
        printer = get_printer(data.get("printer_id", "bambu_x1c"))
        material = get_material(data.get("material_id", "pla"))
        quality_id = data.get("quality_id", "standard")
        ok, compat_msg = compatibility(printer, material)

        t0 = time.time()
        spec = interpret(description, scale)
        verts, faces = build(spec)
        vol = mesh_volume_cm3(verts, faces)

        dims = spec["dims_mm"]
        bw, bd, bh = printer["build"]
        fits = dims[0] <= bw and dims[1] <= bd and dims[2] <= bh
        shrink = material["shrinkage_pct"]
        dims_final = [round(d * (1 + shrink / 100), 1) for d in dims]

        est = slice_estimate(vol, spec, printer, material, quality_id)
        pack = commercial_pack(
            spec,
            description,
            printer,
            material,
            est["weight_g"],
            est["hours"],
            est["unit_cost"],
            margin,
        )

        fname = f"{slug(pack['title'])}-{pack['sku'].lower()}.stl"
        stl_path = os.path.join(OUTPUT_DIR, fname)
        write_binary_stl(stl_path, verts, faces, pack["sku"])

        bundle = {
            "spec": spec,
            "printer": printer,
            "material": material,
            "estimate": est,
            "listing": pack,
            "validation": {
                "compatible": ok,
                "compat_msg": compat_msg,
                "fits_bed": fits,
                "bed_msg": ("Fits " + printer["name"] + f" ({bw}x{bd}x{bh}mm).") if fits
                else (f"TOO BIG for {printer['name']} ({bw}x{bd}x{bh}mm). Reduce size or pick Voron/K2 Plus."),
                "dims_final_mm": dims_final,
                "triangles": int(len(faces)),
                "volume_cm3": round(vol, 1),
            },
            "files": {"stl": f"/download/{fname}", "stl_name": fname},
            "elapsed_s": round(time.time() - t0, 2),
        }

        with open(os.path.join(OUTPUT_DIR, fname.replace(".stl", ".json")), "w", encoding="utf-8") as fh:
            json.dump(bundle, fh, indent=2)

        return jsonify(bundle)

    @app.post("/api/copy-boost")
    def api_boost():
        data = request.get_json(force=True) or {}
        listing = data.get("listing", {})
        provider = (data.get("provider") or os.getenv("AI_PROVIDER") or "offline").strip().lower()
        model = data.get("model") or os.getenv("AI_MODEL") or "gpt-4o-mini"
        out = call_ai_provider("", provider=provider, model=model, listing=listing)
        if out.get("ok"):
            return jsonify(out)
        return jsonify({
            "ok": False,
            "msg": out.get("msg", "No AI provider configured — using built-in copy."),
        })

    @app.get("/download/<path:name>")
    def download(name: str):
        return send_from_directory(OUTPUT_DIR, name, as_attachment=True)

    @app.errorhandler(404)
    def handle_404(_error):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def handle_500(_error):
        return jsonify({"error": "Internal server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=int(app.config["PORT"]), debug=app.config["DEBUG"], threaded=True)
