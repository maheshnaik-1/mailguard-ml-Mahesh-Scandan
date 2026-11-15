"""Procedurally render the Sun Halo / Rainbow Dance / Dragon Head Dance background."""
import colorsys
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates

OUT = sys.argv[1]
W, H = 1920, 1080
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def screen(base, layer):
    layer = np.clip(layer, 0, 1)
    return 1 - (1 - base) * (1 - layer)


def hsv2rgb(h, s, v):
    h = (h % 1.0) * 6
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    s = np.broadcast_to(s, h.shape).astype(np.float32)
    v = np.broadcast_to(v, h.shape).astype(np.float32)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1).astype(np.float32)


def glow(cx, cy, r, col, k):
    d2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)
    return (np.exp(-d2) * k)[..., None] * np.array(col, np.float32)


# ---------- night sky ----------
t = yy / H
top = np.array([0x1F, 0x0A, 0x3A], np.float32) / 255
mid = np.array([0x12, 0x06, 0x1E], np.float32) / 255
bot = np.array([0x08, 0x02, 0x10], np.float32) / 255
a = np.clip(t / 0.45, 0, 1)[..., None]
b = np.clip((t - 0.45) / 0.55, 0, 1)[..., None]
img = np.where((t < 0.45)[..., None], top * (1 - a) + mid * a, mid * (1 - b) + bot * b).astype(np.float32)
img = screen(img, glow(260, 1120, 760, (0.10, 0.65, 1.0), 0.34))
img = screen(img, glow(1760, 1120, 760, (1.0, 0.30, 0.85), 0.32))

# ---------- sun halo ----------
cx, cy = 1190, 290
d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
th = np.arctan2(yy - cy, xx - cx)
img = screen(img, glow(cx, cy, 620, (1.0, 0.38, 0.10), 0.42))
img = screen(img, glow(cx, cy, 260, (1.0, 0.55, 0.2), 0.28))

fine = (0.5 + 0.5 * np.cos(90 * th)) ** 8
env = np.exp(-(((d - 520) / 320) ** 2)) * (d > 290)
img = screen(img, (fine * env * 0.26)[..., None] * np.array((1, 0.78, 0.28), np.float32))
sparse = (0.5 + 0.5 * np.cos(16 * th + 0.6)) ** 30
env2 = np.exp(-(d - 260) / 650) * (d > 262)
img = screen(img, (sparse * env2 * 0.24)[..., None] * np.array((1, 0.85, 0.45), np.float32))
rb_rays = hsv2rgb(th / (2 * np.pi), 0.8, 1.0)
sparse3 = (0.5 + 0.5 * np.cos(10 * th + 2.0)) ** 40
img = screen(img, (sparse3 * env2 * 0.20)[..., None] * rb_rays)

R = 262
img = screen(img, (np.exp(-(((d - R) / 3.5) ** 2)))[..., None] * np.array((1, 0.96, 0.75), np.float32))
img = screen(img, (np.exp(-(((d - R) / 28) ** 2)) * 0.65)[..., None] * np.array((1, 0.68, 0.2), np.float32))
disc = np.clip(1 - d / R, 0, 1) ** 0.7
img = screen(img, (disc * 0.07)[..., None] * np.array((1, 0.5, 0.2), np.float32))
rb = hsv2rgb(th / (2 * np.pi), 0.85, 1.0)
img = screen(img, (np.exp(-(((d - 350) / 11) ** 2)) * 0.9)[..., None] * rb)
img = screen(img, (np.exp(-(((d - 350) / 40) ** 2)) * 0.3)[..., None] * rb)
rb2 = hsv2rgb(-th / (2 * np.pi) + 0.5, 0.8, 1.0)
img = screen(img, (np.exp(-(((d - 410) / 4) ** 2)) * 0.5)[..., None] * rb2)


# ---------- dragon ribbon ----------
def bez(p0, p1, p2, p3, n):
    tt = np.linspace(0, 1, n)[:, None]
    return ((1 - tt) ** 3) * p0 + 3 * ((1 - tt) ** 2) * tt * p1 + 3 * (1 - tt) * tt * tt * p2 + tt ** 3 * p3


P = np.array
seg1 = bez(P([-160, 1010.0]), P([180, 720.0]), P([430, 1130.0]), P([720, 820.0]), 320)
seg2 = bez(P([720, 820.0]), P([900, 640.0]), P([740, 520.0]), P([930, 470.0]), 280)
path = np.vstack([seg1, seg2[1:]])
n = len(path)
s = np.linspace(0, 1, n)
width = 6 + 46 * s ** 1.3
alpha = np.clip(s / 0.12, 0, 1) ** 1.5
stops = [0.0, 0.4, 0.75, 1.0]
cols = np.array([(0.85, 0.08, 0.18), (1.0, 0.45, 0.10), (1.0, 0.78, 0.20), (1.0, 0.93, 0.70)], np.float32)
col = np.stack([np.interp(s, stops, cols[:, k]) for k in range(3)], 1).astype(np.float32)


def accumulate(wscale, mix_white):
    acc_c = np.zeros((H, W, 3), np.float32)
    acc_a = np.zeros((H, W), np.float32)
    for i in range(n):
        x, y = path[i]
        w = width[i] * wscale
        Rr = int(w * 1.6) + 2
        x0, x1 = int(max(0, x - Rr)), int(min(W, x + Rr + 1))
        y0, y1 = int(max(0, y - Rr)), int(min(H, y + Rr + 1))
        if x0 >= x1 or y0 >= y1:
            continue
        dd = np.sqrt((xx[y0:y1, x0:x1] - x) ** 2 + (yy[y0:y1, x0:x1] - y) ** 2) / w
        wt = np.clip(1 - dd ** 2, 0, 1) ** 1.4 * alpha[i]
        c = col[i] * (1 - mix_white) + np.array((1, 0.97, 0.85), np.float32) * mix_white
        acc_a[y0:y1, x0:x1] += wt * 0.10
        acc_c[y0:y1, x0:x1] += wt[..., None] * 0.10 * c
    a_ = np.clip(acc_a, 0, 1)
    return acc_c / (acc_a[..., None] + 1e-6) * a_[..., None], a_


body, body_a = accumulate(1.0, 0.0)
core, core_a = accumulate(0.42, 0.55)
ribbon = np.clip(body * 0.85 + core * 0.12, 0, 1)


def noise(sigma, amp):
    n1 = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma)
    return n1 / (n1.std() + 1e-6) * amp


def warp(arr, dx, dy):
    coords = [yy + dy, xx + dx]
    if arr.ndim == 2:
        return map_coordinates(arr, coords, order=1, mode="nearest")
    return np.stack([map_coordinates(arr[..., c], coords, order=1, mode="nearest") for c in range(arr.shape[-1])], -1)


flame = warp(ribbon, noise(22, 14), noise(22, 14))
wisp_mask = np.clip(gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 6) * 6 + 0.35, 0, 1)
wisps = warp(ribbon, noise(9, 12), noise(9, 12) + 30) * wisp_mask[..., None] * 0.55

# ---------- dragon head ----------
E = path[-1]
u = path[-1] - path[-9]
u = u / np.linalg.norm(u)
nrm = np.array([-u[1], u[0]])
HS = 1.3


def L2I(pt):
    return tuple(E + HS * (pt[0] * u + pt[1] * nrm))


def stroke(ctrl, w0, w1, m=40):
    c = bez(P(ctrl[0], float), P(ctrl[1], float), P(ctrl[2], float), P(ctrl[3], float), m)
    tang = np.gradient(c, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
    nn = np.stack([-tang[:, 1], tang[:, 0]], 1)
    ww = np.linspace(w0, w1, m)[:, None]
    left = c + nn * ww
    right = c - nn * ww
    return [L2I(p) for p in np.vstack([left, right[::-1]])]


head = Image.new("L", (W, H), 0)
dr = ImageDraw.Draw(head)
upper = [(-70, -60), (10, -76), (100, -60), (180, -36), (246, -28), (258, -12), (170, -4), (60, -6), (-70, 10)]
lower = [(-60, 22), (60, 8), (170, 6), (236, 22), (214, 34), (120, 42), (30, 54), (-60, 56)]
dr.polygon([L2I(p) for p in upper], fill=255)
dr.polygon([L2I(p) for p in lower], fill=235)
dr.polygon(stroke([(-10, -66), (-70, -120), (-150, -150), (-235, -118)], 16, 1), fill=255)
dr.polygon(stroke([(-20, -58), (-90, -88), (-170, -88), (-255, -56)], 12, 1), fill=230)
dr.polygon(stroke([(200, -24), (262, -70), (205, -132), (100, -162)], 4, 0.6), fill=210)
dr.polygon(stroke([(190, 24), (262, 82), (212, 142), (120, 164)], 4, 0.6), fill=210)
for tx in (150, 190, 225):  # teeth
    dr.polygon([L2I((tx, -4)), L2I((tx + 12, -4)), L2I((tx + 6, 14))], fill=255)
head_m = np.asarray(head.filter(ImageFilter.GaussianBlur(1.4)), np.float32) / 255
head_m = warp(head_m, noise(10, 4), noise(10, 4))
inner = np.clip(gaussian_filter(head_m, 11) * 1.1 - 0.15, 0, 1)
orange = np.array((1.0, 0.36, 0.08), np.float32)
white = np.array((1.0, 0.82, 0.38), np.float32)
head_rgb = head_m[..., None] * (orange * (1 - inner[..., None]) + white * inner[..., None])
eye = glow(*L2I((70, -34)), 9, (1.0, 1.0, 0.95), 1.0)
eye_halo = glow(*L2I((70, -34)), 34, (0.3, 0.8, 1.0), 0.7)

# ---------- compose ribbon + head ----------
L = np.clip(flame + wisps + head_rgb, 0, 1)
img = screen(img, gaussian_filter(L, (60, 60, 0)) * 0.35)
img = screen(img, gaussian_filter(L, (22, 22, 0)) * 0.30)
rainbow_tint = hsv2rgb(xx / W * 1.1 + 0.02, 0.8, 1.0) * gaussian_filter(np.maximum(body_a, head_m), 38)[..., None] * 0.40
img = screen(img, rainbow_tint)
img = screen(img, L)
img = screen(img, eye_halo)
img = screen(img, eye)

# ---------- rainbow embers ----------
em = Image.new("RGB", (W, H))
de = ImageDraw.Draw(em)
for _ in range(280):
    x = rng.uniform(0, W)
    y = H * (1 - rng.uniform() ** 2)
    r = rng.uniform(1.2, 4.0)
    rgb = colorsys.hsv_to_rgb(rng.uniform(), 0.55, 1.0)
    de.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(255 * c_) for c_ in rgb))
em = np.asarray(em, np.float32) / 255
img = screen(img, np.clip(gaussian_filter(em, (5, 5, 0)) * 2.2 + gaussian_filter(em, (1.2, 1.2, 0)), 0, 1) * 0.8)

# ---------- finish ----------
vx = (xx - W / 2) / (W / 2)
vy = (yy - H / 2) / (H / 2)
img *= 0.9 * (1 - 0.40 * np.clip(vx ** 2 * 0.8 + vy ** 2 * 0.9, 0, 1.4))[..., None]
img += rng.normal(0, 0.006, img.shape).astype(np.float32)
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
out.save(OUT, quality=88, optimize=True)
print("saved", OUT, os.path.getsize(OUT) // 1024, "KB")
