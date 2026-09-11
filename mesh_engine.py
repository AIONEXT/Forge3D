"""Procedural watertight-ish mesh builders (numpy only) + binary STL writer."""
from __future__ import annotations
import math
import os
import struct
import numpy as np


# ---------- primitives ----------

def box_mesh(w: float, h: float, d: float, cx=0.0, cy=0.0, cz=0.0):
    x, y, z = w / 2, h / 2, d / 2
    v = np.array([
        [cx - x, cy - y, cz - z], [cx + x, cy - y, cz - z],
        [cx + x, cy + y, cz - z], [cx - x, cy + y, cz - z],
        [cx - x, cy - y, cz + z], [cx + x, cy - y, cz + z],
        [cx + x, cy + y, cz + z], [cx - x, cy + y, cz + z],
    ], float)
    f = np.array([
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [3, 2, 6], [3, 6, 7],
        [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2],
    ])
    return v, f


def cylinder_mesh(r_top: float, r_bot: float, h: float, seg: int = 48, cy: float = 0.0):
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ct, st = np.cos(ang), np.sin(ang)
    y0, y1 = cy - h / 2, cy + h / 2
    bot = np.stack([r_bot * ct, np.full(seg, y0), r_bot * st], 1)
    top = np.stack([r_top * ct, np.full(seg, y1), r_top * st], 1)
    v = np.vstack([bot, top, [[0, y0, 0], [0, y1, 0]]])
    cb, ct_ = 2 * seg, 2 * seg + 1
    faces = []
    for i in range(seg):
        j = (i + 1) % seg
        faces.append([i, seg + i, seg + j])
        faces.append([i, seg + j, j])
        faces.append([cb, j, i])
        faces.append([ct_, seg + i, seg + j])
    return v, np.array(faces)


def lathe_mesh(profile: list[tuple[float, float]], seg: int = 64,
               twist: float = 0.0, rib_amp: float = 0.0, ribs: int = 8,
               facet: bool = False, seed: int = 0):
    """profile: list of (radius, y). Revolve around Y."""
    if facet:
        seg = max(7, seg // 8)
    rings = []
    for (r, y) in profile:
        ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
        rr = np.full(seg, r)
        if rib_amp:
            rr = rr + rib_amp * np.sin(ang * ribs + seed % 7)
        tw = (y * twist) if twist else 0.0
        rings.append(np.stack([rr * np.cos(ang + tw), np.full(seg, y), rr * np.sin(ang + tw)], 1))
    v = np.vstack(rings)
    nrow = len(profile)
    faces = []
    for r_i in range(nrow - 1):
        for i in range(seg):
            j = (i + 1) % seg
            a, b = r_i * seg + i, r_i * seg + j
            c, d = (r_i + 1) * seg + i, (r_i + 1) * seg + j
            faces.append([a, c, d])
            faces.append([a, d, b])
    # caps
    bot_c = len(v); v = np.vstack([v, [[0, profile[0][1], 0]]])
    top_c = len(v); v = np.vstack([v, [[0, profile[-1][1], 0]]])
    for i in range(seg):
        j = (i + 1) % seg
        faces.append([bot_c, j, i])
        base = (nrow - 1) * seg
        faces.append([top_c, base + i, base + j])
    return v, np.array(faces)


def gear_mesh(radius: float, teeth: int = 12, thick: float = 12.0, seg_per_tooth: int = 4):
    pts = []
    for t in range(teeth):
        for k in range(seg_per_tooth):
            a = 2 * math.pi * (t + k / seg_per_tooth) / teeth
            rr = radius if (k % 2 == 0) else radius * 0.82
            pts.append((rr * math.cos(a), rr * math.sin(a)))
    n = len(pts)
    z0, z1 = -thick / 2, thick / 2
    bot = np.array([[x, y, z0] for x, y in pts])
    top = np.array([[x, y, z1] for x, y in pts])
    v = np.vstack([bot, top, [[0, 0, z0], [0, 0, z1]]])
    # hole
    hr = radius * 0.18
    hs = 16
    ang = np.linspace(0, 2 * math.pi, hs, endpoint=False)
    hbot = np.stack([hr * np.cos(ang), hr * np.sin(ang), np.full(hs, z0)], 1)
    htop = np.stack([hr * np.cos(ang), hr * np.sin(ang), np.full(hs, z1)], 1)
    hb, ht = len(v), len(v) + hs
    v = np.vstack([v, hbot, htop])
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces += [[i, n + i, n + j], [i, n + j, j]]
    cb, ct_ = 2 * n, 2 * n + 1
    hole_cap = [[hb + (i + 1) % hs, hb + i, cb] for i in range(hs)]
    hole_cap += [[ht + i, ht + (i + 1) % hs, ct_] for i in range(hs)]
    # outer ring around hole (annulus fans)
    for i in range(n):
        j = (i + 1) % n
    faces += hole_cap
    # inner hole walls
    for i in range(hs):
        j = (i + 1) % hs
        faces += [[hb + i, hb + j, ht + j], [hb + i, ht + j, ht + i]]
    return v, np.array(faces)


def rotate_x(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    return v @ R.T


def rotate_z(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return v @ R.T


def merge(meshes):
    vs, fs, off = [], [], 0
    for v, f in meshes:
        vs.append(v)
        fs.append(f + off)
        off += len(v)
    return np.vstack(vs), np.vstack(fs)


# ---------- product builders (units: mm, origin at base center) ----------

def build(spec: dict):
    cat = spec["category"]
    W, D, H = spec["dims_mm"]
    seed = spec.get("seed", 1)
    style = spec.get("style", "smooth")
    rib = 2.2 if style == "ribbed" else 0.0
    facet = style == "faceted"
    seg = 72
    y = lambda h: h  # base at 0

    if cat == "vase":
        prof = [(W*0.30, 0), (W*0.46, H*0.12), (W*0.52, H*0.45),
                (W*0.44, H*0.75), (W*0.34, H*0.92), (W*0.36, H)]
        return lathe_mesh(prof, seg, twist=0.6 if rib else 0.0, rib_amp=rib, ribs=10, facet=facet, seed=seed)
    if cat == "lamp":
        prof = [(W*0.32, 0), (W*0.5, H*0.35), (W*0.55, H*0.7), (W*0.42, H)]
        shade = lathe_mesh(prof, seg, rib_amp=rib, ribs=12, facet=facet, seed=seed)
        v2, f2 = cylinder_mesh(W*0.30, W*0.34, 10, 48, cy=5)
        return merge([(shade[0], shade[1]), (v2, f2)])
    if cat == "planter":
        v1, f1 = cylinder_mesh(W*0.46, W*0.36, H*0.8, seg, cy=H*0.45)
        v2, f2 = cylinder_mesh(W*0.52, W*0.52, H*0.12, seg, cy=H*0.9)
        return merge([(v1, f1), (v2, f2)])
    if cat == "cup":
        prof = [(W*0.30, 0), (W*0.42, H*0.1), (W*0.46, H*0.6), (W*0.48, H)]
        return lathe_mesh(prof, seg, rib_amp=rib, ribs=9, facet=facet, seed=seed)
    if cat == "coaster":
        v, f = cylinder_mesh(W/2, W/2, H, 64, cy=H/2)
        if rib:  # embossed rings via vertex lift
            c = v.mean(0)
            r = np.linalg.norm(v[:, [0, 2]] - c[[0, 2]], axis=1)
            v[:, 1] += (np.sin(r / 4.0) * 0.8 * (v[:, 1] > H * 0.9))
        return v, f
    if cat == "phone_stand":
        base = box_mesh(W, 8, D, 0, 4, 0)
        back = box_mesh(W, H, 8, 0, H/2 + 4, -D/2 + 12)
        back = (rotate_x(back[0], -18), back[1])
        lip = box_mesh(W, 14, 8, 0, 11, D/2 - 10)
        return merge([base, back, lip])
    if cat == "desk_organizer":
        t = 4.0
        bottom = box_mesh(W, t, D, 0, t/2, 0)
        fwall = box_mesh(W, H, t, 0, H/2, D/2 - t/2)
        bwall = box_mesh(W, H, t, 0, H/2, -D/2 + t/2)
        lwall = box_mesh(t, H, D, -W/2 + t/2, H/2, 0)
        rwall = box_mesh(t, H, D, W/2 - t/2, H/2, 0)
        div = box_mesh(t/2, H*0.7, D - 8, -W/6, H*0.35 + t, 0)
        return merge([bottom, fwall, bwall, lwall, rwall, div])
    if cat == "box":
        t = 4.0
        bottom = box_mesh(W, t, D, 0, t/2, 0)
        walls = [box_mesh(W, H, t, 0, H/2, D/2 - t/2), box_mesh(W, H, t, 0, H/2, -D/2 + t/2),
                 box_mesh(t, H, D, -W/2 + t/2, H/2, 0), box_mesh(t, H, D, W/2 - t/2, H/2, 0)]
        lid = box_mesh(W + 3, 10, D + 3, 0, H + 5, 0)
        return merge([bottom, *walls, lid])
    if cat == "hook":
        plate = box_mesh(8, H, W*0.8, 0, H/2, 0)
        # curved arm: arc of small cylinders merged
        parts = [plate]
        arm_r, n = W*0.45, 7
        for i in range(n):
            a = math.pi * (0.1 + 0.8 * i / (n - 1))
            x = arm_r * math.cos(a) + arm_r
            yy = H*0.85 + arm_r * math.sin(a) * 0.7
            v, f = cylinder_mesh(7, 7, 12, 20, cy=0)
            v = rotate_x(v, 90)
            v += np.array([x, yy, 0])
            parts.append((v, f))
        return merge(parts)
    if cat == "gear":
        return gear_mesh(min(W, D)/2, teeth=12 + seed % 6, thick=max(10, H*0.25))
    # decor / fallback: twisted sculptural piece
    prof = [(W*0.28, 0), (W*0.5, H*0.3), (W*0.42, H*0.6), (W*0.5, H*0.85), (W*0.3, H)]
    return lathe_mesh(prof, seg, twist=1.2, rib_amp=2.5, ribs=6 + seed % 5, facet=facet, seed=seed)


# ---------- metrics + STL ----------

def mesh_volume_cm3(v: np.ndarray, f: np.ndarray) -> float:
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    vol = np.einsum("ij,ij->i", p0, np.cross(p1, p2)).sum() / 6.0
    return abs(float(vol)) / 1000.0


def write_binary_stl(path: str, v: np.ndarray, f: np.ndarray, name: str = "product"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    p0, p1, p2 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm[norm == 0] = 1
    n = n / norm
    with open(path, "wb") as fh:
        fh.write(struct.pack("<80sI", f"Binary STL {name}".encode()[:80].ljust(80, b" "), len(f)))
        for i in range(len(f)):
            fh.write(struct.pack("<12fH", *n[i], *p0[i], *p1[i], *p2[i], 0))
