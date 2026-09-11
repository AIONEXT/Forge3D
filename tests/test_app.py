"""Tests for Forge3D application."""
from __future__ import annotations

import os

import pytest

from ai_engine import commercial_pack, detect_category, interpret, sku_for
from app import create_app, slug
from mesh_engine import build, mesh_volume_cm3
from printers_materials import compatibility, get_material, get_printer


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealth:
    def test_index(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert b"Forge3D" in r.data

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["service"] == "forge3d"

    def test_ready(self, client):
        r = client.get("/ready")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["status"] == "ready"

    def test_404(self, client):
        r = client.get("/nonexistent")
        assert r.status_code == 404
        assert "error" in r.get_json()


class TestAPI:
    def test_api_printers(self, client):
        r = client.get("/api/printers")
        assert r.status_code == 200
        printers = r.get_json()
        assert len(printers) > 0
        assert any(p["id"] == "bambu_x1c" for p in printers)

    def test_api_materials(self, client):
        r = client.get("/api/materials")
        assert r.status_code == 200
        materials = r.get_json()
        assert len(materials) > 0

    def test_api_run_valid(self, client):
        r = client.post("/api/run", json={
            "description": "ribbed twist vase, modern home decor",
            "printer_id": "bambu_x1c",
            "material_id": "pla",
            "quality_id": "standard",
            "scale": 1.0,
            "margin": 0.55,
        })
        assert r.status_code == 200
        data = r.get_json()
        assert "listing" in data
        assert "validation" in data
        assert "estimate" in data
        assert data["validation"]["compatible"] is True

    def test_api_run_invalid_description(self, client):
        r = client.post("/api/run", json={"description": "hi"})
        assert r.status_code == 400
        assert "error" in r.get_json()

    def test_api_run_invalid_scale(self, client):
        r = client.post("/api/run", json={
            "description": "test product",
            "scale": 5.0,
        })
        assert r.status_code == 400

    def test_api_run_missing_json(self, client):
        r = client.post("/api/run", data="not json", content_type="application/json")
        assert r.status_code == 400
        assert r.get_json()["error"]

    def test_api_copy_boost_offline(self, client):
        r = client.post("/api/copy-boost", json={"listing": {"title": "test"}})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is False

    def test_api_download(self, client):
        r = client.get("/download/test.stl")
        assert r.status_code == 404


class TestSlug:
    def test_slug_basic(self):
        assert slug("Hello World") == "hello-world"

    def test_slug_special_chars(self):
        assert slug("ribbed twist vase!@#") == "ribbed-twist-vase"

    def test_slug_empty(self):
        assert slug("   ") == "product"


class TestAIEngine:
    def test_detect_category(self):
        assert detect_category("vase for flowers") == "vase"
        assert detect_category("phone stand for desk") == "phone_stand"
        assert detect_category("unknown item") == "decor"

    def test_interpret(self):
        spec = interpret("ribbed twist vase, modern home decor", 1.0)
        assert spec["category"] == "vase"
        assert "dims_mm" in spec
        assert "style" in spec
        assert spec["style"] == "ribbed"

    def test_interpret_scale(self):
        spec = interpret("small vase", 0.5)
        assert spec["scale"] < 1.0


class TestPrintersMaterials:
    def test_get_printer(self):
        p = get_printer("bambu_x1c")
        assert p["name"] == "Bambu Lab X1 Carbon"

    def test_get_material(self):
        m = get_material("pla")
        assert m["name"] == "PLA"

    def test_compatibility_ok(self):
        p = get_printer("bambu_x1c")
        m = get_material("pla")
        ok, _msg = compatibility(p, m)
        assert ok is True

    def test_compatibility_resin_fdm(self):
        p = get_printer("bambu_x1c")
        m = get_material("resin")
        ok, _msg = compatibility(p, m)
        assert ok is False

    def test_compatibility_enclosure(self):
        p = get_printer("prusa_mk4s")
        m = get_material("abs")
        ok, _msg = compatibility(p, m)
        assert ok is False


class TestMeshEngine:
    def test_box_mesh(self):
        from mesh_engine import box_mesh
        v, f = box_mesh(10, 10, 10)
        assert len(v) == 8
        assert len(f) == 12

    def test_cylinder_mesh(self):
        from mesh_engine import cylinder_mesh
        v, f = cylinder_mesh(5, 5, 20, seg=24)
        assert len(v) > 0
        assert len(f) > 0

    def test_build_vase(self):
        spec = {"category": "vase", "dims_mm": [100, 100, 150], "seed": 1, "style": "smooth"}
        v, f = build(spec)
        assert len(v) > 0
        assert len(f) > 0

    def test_build_phone_stand(self):
        spec = {"category": "phone_stand", "dims_mm": [90, 110, 70], "seed": 1, "style": "smooth"}
        v, _f = build(spec)
        assert len(v) > 0

    def test_volume(self):
        from mesh_engine import box_mesh
        v, f = box_mesh(10, 10, 10)
        vol = mesh_volume_cm3(v, f)
        assert vol > 0
        assert abs(vol - 1.0) < 0.01

    def test_write_stl(self):
        import tempfile

        from mesh_engine import box_mesh, write_binary_stl

        v, f = box_mesh(10, 10, 10)
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tf:
            path = tf.name
        write_binary_stl(path, v, f, "test")
        assert os.path.exists(path)
        os.unlink(path)

    def test_lathe_mesh(self):
        from mesh_engine import lathe_mesh
        prof = [(10, 0), (10, 50)]
        v, f = lathe_mesh(prof, seg=24)
        assert len(v) > 0
        assert len(f) > 0


class TestCommercialPack:
    def test_commercial_pack(self):
        spec = {"category": "vase", "keywords": ["ribbed", "twist"], "dims_mm": [100, 100, 150], "style": "ribbed", "seed": 1, "wall_mm": 2.4, "infill_pct": 15}
        material = {"name": "PLA", "id": "pla", "finish": "Matte", "density_g_cm3": 1.24, "price_usd_kg": 22.0, "shrinkage_pct": 0.3, "print_temp": 210, "desc": "Best default for sellable products. Low warp, crisp details.", "tech": ["FDM"], "needs_enclosure": False}
        printer = {"name": "Bambu X1C", "id": "bambu_x1c"}
        result = commercial_pack(spec, "ribbed twist vase", printer, material, 200.0, 5.0, 10.0, 0.55)
        assert "title" in result
        assert "bullets" in result
        assert "price" in result
        assert "sku" in result
        assert result["price"] > 0
        assert len(result["bullets"]) > 0

    def test_sku_format(self):
        sku = sku_for("test vase", "bambu_x1c", "pla")
        assert sku.startswith("PRD-PLA-")
        assert len(sku) > 8
