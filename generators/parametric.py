"""Procedural watertight-ish mesh generation + STL/OBJ/3MF export. Pure numpy."""
from __future__ import annotations
import math
import struct
import zipfile
import numpy as np


class Mesh:
    def __init__(self, verts: np.ndarray, faces: np.ndarray):
        self.verts = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
        self.faces = np.asarray(faces, dtype=np.int64).reshape(-1, 3)

    def merge(self, other: "Mesh") -> "Mesh":
        off = len(self.verts)
        v = np.vstack([self.verts, other.verts])
        f = np.vstack([self.faces, other.faces + off])
        return Mesh(v, f)

    def translate(self, dx=0, dy=0, dz=0) -> "Mesh":
        v = self.verts.copy()
        v += np.array([dx, dy, dz])
        return Mesh(v, self.faces)

    def scale(self, sx=1, sy=1, sz=1) -> "Mesh":
        v = self.verts.copy() * np.array([sx, sy, sz])
        return Mesh(v, self.faces)

    def volume_cm3(self) -> float:
        v = self.verts
        f = self.faces
        p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
        vol = np.sum(np.einsum("ij,ij->i", p0, np.cross(p1, p2))) / 6.0
        return abs(float(vol)) / 1000.0  # mm^3 -> cm^3

    def bbox(self):
        mn = self.verts.min(axis=0)
        mx = self.verts.max(axis=0)
        return mn, mx


def box(sx, sy, sz, center=(0, 0, 0)) -> Mesh:
    x, y, z = sx / 2, sy / 2, sz / 2
    v = np.array([[-x, -y, 0], [x, -y, 0], [x, y, 0], [-x, y, 0],
                  [-x, -y, sz], [x, -y, sz], [x, y, sz], [-x, y, sz]], float)
    v += np.array(center)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                  [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                  [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return Mesh(v, f)


def cylinder(r_top, r_bot, h, seg=48, center=(0, 0, 0)) -> Mesh:
    th = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ring_b = np.stack([np.cos(th) * r_bot, np.sin(th) * r_bot, np.zeros(seg)], 1)
    ring_t = np.stack([np.cos(th) * r_top, np.sin(th) * r_top, np.full(seg, h)], 1)
    v = [ring_b[i] for i in range(seg)] + [ring_t[i] for i in range(seg)]
    v += [np.array([0, 0, 0]), np.array([0, 0, h])]
    v = np.array(v) + np.array(center)
    cb, ct = 2 * seg, 2 * seg + 1
    faces = []
    for i in range(seg):
        j = (i + 1) % seg
        faces.append([i, j, seg + j])
        faces.append([i, seg + j, seg + i])
        faces.append([cb, j, i])
        faces.append([ct, seg + i, seg + j])
    return Mesh(v, np.array(faces))


def lathe(profile, seg=64) -> Mesh:
    """profile: list of (r, z)."""
    th = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    rings = []
    for (r, z) in profile:
        rings.append(np.stack([np.cos(th) * r, np.sin(th) * r, np.full(seg, z)], 1))
    v = np.vstack(rings)
    faces = []
    R = len(profile)
    for ri in range(R - 1):
        for i in range(seg):
            j = (i + 1) % seg
            a, b = ri * seg + i, ri * seg + j
            c, d = (ri + 1) * seg + j, (ri + 1) * seg + i
            faces.extend([[a, b, c], [a, c, d]])
    # caps
    c0 = len(v)
    v = np.vstack([v, [[0, 0, profile[0][1]], [0, 0, profile[-1][1]]]])
    for i in range(seg):
        j = (i + 1) % seg
        faces.append([c0, j, i])
        faces.append([c0 + 1, (R - 1) * seg + i, (R - 1) * seg + j])
    return Mesh(v, np.array(faces))


def extrude_polygon(poly2d, z0, z1) -> Mesh:
    n = len(poly2d)
    vb = [[x, y, z0] for x, y in poly2d]
    vt = [[x, y, z1] for x, y in poly2d]
    v = np.array(vb + vt, float)
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend([[i, j, n + j], [i, n + j, n + i]])
    # fan caps (assumes convex-ish; fine for our shapes)
    for i in range(1, n - 1):
        faces.append([0, i + 1, i])
        faces.append([n, n + i, n + i + 1])
    return Mesh(v, np.array(faces))


def gear_mesh(radius=40, teeth=18, thick=15) -> Mesh:
    poly = []
    for i in range(teeth * 2):
        r = radius if i % 2 == 0 else radius * 0.82
        a = 2 * math.pi * i / (teeth * 2)
        poly.append((math.cos(a) * r, math.sin(a) * r))
    return extrude_polygon(poly, 0, thick)


def _fit_to_dims(mesh: Mesh, dims) -> Mesh:
    mn, mx = mesh.bbox()
    size = (mx - mn)
    size[size == 0] = 1
    s = np.array(dims) / size
    v = (mesh.verts - mn) * s
    # sit on build plate
    v[:, 2] -= v[:, 2].min()
    return Mesh(v, mesh.faces)


def generate(spec: dict) -> Mesh:
    cat = spec["category"]
    dx, dy, dz = spec["dimensions_mm"]
    seed = spec.get("seed", 7)
    rng = np.random.default_rng(seed)
    style = spec.get("style", "modern")

    if cat == "vase":
        h = 1.0
        prof = []
        for i in range(14):
            t = i / 13
            wob = 1 + 0.12 * math.sin(t * 9 + seed % 7) if style == "organic" else 1 + 0.05 * math.sin(t * 6)
            r = (0.42 + 0.28 * math.sin(t * math.pi) ** 0.8 + 0.06 * math.sin(t * 12)) * wob
            prof.append((max(0.12, r), t * h))
        m = lathe(prof, seg=72)
        # close top rim inward slightly
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "planter":
        outer = lathe([(0.55, 0), (0.62, 0.85), (0.68, 1.0)], seg=56)
        tray = cylinder(0.62, 0.55, 0.08, seg=56, center=(0, 0, 0)).translate(0, 0, 0)
        m = outer.merge(tray)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "phone_stand":
        # wedge-ish prism + base
        base = box(1.0, 1.1, 0.12)
        back = box(1.0, 0.14, 0.9, center=(0, -0.42, 0.45))
        # tilt: shear back panel
        v = back.verts.copy()
        v[:, 1] += v[:, 2] * 0.35
        back = Mesh(v, back.faces)
        lip = box(1.0, 0.1, 0.12, center=(0, 0.4, 0.12))
        m = base.merge(back).merge(lip)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "coaster":
        m = cylinder(0.5, 0.5, 0.09, seg=56)
        rim = lathe([(0.5, 0), (0.52, 0.05), (0.5, 0.09)], seg=56)
        m = m.merge(rim)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "organizer":
        outer = box(1.5, 1.0, 0.6)
        # dividers
        d1 = box(0.04, 1.0, 0.5, center=(-0.25, 0, 0.3))
        d2 = box(0.04, 1.0, 0.5, center=(0.25, 0, 0.3))
        d3 = box(1.5, 0.04, 0.5, center=(0, 0, 0.3))
        m = outer.merge(d1).merge(d2).merge(d3)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat in ("hook", "bracket"):
        plate = box(0.6, 0.12, 0.8, center=(0, 0, 0.4))
        arm_pts = [(0.0, 0.0), (0.5, 0.05), (0.62, 0.3), (0.55, 0.55)]
        arm = None
        for (x0, z0), (x1, z1) in zip(arm_pts[:-1], arm_pts[1:]):
            segm = box(abs(x1 - x0) + 0.14, 0.3, abs(z1 - z0) + 0.14,
                       center=((x0 + x1) / 2 + 0.2, 0, (z0 + z1) / 2 + 0.2))
            arm = segm if arm is None else arm.merge(segm)
        m = plate.merge(arm)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "gear":
        m = gear_mesh(radius=0.5, teeth=14 + seed % 8, thick=0.25)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat == "lamp":
        prof = [(0.5, 0), (0.62, 0.4), (0.55, 0.75), (0.42, 1.0)]
        m = lathe(prof, seg=64)
        return _fit_to_dims(m, (dx, dy, dz))

    if cat in ("keychain", "dice"):
        m = box(1.0, 0.6, 0.12) if cat == "keychain" else box(0.4, 0.4, 0.4)
        return _fit_to_dims(m, (dx, dy, dz))

    # generic decor: faceted gem-like solid, scaled by seed
    n = 5 + seed % 3
    poly = [(math.cos(2 * math.pi * i / n) * 0.5, math.sin(2 * math.pi * i / n) * 0.5) for i in range(n)]
    m = extrude_polygon(poly, 0, 0.55 + (seed % 5) * 0.05)
    peb = cylinder(0.35, 0.5, 0.2, seg=32, center=(0, 0, 0.5))
    m = m.merge(peb)
    return _fit_to_dims(m, (dx, dy, dz))


# ---------- export ----------

def save_stl_binary(mesh: Mesh, path: str):
    v = mesh.verts.astype(np.float32)
    f = mesh.faces
    with open(path, "wb") as fh:
        fh.write(b"\x00" * 80)
        fh.write(struct.pack("<I", len(f)))
        for tri in f:
            p0, p1, p2 = v[tri[0]], v[tri[1]], v[tri[2]]
            n = np.cross(p1 - p0, p2 - p0)
            l = np.linalg.norm(n)
            n = n / l if l > 0 else np.array([0, 0, 1], np.float32)
            fh.write(struct.pack("<3f", *n))
            fh.write(struct.pack("<3f", *p0))
            fh.write(struct.pack("<3f", *p1))
            fh.write(struct.pack("<3f", *p2))
            fh.write(struct.pack("<H", 0))


def save_obj(mesh: Mesh, path: str):
    with open(path, "w") as fh:
        fh.write("# Forge3D auto-generated commercial model\n")
        for x, y, z in mesh.verts:
            fh.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for a, b, c in mesh.faces:
            fh.write(f"f {a+1} {b+1} {c+1}\n")


def save_3mf(mesh: Mesh, path: str):
    verts_xml = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in mesh.verts)
    tris_xml = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
<resources><object id="1" type="model"><mesh><vertices>{verts_xml}</vertices><triangles>{tris_xml}</triangles></mesh></object></resources>
<build><item objectid="1"/></build></model>'''
    content_types = '''<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("3D/3dmodel.model", model)
