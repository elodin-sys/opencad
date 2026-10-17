"""Figures for the sprite-aleph-v2 design proposal, iteration 2. Run from the repo root:
.venv/bin/python docs/proposals/sprite-aleph-v2/figures.py

Sprite-drone assembly frame (mm): z along the fuselage from the carbon plate top face toward the nose, y toward the top
cover, x lateral (starboard positive). Numbers match proposal.md; change them together.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle
from shapely.geometry import Polygon as ShapelyPolygon

OUT = Path(__file__).parent

# ---- measured Sprite outlines (assembly frame), as in v1 ----
NOSE_BOTTOM = [
    (170, -37.5),
    (180.5, -37.25),
    (190.5, -36.55),
    (200.5, -35.39),
    (210.5, -33.77),
    (220.5, -31.67),
    (230.5, -29.08),
    (240.5, -25.99),
    (249.3, -22.9),
]
COVER_TOP = [
    (170, 37.5),
    (178.5, 37.25),
    (188.5, 36.29),
    (198.5, 34.61),
    (208.5, 32.16),
    (218.5, 28.91),
    (228.5, 24.81),
    (238.5, 19.76),
    (248.5, 13.63),
    (253.5, 10.12),
    (256.7, 7.8),
]
NOSE_HALF_WIDTH = [
    (200.5, 25.0),
    (205.5, 24.86),
    (210.5, 24.48),
    (215.5, 23.87),
    (220.5, 23.01),
    (225.5, 21.91),
    (230.5, 20.55),
    (235.5, 18.93),
    (240.5, 17.02),
    (245.5, 14.77),
    (249.3, 13.1),
]
CONE_Y = [
    (-6, 36.0),
    (-26.5, 36.0),
    (-31.5, 35.3),
    (-41.5, 33.6),
    (-51.5, 31.4),
    (-61.5, 28.7),
    (-71.5, 25.5),
    (-81.5, 21.7),
    (-91.5, 17.3),
]
CONE_X = [
    (-6, 28.6),
    (-26.5, 28.6),
    (-31.5, 27.9),
    (-41.5, 25.6),
    (-51.5, 22.3),
    (-61.5, 17.8),
    (-71.5, 12.9),
    (-81.5, 9.1),
    (-91.5, 4.8),
]
TIP_Z, COVER_TIP_Z = 249.3, 256.7

# ---- body section: v1's 60 x 75 faceted outline, now prismatic from z 0 (no flare) ----
HW, HH = 30.0, 37.5
SIDE_Y, CROWN_X = 23.4, 17.6
WALL = 2.0
INNER = {"hw": 28.0, "hh": 35.5, "side_y": 22.6, "crown_x": 16.4}
ROOF_END = 22.0  # roof lip z 0..22; the cover starts here
WALL_END = 202.0
SPLIT_Y = 22.0
NOSE_SPLIT = (202.0, 15.0, 216.0)  # past the walls: y 15 (skirt band bottom) at 202, smoothstep to y 0 at 216
SKIRT_Y = (15.0, 22.0)  # cover skirt band inside the walls, x 26.6..27.8
SKIRT_X = (26.6, 27.8)
GROOVE_Y = (16.0, 20.0)  # in the shell's inner wall, x 28..29.2
GROOVE_DEPTH = 1.2
TONGUE_Y = (16.05, 19.95)
VTX_Z = (203.0, 212.0)
SERVO_Z = (214.8, 229.1)
HINGE = (244.0, -2.28)

# ---- nose laws: cubic Hermite in z, slope 0 at the start, the Sprite's slope at the tip ----
W_LAW = (202.0, 30.0, 249.3, 13.1, -0.40)  # half width
C_LAW = (185.0, 37.5, 256.7, 7.8, -0.72)  # crown (cover)
K_LAW = (125.0, -37.5, 249.3, -22.9, 0.35)  # keel (shell)
MORPH = (202.0, 225.0)  # faceted section -> half-ellipse pair
STATIONS = (202.0, 210.0, 218.0, 225.0, 235.0, 245.0, 249.3)

# ---- sled ----
BASE_Z = (0.0, 3.0)
SLED_WALL_X = (21.6, 25.6)
SLED_WALL_Y = (-27.0, 25.0)
SLED_WALL_Z = (11.0, 117.0)
FLANGE = {"y": (-31.0, -28.5), "x": (8.0, 22.0), "z": (11.0, 117.0)}  # starts above the shell's rib ring
TRAY = {"floor_y": (-25.0, -22.5), "x": (-25.5, 25.5), "z": (117.0, 202.0)}
LIPS = {"x": (24.0, 25.5), "y": (-22.5, -12.5)}
BULKHEAD = {"z": (117.0, 119.0), "y": (-31.0, 19.5)}
STRAPS = (145.0, 178.0)
XT60 = {"x": (-22.0, -6.0), "z": (109.0, 117.0), "y": (-12.0, 12.0)}
SCREWS = [(14.0, 0.0), (112.0, -18.0)]  # (z, y) on both flanks: M3 x 8 countersunk into inserts in sled pads
SLED_PAD_X = (21.6, 26.0)
SHELL_PAD_X = (26.4, 28.0)
PAD_R = 4.5
CLAMP_XY = 15.0
RIB_X = (26.5, 28.0)

# ---- battery bay and power bay ----
BAT_ENV = {"z": (120.0, 201.0), "y": (-22.5, 19.5), "x": (-24.0, 24.0)}
BATTERY = {"z": (121.5, 199.5), "y": (-22.5, 16.5), "x": (-21.0, 21.0)}  # Tattu R-Line V5 1400 flat
REGULATOR = {"x": (-15.9, 15.9), "y": (19.5, 30.5), "z": (139.0, 182.2)}  # optional, velcro on the pack
POWER_BAY_Z = (3.0, 19.0)
MOLEX_PLUG = {"x": (8.9, 16.0), "y": (9.4, 18.1), "z": (3.5, 19.0)}

# ---- Aleph on edge: base against the sled wall through 4 mm standoffs, board plane x = 17.6 ----
# asm (x, y, z) = (17.6 - sz, 24.75 - sy, 107 - sx) from the aleph-stack frame (power end aft, service edge up)
XP = 17.6
STANDOFF = 4.0
BOARD_Y = (-27.75, 24.75)
BOARD_Z = (19.0, 107.0)
HOLES_Y = (-24.75, 21.75)
HOLES_Z = (22.0, 104.0)
LAYERS_X = {
    k: (XP - b, XP - a)
    for k, (a, b) in {
        "parts": (-1.97, 0.0),
        "base": (0.0, 1.56),
        "standoff": (1.56, 11.56),
        "carrier": (11.56, 13.13),
        "sodimm": (13.13, 23.99),
        "module": (19.69, 20.89),
        "lid": (20.89, 23.52),
        "heatsink": (23.52, 41.52),
    }.items()
}
SODIMM = {"y": (-26.25, -21.25), "z": (24.9, 101.1)}
MODULE = {"y": (-21.25, 23.75), "z": (28.2, 97.8)}
HEATSINK = {"y": (-15.4, 22.6), "z": (34.0, 92.0)}
LID = {"y": (-6.5, 13.7), "z": (51.9, 74.1)}
HS_CENTER = {"y": 3.6, "z": 63.0}
FAN_D = 38.0
GRILLE = {"z": (33.0, 93.0), "y": (-16.0, 14.0)}
LOUVERS = [{"z": (21.0, 32.0), "y": (-14.0, 14.0)}, {"z": (94.0, 105.0), "y": (-14.0, 14.0)}]
ETH = {"x": (XP - 8.89, XP - 1.56), "y": (13.9, 27.25), "z": (78.6, 89.4)}
USBC_BASE = {"x": (XP - 6.5, XP - 1.56), "y": (17.0, 24.75), "z": (31.8, 40.8)}
JSTGH = {"x": (XP - 7.54, XP - 1.56), "y": (19.5, 24.4), "z": (43.0, 75.3)}

# ---- tail: v1 unchanged ----
ESC_PCB_Z = (-20.6, -19.0)
ESC_HOUSING_Z = (-25.5, -18.6)
ESC_LONG = 31.58
ESC_X = (-22.75, 19.5)
MR30_Y = (31.58, 38.31)
PLUG_Y = (38.31, 46.5)
MR30_X = [(4.05, 19.58), (-19.58, -4.05)]
SLOT = {"z": (-27.0, -17.0), "x": (-22.5, 22.5)}
SPACER = 12.0
MOTOR_XY = 80.0
PROP_R = 63.5

INK, OLD, BODY = "#222222", "#9a9a9a", "#f3efe6"
ESC_C, BAT_C, ALEPH_C, SLED_C, VENT_C, NOSE_C, HS_C, COVER_C, WIRE_C = (
    "#c8553d",
    "#e0a458",
    "#4c86a8",
    "#7a6c5d",
    "#2a9d8f",
    "#b7b7a4",
    "#2f5d7a",
    "#8fa8c8",
    "#f2c14e",
)


def faceted(hw, hh, side_y, crown_x):
    q = [(hw, 0), (hw, side_y), (crown_x, hh), (0, hh)]
    pts = (
        q
        + [(-x, y) for x, y in reversed(q[:-1])]
        + [(-x, -y) for x, y in q[1:]]
        + [(x, -y) for x, y in reversed(q[1:-1])]
    )
    return np.array(pts)


def stadium(cx, cy, w, h, n=48):
    r = w / 2
    top = [(cx + r * np.cos(np.radians(a)), cy + h / 2 - r + r * np.sin(np.radians(a))) for a in np.linspace(0, 180, n)]
    bot = [
        (cx + r * np.cos(np.radians(a)), cy - h / 2 + r + r * np.sin(np.radians(a))) for a in np.linspace(180, 360, n)
    ]
    return np.array(top + bot)


def interp(profile, z):
    zs, vs = zip(*sorted(profile))
    return float(np.interp(z, zs, vs))


def herm(z, z0, p0, z1, p1, m1):
    t = float(np.clip((z - z0) / (z1 - z0), 0.0, 1.0))
    return (2 * t**3 - 3 * t**2 + 1) * p0 + (3 * t**2 - 2 * t**3) * p1 + (t**3 - t**2) * (z1 - z0) * m1


def law(spec, z0, z1, n=120):
    return [(z, herm(z, *spec)) for z in np.linspace(z0, z1, n)]


def smooth(u):
    u = float(np.clip(u, 0.0, 1.0))
    return u * u * (3 - 2 * u)


def split_y(z):
    z0, y0, z1 = NOSE_SPLIT
    return y0 * (1 - smooth((z - z0) / (z1 - z0)))


def nose_section(z, n=240):
    """Outer section at z: the faceted outline scaled to the laws, blended radially into a half-ellipse pair."""
    w, c, k = herm(z, *W_LAW), herm(z, *C_LAW), herm(z, *K_LAW)
    ys, cx = SIDE_Y * w / HW, CROWN_X * w / HW
    poly = np.array([(w, ys), (cx, c), (-cx, c), (-w, ys), (-w, -ys), (-cx, k), (cx, k), (w, -ys)])
    edges = np.roll(poly, -1, axis=0) - poly
    normals = np.c_[edges[:, 1], -edges[:, 0]]
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    offsets = np.einsum("ij,ij->i", normals, poly)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    u = np.c_[np.cos(th), np.sin(th)]
    dots = u @ normals.T
    r_facet = np.min(np.where(dots > 1e-9, offsets / np.where(dots > 1e-9, dots, 1.0), np.inf), axis=1)
    semi = np.where(u[:, 1] >= 0, c, -k)
    r_ellipse = 1 / np.sqrt((u[:, 0] / w) ** 2 + (u[:, 1] / semi) ** 2)
    b = smooth((z - MORPH[0]) / (MORPH[1] - MORPH[0]))
    return u * ((1 - b) * r_facet + b * r_ellipse)[:, None]


def inner_of(section):
    return np.array(ShapelyPolygon(section).buffer(-WALL, join_style=2).exterior.coords)


def inner_x_at(y):
    y = abs(y)
    if y <= INNER["side_y"]:
        return INNER["hw"]
    return INNER["hw"] - (y - INNER["side_y"]) / (INNER["hh"] - INNER["side_y"]) * (INNER["hw"] - INNER["crown_x"])


def rect(ax, x0, x1, y0, y1, **kw):
    ax.add_patch(Rectangle((min(x0, x1), min(y0, y1)), abs(x1 - x0), abs(y1 - y0), **kw))


def side_elevation():
    fig, ax = plt.subplots(figsize=(17, 8))
    ax.set_aspect("equal")
    # plate, tail cone, rear mount, ESC (v1)
    rect(ax, -6, 0, -37.5, 37.5, fc="#3b3b3b", ec="none")
    rect(ax, -6, 0, -13.5, 13.5, fc="white", ec="none")
    cone = [(z, y) for z, y in CONE_Y] + [(z, -y) for z, y in reversed(CONE_Y)]
    ax.add_patch(Polygon(cone, closed=True, fc="none", ec=INK, lw=1.2))
    rect(ax, -7.2, -6, -36.6, 36.6, fc=NOSE_C, ec=INK, lw=0.6)
    rect(ax, -13.3, -6, 25.5, 36.4, fc=NOSE_C, ec=INK, lw=0.5)
    rect(ax, -13.3, -6, -36.3, -29.6, fc=NOSE_C, ec=INK, lw=0.5)
    for yc in (CLAMP_XY, -CLAMP_XY):
        rect(ax, -7.2 - SPACER, -7.2, yc - 2.5, yc + 2.5, fc="#dddddd", ec=INK, lw=0.5)
        ax.plot([BASE_Z[1], ESC_PCB_Z[0]], [yc, yc], color=INK, lw=1.1)
    rect(ax, ESC_PCB_Z[0], ESC_PCB_Z[0] + 1.6, -ESC_LONG, ESC_LONG, fc=ESC_C, ec=INK, lw=0.6)
    for s in (1, -1):
        rect(ax, ESC_HOUSING_Z[0], ESC_HOUSING_Z[0] + 6.9, s * MR30_Y[0], s * MR30_Y[1], fc=ESC_C, ec=INK, lw=0.6)
        rect(
            ax,
            ESC_HOUSING_Z[0] + 0.5,
            ESC_HOUSING_Z[0] + 6.4,
            s * PLUG_Y[0],
            s * PLUG_Y[1],
            fc="none",
            ec=ESC_C,
            lw=0.9,
            ls="--",
        )
        ax.plot([SLOT["z"][0], SLOT["z"][1]], [s * 36.5, s * 36.5], color="white", lw=2.5)
        ax.plot([SLOT["z"][0], SLOT["z"][1]], [s * 36.5, s * 36.5], color=VENT_C, lw=1.0, ls="--")
    ax.text(
        -52,
        -46,
        "tail: v1 as built (cone slots, ESC on\n12 mm standoffs, ring cut at z -13)",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    # shell screws: countersunk M3 through both flanks into inserts in sled pads
    for zc, yc in SCREWS:
        rect(ax, zc - PAD_R, zc + PAD_R, yc - PAD_R, yc + PAD_R, fc=SLED_C, ec=INK, lw=0.6)
        ax.add_patch(Circle((zc, yc), 3.0, fc="white", ec=INK, lw=0.9, zorder=6))
        ax.plot([zc - 2.1, zc + 2.1], [yc - 2.1, yc + 2.1], color=INK, lw=0.8, zorder=7)
        ax.plot([zc - 2.1, zc + 2.1], [yc + 2.1, yc - 2.1], color=INK, lw=0.8, zorder=7)
    ax.annotate(
        "shell screws: four M3 x 8 countersunk through the flanks (both sides, z 14 and 112)\n"
        "into heat-set inserts in sled pads; the tail and frame are untouched",
        xy=(14, -3),
        xytext=(-40, -66),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    ax.annotate("", xy=(112, -21), xytext=(-14, -62), arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6})
    # sled: base, wall (behind the board), flange, tray, bulkhead
    rect(ax, BASE_Z[0], BASE_Z[1], -35.2, 35.2, fc=SLED_C, ec=INK, lw=0.6)
    rect(
        ax,
        SLED_WALL_Z[0],
        SLED_WALL_Z[1],
        SLED_WALL_Y[0],
        SLED_WALL_Y[1],
        fc=SLED_C,
        alpha=0.18,
        ec=SLED_C,
        lw=0.8,
        ls="--",
    )
    rect(ax, FLANGE["z"][0], FLANGE["z"][1], FLANGE["y"][0], FLANGE["y"][1], fc=SLED_C, ec=INK, lw=0.6)
    rect(ax, TRAY["z"][0], TRAY["z"][1], TRAY["floor_y"][0], TRAY["floor_y"][1], fc=SLED_C, ec=INK, lw=0.6)
    rect(ax, BULKHEAD["z"][0], BULKHEAD["z"][1], BULKHEAD["y"][0], BULKHEAD["y"][1], fc=SLED_C, ec=INK, lw=0.6)
    for zs in STRAPS:
        ax.plot([zs, zs], [-23.5, 17.5], color=INK, lw=1.2)
    rect(ax, XT60["z"][0], XT60["z"][1], XT60["y"][0], XT60["y"][1], fc=WIRE_C, ec=INK, lw=0.6)
    ax.text(
        60,
        -52,
        "sled (one print, about 60 g): base plate on the frame's four clamp axes, 4 mm Aleph wall\n"
        "(dashed, behind the board) with flange, battery tray with lips, strap slots, bulkhead and XT60 pocket",
        fontsize=7.5,
        ha="center",
        va="top",
        color=SLED_C,
    )
    # power bay: leads up the plate hole, Y, 6S plug; keel channel forward to the alcove
    ax.plot([-8, -8, 8, 8, 112, 112], [-16, -33, -33, -33, -33, -10], color=WIRE_C, lw=1.8)
    ax.plot([-8, 12, 12], [-10, -10, 9], color=WIRE_C, lw=1.2)
    rect(
        ax, MOLEX_PLUG["z"][0], MOLEX_PLUG["z"][1], MOLEX_PLUG["y"][0], MOLEX_PLUG["y"][1], fc="#dddddd", ec=INK, lw=0.6
    )
    ax.annotate(
        "power bay z 3..19: ESC leads up the D27 hole, Y to the\nAleph's 6S plug; pack lead through the keel channel",
        xy=(11, 13),
        xytext=(24, 60),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    # shell outline: no flare; roof lip; split; nose laws (the Sprite's nose dashed for comparison)
    ax.plot(*zip(*NOSE_BOTTOM), color=OLD, lw=0.9, ls="--")
    ax.plot(*zip(*COVER_TOP), color=OLD, lw=0.9, ls="--")
    ax.plot(*zip(*law(K_LAW, 0, TIP_Z)), color=INK, lw=1.4)
    ax.plot([0, 0], [-37.5, 37.5], color=INK, lw=1.4)
    ax.plot([0, ROOF_END], [37.5, 37.5], color=INK, lw=1.4)
    ax.plot([ROOF_END, ROOF_END], [37.5, SPLIT_Y], color=INK, lw=1.0)
    split = [(z, split_y(z)) for z in np.linspace(WALL_END, TIP_Z, 60)]
    ax.plot([ROOF_END, WALL_END, WALL_END], [SPLIT_Y, SPLIT_Y, NOSE_SPLIT[1]], color=INK, lw=1.0)
    ax.plot(*zip(*split), color=INK, lw=1.0)
    ax.plot([TIP_Z, TIP_Z], [0, -22.9], color=INK, lw=1.4)
    cover = (
        law(C_LAW, ROOF_END, COVER_TIP_Z)
        + [(COVER_TIP_Z, 0)]
        + split[::-1]
        + [(WALL_END, SPLIT_Y), (ROOF_END, SPLIT_Y), (ROOF_END, 37.5)]
    )
    ax.add_patch(Polygon(cover, closed=True, fc="none", ec=INK, lw=1.2))
    for z0, lab, y in (
        (K_LAW[0], "keel\nrises", -44),
        (C_LAW[0], "crown\ndescends", 44),
        (W_LAW[0], "width\ntapers", 44),
    ):
        ax.plot([z0], [herm(z0, *(K_LAW if y < 0 else C_LAW))], "o", ms=3.5, color=ESC_C, zorder=8)
        ax.text(z0, y, lab, fontsize=6.5, ha="center", va="center", color=ESC_C)
    rect(ax, 0, ROOF_END, SPLIT_Y, 37.5, fc="none", ec=INK, hatch="////", lw=0)
    rect(ax, ROOF_END, WALL_END, SKIRT_Y[0], SKIRT_Y[1], fc=COVER_C, alpha=0.35, ec="none")
    for gy in GROOVE_Y:
        ax.plot([ROOF_END, WALL_END], [gy, gy], color=INK, lw=0.6)
    ax.text(11, 41, "roof lip\nz 0..22", fontsize=7.5, ha="center", va="bottom")
    ax.text(
        110,
        41.5,
        "sliding cover, 60 wide, z 22..256.7: skirt y 15..22 (shaded), tongue in the groove y 16..20;\n"
        "the tongue enters at z 202 and slides 180 mm to the roof lip",
        fontsize=7.5,
        ha="center",
        va="bottom",
    )
    ax.annotate("", xy=(150, 27), xytext=(200, 27), arrowprops={"arrowstyle": "->", "color": COVER_C, "lw": 1.6})
    ax.annotate("", xy=(0, -44), xytext=(60, -44), arrowprops={"arrowstyle": "->", "color": SLED_C, "lw": 1.6})
    ax.text(30, -45.5, "shell slides down over the loaded sled", fontsize=7, ha="center", va="top", color=SLED_C)
    # battery and regulator
    rect(ax, BATTERY["z"][0], BATTERY["z"][1], BATTERY["y"][0], BATTERY["y"][1], fc=BAT_C, ec=INK, lw=0.8)
    rect(ax, BAT_ENV["z"][0], BAT_ENV["z"][1], BAT_ENV["y"][0], BAT_ENV["y"][1], fc="none", ec=INK, lw=0.8, ls="--")
    rect(
        ax,
        REGULATOR["z"][0],
        REGULATOR["z"][1],
        REGULATOR["y"][0],
        REGULATOR["y"][1],
        fc="none",
        ec=INK,
        lw=0.8,
        ls="--",
    )
    ax.text(
        160.5,
        -3,
        "6S pack envelope 81 x 48 x 42 flat (dashed),\nV5 1400 shown; top 2.5 under the split",
        fontsize=8,
        ha="center",
        va="center",
    )
    ax.text(160.5, 25, "optional regulator on the pack", fontsize=6.5, ha="center", va="center")
    # Aleph
    rect(ax, BOARD_Z[0], BOARD_Z[1], BOARD_Y[0], BOARD_Y[1], fc=ALEPH_C, alpha=0.35, ec=INK, lw=0.8)
    rect(ax, MODULE["z"][0], MODULE["z"][1], MODULE["y"][0], MODULE["y"][1], fc="none", ec=INK, lw=0.6, ls=":")
    rect(
        ax,
        HEATSINK["z"][0],
        HEATSINK["z"][1],
        HEATSINK["y"][0],
        HEATSINK["y"][1],
        fc=HS_C,
        alpha=0.25,
        ec=HS_C,
        lw=1.0,
        ls="--",
    )
    ax.add_patch(Circle((HS_CENTER["z"], HS_CENTER["y"]), FAN_D / 2, fc="none", ec=HS_C, lw=0.8, ls="--"))
    for zc in HOLES_Z:
        for yc in HOLES_Y:
            ax.add_patch(Circle((zc, yc), 2.2, fc="#dddddd", ec=INK, lw=0.8))
    for c, lab in ((ETH, "ETH"), (USBC_BASE, "USB-C"), (JSTGH, "JST-GH")):
        rect(ax, c["z"][0], c["z"][1], c["y"][0], c["y"][1], fc="#dddddd", ec=INK, lw=0.5)
        ax.text((c["z"][0] + c["z"][1]) / 2, c["y"][1] + 1, lab, fontsize=6, ha="center", va="bottom")
    ax.text(
        63,
        52,
        "Aleph on edge over the frame: base against the sled wall through four 4 mm standoffs,\n"
        "service edge up, power end aft, heatsink behind a grille in the port wall",
        fontsize=8,
        ha="center",
        va="bottom",
    )
    rect(ax, GRILLE["z"][0], GRILLE["z"][1], GRILLE["y"][0], GRILLE["y"][1], fc="none", ec=VENT_C, lw=1.2, ls="--")
    for zg in np.arange(GRILLE["z"][0] + 3, GRILLE["z"][1], 4.0):
        ax.plot([zg, zg], [GRILLE["y"][0] + 1, GRILLE["y"][1] - 1], color=VENT_C, lw=0.5, alpha=0.6)
    ax.annotate(
        "grille 60 x 30 (y -16..14): stops one wall\nunder the skirt band; 83 % of the fan face",
        xy=(93, 0),
        xytext=(118, -66),
        fontsize=7.5,
        ha="center",
        color=VENT_C,
        arrowprops={"arrowstyle": "-", "color": VENT_C, "lw": 0.6},
    )
    for lv in LOUVERS:
        rect(ax, lv["z"][0], lv["z"][1], lv["y"][0], lv["y"][1], fc="none", ec=VENT_C, lw=1.0, ls=":")
    # nose
    rect(ax, VTX_Z[0], VTX_Z[1], -22, 29.5, fc=NOSE_C, ec=INK, lw=0.6)
    servo = law(K_LAW, SERVO_Z[0], SERVO_Z[1], 20)
    servo = [(z, y + WALL) for z, y in servo] + [(SERVO_Z[1], 13.8), (SERVO_Z[0], 13.8)]
    ax.add_patch(Polygon(servo, closed=True, fc=NOSE_C, ec=INK, lw=0.6))
    rect(ax, 234, 253, -12, 7, fc=NOSE_C, ec=INK, lw=0.6)
    ax.add_patch(Circle(HINGE, 2.0, fc="white", ec=INK, lw=0.6))
    ax.text(207.5, 50, "VTX mount\nz 203..212", fontsize=7, ha="center", va="bottom")
    ax.text(222, 17, "servo mount\n(glue face\nre-lofted)", fontsize=6.5, ha="center")
    ax.text(250, 20, "camera + tilt", fontsize=7, ha="center")
    ax.text(-3, -42, "carbon plate\n(v1)", fontsize=7, ha="center", va="top")
    # axes and stations
    ax.annotate("", xy=(295, -96), xytext=(-100, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(295, -103, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-100, -66), xytext=(-100, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-97, -68, "y (cover)", fontsize=8)
    for z, lab in [
        (-20, "-20"),
        (0, "0"),
        (ROOF_END, "22"),
        (107, "107"),
        (BULKHEAD["z"][0], "117"),
        (K_LAW[0], "125"),
        (C_LAW[0], "185"),
        (WALL_END, "202"),
        (MORPH[1], "225"),
        (TIP_Z, "249.3"),
    ]:
        ax.plot([z, z], [-93, -89], color=INK, lw=0.6)
        ax.text(z, -99, lab, fontsize=7, ha="center", va="top")
    for z0, z1, lab in [
        (-30, -6, "ESC"),
        (POWER_BAY_Z[0], POWER_BAY_Z[1], ""),
        (BOARD_Z[0], BOARD_Z[1], "Aleph bay"),
        (BAT_ENV["z"][0], BAT_ENV["z"][1], "battery bay"),
        (WALL_END, COVER_TIP_Z, "nose laws"),
    ]:
        yy = -78
        ax.plot([z0, z1], [yy, yy], color=INK, lw=1.0)
        ax.plot([z0, z0], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.plot([z1, z1], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.text((z0 + z1) / 2, yy - 3.5, lab, fontsize=7.5, ha="center", va="top")
    ax.text(
        -100,
        -110,
        "plate top face z = 0. Body 60 x 75 faceted from z 0, shell 249.3 tall (Bambu X1C). Hover: nose up.",
        fontsize=7.5,
        ha="left",
    )
    ax.set_xlim(-105, 300)
    ax.set_ylim(-116, 72)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph-v2, iteration 2: side elevation, port wall removed; Sprite nose dashed (mm, assembly frame)",
        fontsize=11,
        loc="left",
    )
    fig.tight_layout()
    fig.savefig(OUT / "side-elevation.png", dpi=170)
    plt.close(fig)


def draw_section(ax, with_cover=True):
    ax.add_patch(Polygon(faceted(HW, HH, SIDE_Y, CROWN_X), closed=True, fc=BODY, ec=INK, lw=1.4))
    ax.add_patch(Polygon(faceted(**INNER), closed=True, fc="white", ec=INK, lw=0.8))
    ax.plot([-HW, HW], [SPLIT_Y, SPLIT_Y], color=INK, lw=0.6, ls=":")
    for s in (1, -1):
        # groove in the wall, skirt and tongue of the cover
        rect(
            ax, s * INNER["hw"], s * (INNER["hw"] + GROOVE_DEPTH), GROOVE_Y[0], GROOVE_Y[1], fc="white", ec=INK, lw=0.5
        )
        if with_cover:
            rect(ax, s * SKIRT_X[0], s * SKIRT_X[1], SKIRT_Y[0], SKIRT_Y[1], fc=COVER_C, ec=INK, lw=0.5)
            rect(
                ax,
                s * SKIRT_X[1],
                s * (INNER["hw"] + GROOVE_DEPTH - 0.1),
                TONGUE_Y[0],
                TONGUE_Y[1],
                fc=COVER_C,
                ec=INK,
                lw=0.5,
            )
    if with_cover:
        upper = [p for p in faceted(HW, HH, SIDE_Y, CROWN_X) if p[1] >= SPLIT_Y - 1e-6]
        upper = np.array([(HW, SPLIT_Y)] + [tuple(p) for p in upper] + [(-HW, SPLIT_Y)])
        ax.add_patch(Polygon(upper, closed=True, fc=COVER_C, alpha=0.25, ec="none"))


def sections():
    fig, axes = plt.subplots(1, 4, figsize=(22, 8), gridspec_kw={"width_ratios": [1.15, 1.15, 1.25, 1.3]})
    # (a) Aleph bay at z = 63
    ax = axes[0]
    ax.set_aspect("equal")
    draw_section(ax)
    rect(ax, -HW - 0.4, -INNER["hw"] + 0.3, GRILLE["y"][0], GRILLE["y"][1], fc="white", ec="none")
    for yy in np.arange(GRILLE["y"][0] + 2, GRILLE["y"][1], 4.0):
        ax.plot([-HW - 0.2, -INNER["hw"] + 0.2], [yy, yy], color=VENT_C, lw=1.4)
    # sled wall (outer face follows the facet at 0.4) and flange
    wall = [(SLED_WALL_X[0], SLED_WALL_Y[0]), (SLED_WALL_X[0], SLED_WALL_Y[1])]
    for y in np.linspace(SLED_WALL_Y[1], SLED_WALL_Y[0], 40):
        wall.append((min(SLED_WALL_X[1], inner_x_at(y) - 0.4), y))
    ax.add_patch(Polygon(wall, closed=True, fc=SLED_C, ec=INK, lw=0.8))
    flange = [
        (FLANGE["x"][0], FLANGE["y"][0]),
        (FLANGE["x"][0], FLANGE["y"][1]),
        (inner_x_at(FLANGE["y"][1]) - 0.4, FLANGE["y"][1]),
        (inner_x_at(FLANGE["y"][0]) - 0.4, FLANGE["y"][0]),
    ]
    ax.add_patch(Polygon(flange, closed=True, fc=SLED_C, ec=INK, lw=0.8))
    for yc in HOLES_Y:
        rect(ax, XP, SLED_WALL_X[0], yc - 2.5, yc + 2.5, fc="#dddddd", ec=INK, lw=0.5)
        ax.plot([SLED_WALL_X[0] - 0.2, SLED_WALL_X[1] - 0.6], [yc, yc], color="white", lw=1.6)
    # stack layers
    rect(
        ax, LAYERS_X["parts"][0], LAYERS_X["parts"][1], BOARD_Y[0] + 2, BOARD_Y[1] - 2, fc=ALEPH_C, alpha=0.3, ec="none"
    )
    rect(ax, LAYERS_X["base"][0], LAYERS_X["base"][1], BOARD_Y[0], BOARD_Y[1], fc=ALEPH_C, ec=INK, lw=0.6)
    for yc in HOLES_Y:
        rect(ax, LAYERS_X["standoff"][0], LAYERS_X["standoff"][1], yc - 2.5, yc + 2.5, fc="#dddddd", ec=INK, lw=0.5)
    rect(ax, LAYERS_X["carrier"][0], LAYERS_X["carrier"][1], BOARD_Y[0], BOARD_Y[1], fc=ALEPH_C, ec=INK, lw=0.6)
    rect(ax, LAYERS_X["sodimm"][0], LAYERS_X["sodimm"][1], SODIMM["y"][0], SODIMM["y"][1], fc="#bbbbbb", ec=INK, lw=0.5)
    rect(ax, LAYERS_X["module"][0], LAYERS_X["module"][1], MODULE["y"][0], MODULE["y"][1], fc=ALEPH_C, ec=INK, lw=0.6)
    rect(ax, LAYERS_X["lid"][0], LAYERS_X["lid"][1], LID["y"][0], LID["y"][1], fc="#555555", ec=INK, lw=0.5)
    rect(
        ax,
        LAYERS_X["heatsink"][0],
        LAYERS_X["heatsink"][1],
        HEATSINK["y"][0],
        HEATSINK["y"][1],
        fc=HS_C,
        alpha=0.6,
        ec=INK,
        lw=0.8,
    )
    for yy in np.arange(-13, 21, 3.3):
        ax.plot([LAYERS_X["heatsink"][1] - 9.5, LAYERS_X["heatsink"][1] - 0.5], [yy, yy], color="white", lw=0.6)
    rect(ax, ETH["x"][0], ETH["x"][1], ETH["y"][0], ETH["y"][1], fc="#dddddd", ec=INK, lw=0.5)
    for dy in (-11, 0, 11):
        ax.annotate(
            "",
            xy=(LAYERS_X["heatsink"][0] - 0.5, HS_CENTER["y"] + dy),
            xytext=(-HW - 9, HS_CENTER["y"] + dy),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    ax.plot([-15, 15], [-33, -33], color=WIRE_C, lw=3, solid_capstyle="round")
    ax.text(-8, -30, "keel channel", fontsize=6.5, ha="center", color="#8a6d1c")
    ax.text(
        -HW - 10, HS_CENTER["y"] + 22, "air through the\ngrille, top at y 14", fontsize=7, ha="center", color=VENT_C
    )
    ax.text(33, -2, "sled wall\n4 mm,\nstandoffs 4", fontsize=6.5, ha="center", va="center", color=SLED_C)
    ax.text(0, 18.5, "skirt band y 15..22: only the groove", fontsize=6.5, ha="center", va="center", color="#3c5a80")
    ax.text(-25.5, -26, "4.1\nplenum", fontsize=6.5, ha="center", va="center", color=HS_C)
    ax.text(0, 39.5, "60 x 75, cover on (blue)", fontsize=7.5, ha="center", color="#555555")
    ax.set_title("(a) Aleph bay, z = 63\nbase on the sled wall, fan to port", fontsize=9)
    # (b) battery bay at z = 160
    ax = axes[1]
    ax.set_aspect("equal")
    draw_section(ax)
    rect(ax, TRAY["x"][0], TRAY["x"][1], TRAY["floor_y"][0], TRAY["floor_y"][1], fc=SLED_C, ec=INK, lw=0.6)
    for s in (1, -1):
        rect(ax, s * LIPS["x"][0], s * LIPS["x"][1], LIPS["y"][0], LIPS["y"][1], fc=SLED_C, ec=INK, lw=0.5)
    rect(ax, BATTERY["x"][0], BATTERY["x"][1], BATTERY["y"][0], BATTERY["y"][1], fc=BAT_C, ec=INK, lw=0.8)
    ax.plot([-24, -24, 24, 24], [-22.5, 19.5, 19.5, -22.5], color=INK, lw=1.0, ls="--")
    rect(
        ax,
        REGULATOR["x"][0],
        REGULATOR["x"][1],
        REGULATOR["y"][0],
        REGULATOR["y"][1],
        fc="none",
        ec=INK,
        lw=0.8,
        ls="--",
    )
    ax.plot([-18, -6], [-31, -31], color=WIRE_C, lw=3, solid_capstyle="round")
    ax.text(
        0,
        -3,
        "V5 1400 flat, 42 x 39;\nenvelope 48 x 42 (dashed)\non the tray floor y -25..-22.5",
        fontsize=7.5,
        ha="center",
        va="center",
    )
    ax.text(0, 25, "regulator (optional)", fontsize=6.5, ha="center", va="center")
    ax.text(0, -30, "keel channel", fontsize=6.5, ha="center", color="#8a6d1c")
    ax.text(0, 39.5, "lips x 24..25.5: 1.0 to the skirt", fontsize=7.5, ha="center", color="#555555")
    ax.set_title("(b) battery bay, z = 160\ntray on the sled, cover on", fontsize=9)
    for ax in axes[:2]:
        ax.set_xlim(-47, 47)
        ax.set_ylim(-47, 47)
        ax.axis("off")
    # (c) power bay from above at z = 6: rib ring, lugs, sled base, screws, plug, leads
    ax = axes[2]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 60], [0, sy * 60], color="#dadada", lw=11, solid_capstyle="round", zorder=0)
    ax.add_patch(Polygon(stadium(0, 0, 50, 75), closed=True, fc="#c9c9c9", ec=OLD, lw=0.9, zorder=0))
    ax.add_patch(Polygon(faceted(HW, HH, SIDE_Y, CROWN_X), closed=True, fc=BODY, ec=INK, lw=1.4, zorder=1))
    ax.add_patch(Polygon(faceted(**INNER), closed=True, fc="white", ec=INK, lw=0.8, zorder=1))
    base = faceted(INNER["hw"] - 0.3, INNER["hh"] - 0.3, INNER["side_y"] - 0.3, INNER["crown_x"] - 0.3)
    ax.add_patch(Polygon(base, closed=True, fc=SLED_C, alpha=0.35, ec=SLED_C, lw=0.8, zorder=2))
    ring_in = faceted(RIB_X[0], INNER["hh"] - (INNER["hw"] - RIB_X[0]), INNER["side_y"], INNER["crown_x"] - 1.5)
    ax.add_patch(Polygon(ring_in, closed=True, fc="none", ec=INK, lw=0.8, zorder=3))
    ax.add_patch(Circle((0, 0), 13.5, fc="white", ec=INK, lw=0.6, ls=":", zorder=3))
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.add_patch(Circle((sx * CLAMP_XY, sy * CLAMP_XY), 3.0, fc="#dddddd", ec=INK, lw=0.6, zorder=4))
        ax.add_patch(Circle((sx * CLAMP_XY, sy * CLAMP_XY), 1.55, fc="white", ec=INK, lw=0.5, zorder=5))
    rect(ax, SLED_WALL_X[0], SLED_WALL_X[1], -15, 15, fc=SLED_C, ec=INK, lw=0.6, zorder=3)
    for s in (1, -1):
        rect(ax, s * SLED_PAD_X[0], s * SLED_PAD_X[1], -PAD_R, PAD_R, fc=SLED_C, ec=INK, lw=0.6, zorder=4)
        rect(ax, s * SHELL_PAD_X[0], s * SHELL_PAD_X[1], -PAD_R, PAD_R, fc=BODY, ec=INK, lw=0.6, zorder=4)
        rect(ax, s * (SLED_PAD_X[1] - 4.0), s * SLED_PAD_X[1], -2.0, 2.0, fc="#dddddd", ec=INK, lw=0.5, zorder=5)
        ax.plot([s * HW, s * (SLED_PAD_X[1] - 4.0)], [0, 0], color=INK, lw=1.4, zorder=6)
        ax.add_patch(
            Polygon([(s * HW, 3.0), (s * (HW - 1.7), 1.3), (s * (HW - 1.7), -1.3), (s * HW, -3.0)], fc=INK, zorder=6)
        )
    rect(ax, FLANGE["x"][0], FLANGE["x"][1], FLANGE["y"][0], FLANGE["y"][1], fc=SLED_C, ec=INK, lw=0.6, zorder=3)
    rect(
        ax,
        MOLEX_PLUG["x"][0],
        MOLEX_PLUG["x"][1],
        MOLEX_PLUG["y"][0],
        MOLEX_PLUG["y"][1],
        fc="#dddddd",
        ec=INK,
        lw=0.6,
        zorder=4,
    )
    ax.plot([-6, -12, -12], [-8, -8, -33], color=WIRE_C, lw=2.5, zorder=4)
    ax.plot([-4, 8, 12], [-6, 6, 9], color=WIRE_C, lw=1.6, zorder=4)
    ax.text(
        0,
        -60,
        "shell rib ring (x 26.5..28, z 3..10) bears on the sled base (grey); countersunk clamp screws (+-15)\n"
        "hold the sled to the frame; the low shell screws (z 14) go through the flanks into M3 x 4 inserts in\n"
        "sled pads (x 21.6..26.0) across 0.4 from the shell's inner pads; 6S plug and leads in the bay",
        fontsize=7,
        ha="center",
        va="top",
    )
    ax.set_xlim(-62, 62)
    ax.set_ylim(-76, 48)
    ax.axis("off")
    ax.set_title("(c) power bay from above, z = 14\nhow the shell meets the sled and the frame", fontsize=9)
    # (d) prop plane, unchanged from v1
    ax = axes[3]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=9, solid_capstyle="round", zorder=0)
        ax.add_patch(Circle((sx * MOTOR_XY, sy * MOTOR_XY), PROP_R, fc="none", ec=INK, lw=0.9))
        ax.add_patch(Circle((sx * MOTOR_XY, sy * MOTOR_XY), 9, fc="#555555", ec="none"))
    ax.add_patch(Polygon(stadium(0, 0, 50, 75), closed=True, fc="none", ec=OLD, lw=1.0, ls="--"))
    ax.add_patch(Polygon(faceted(HW, HH, SIDE_Y, CROWN_X), closed=True, fc=BODY, ec=INK, lw=1.4))
    p, q = np.array([HW, SIDE_Y]), np.array([CROWN_X, HH])
    d = q - p
    m = np.array([MOTOR_XY, MOTOR_XY])
    t = np.clip(np.dot(m - p, d) / np.dot(d, d), 0, 1)
    foot = p + t * d
    tip = m - PROP_R * (m - foot) / np.linalg.norm(m - foot)
    ax.plot([foot[0], tip[0]], [foot[1], tip[1]], color=ESC_C, lw=1.6, zorder=5)
    gap = np.linalg.norm(m - foot) - PROP_R
    ax.text(
        42, 4, f"{gap:.1f} mm to a 5 in prop\n(unchanged from v1)", fontsize=7.5, color=ESC_C, ha="left", va="center"
    )
    ax.text(
        0,
        -138,
        "Same section as v1 at the prop plane (z 47..59); the grille below it\nsits between the two port "
        "arms, in the props' inflow.",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    ax.set_xlim(-150, 150)
    ax.set_ylim(-160, 145)
    ax.axis("off")
    ax.set_title("(d) prop plane, looking down the fuselage\nmotors at (+-80, +-80)", fontsize=9)
    fig.suptitle(
        "sprite-aleph-v2, iteration 2: cross-sections (x across, y toward the cover; mm)",
        fontsize=11,
        x=0.02,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(OUT / "sections.png", dpi=170)
    plt.close(fig)


def plan_view():
    fig, ax = plt.subplots(figsize=(17, 6.8))
    ax.set_aspect("equal")
    top = law(W_LAW, 0, TIP_Z)
    outline = top + [(z, -w) for z, w in reversed(top)]
    ax.add_patch(Polygon(outline, closed=True, fc=BODY, ec=INK, lw=1.4))
    for s in (1, -1):
        ax.plot([z for z, _ in NOSE_HALF_WIDTH], [s * w for _, w in NOSE_HALF_WIDTH], color=OLD, lw=0.9, ls="--")
    cone = [(z, x) for z, x in CONE_X] + [(z, -x) for z, x in reversed(CONE_X)]
    ax.add_patch(Polygon(cone, closed=True, fc="none", ec=INK, lw=1.2))
    rect(ax, -6, 0, -25, 25, fc="#3b3b3b", ec="none")
    rect(ax, -6, 0, -13.5, 13.5, fc="white", ec="none")
    rect(ax, 0, ROOF_END, -HW, HW, fc="none", ec=INK, hatch="////", lw=0)
    ax.text(11, 34, "roof lip", fontsize=7.5, ha="center")
    ax.text(-45, 0, "Sprite tail cone\n(v1, unchanged)", fontsize=7.5, ha="center", va="center", color="#555555")
    rect(ax, ESC_PCB_Z[0], ESC_PCB_Z[0] + 1.6, ESC_X[0], ESC_X[1], fc=ESC_C, ec=INK, lw=0.6)
    ax.text(-20, -32, "ESC", fontsize=6.5, ha="center", va="top", color=ESC_C)
    # sled from above: base, wall, flange, tray, lips, bulkhead, slots, XT60
    rect(ax, BASE_Z[0], BASE_Z[1], -27.7, 27.7, fc=SLED_C, ec=INK, lw=0.6)
    rect(ax, SLED_WALL_Z[0], SLED_WALL_Z[1], SLED_WALL_X[0], SLED_WALL_X[1], fc=SLED_C, ec=INK, lw=0.6)
    rect(ax, FLANGE["z"][0], FLANGE["z"][1], FLANGE["x"][0], FLANGE["x"][1], fc=SLED_C, alpha=0.5, ec=INK, lw=0.5)
    rect(ax, TRAY["z"][0], TRAY["z"][1], TRAY["x"][0], TRAY["x"][1], fc=SLED_C, alpha=0.35, ec=INK, lw=0.6)
    for s in (1, -1):
        rect(ax, TRAY["z"][0], TRAY["z"][1], s * LIPS["x"][0], s * LIPS["x"][1], fc=SLED_C, ec=INK, lw=0.5)
    rect(ax, BULKHEAD["z"][0], BULKHEAD["z"][1], TRAY["x"][0], TRAY["x"][1], fc=SLED_C, ec=INK, lw=0.6)
    for zs in STRAPS:
        rect(ax, zs - 1, zs + 1, -26, 26, fc=INK, ec="none")
    rect(ax, XT60["z"][0], XT60["z"][1], XT60["x"][0], XT60["x"][1], fc=WIRE_C, ec=INK, lw=0.6)
    ax.text(113, -24.5, "XT60", fontsize=6.5, ha="center", va="top")
    for zc, _ in SCREWS:
        for s in (1, -1):
            rect(ax, zc - PAD_R, zc + PAD_R, s * SLED_PAD_X[0], s * SLED_PAD_X[1], fc=SLED_C, ec=INK, lw=0.6)
            ax.plot([zc, zc], [s * (SLED_PAD_X[1] - 4.0), s * HW], color=INK, lw=1.4)
            ax.add_patch(
                Polygon(
                    [(zc - 3, s * HW), (zc - 1.3, s * (HW - 1.7)), (zc + 1.3, s * (HW - 1.7)), (zc + 3, s * HW)], fc=INK
                )
            )
    ax.text(14, -33, "shell screws\nz 14 and 112", fontsize=6.5, ha="center", va="top")
    rect(
        ax, MOLEX_PLUG["z"][0], MOLEX_PLUG["z"][1], MOLEX_PLUG["x"][0], MOLEX_PLUG["x"][1], fc="#dddddd", ec=INK, lw=0.6
    )
    ax.text(11, 19, "6S plug", fontsize=6, ha="center", va="bottom")
    # battery
    rect(ax, BATTERY["z"][0], BATTERY["z"][1], BATTERY["x"][0], BATTERY["x"][1], fc=BAT_C, alpha=0.85, ec=INK, lw=0.8)
    rect(ax, BAT_ENV["z"][0], BAT_ENV["z"][1], BAT_ENV["x"][0], BAT_ENV["x"][1], fc="none", ec=INK, lw=0.8, ls="--")
    ax.text(160.5, 0, "6S pack: V5 1400 shown, envelope 81 x 48 dashed", fontsize=7.5, ha="center", va="center")
    ax.text(
        160.5,
        -30,
        "tray on the sled: floor, lips x 24..25.5, strap slots, bulkhead z 117..119",
        fontsize=7,
        ha="center",
        va="top",
        color="#555555",
    )
    # Aleph layers from above
    rect(ax, BOARD_Z[0], BOARD_Z[1], LAYERS_X["base"][0], LAYERS_X["base"][1], fc=ALEPH_C, ec=INK, lw=0.6)
    for zc in HOLES_Z:
        rect(ax, zc - 2.5, zc + 2.5, XP, SLED_WALL_X[0], fc="#dddddd", ec=INK, lw=0.5)
        rect(ax, zc - 2.5, zc + 2.5, LAYERS_X["standoff"][0], LAYERS_X["standoff"][1], fc="#dddddd", ec=INK, lw=0.5)
    rect(ax, BOARD_Z[0], BOARD_Z[1], LAYERS_X["carrier"][0], LAYERS_X["carrier"][1], fc=ALEPH_C, ec=INK, lw=0.6)
    rect(ax, SODIMM["z"][0], SODIMM["z"][1], LAYERS_X["sodimm"][0], LAYERS_X["sodimm"][1], fc="#cccccc", ec=INK, lw=0.5)
    rect(ax, MODULE["z"][0], MODULE["z"][1], LAYERS_X["module"][0], LAYERS_X["module"][1], fc=ALEPH_C, ec=INK, lw=0.6)
    rect(ax, LID["z"][0], LID["z"][1], LAYERS_X["lid"][0], LAYERS_X["lid"][1], fc="#555555", ec=INK, lw=0.5)
    rect(
        ax,
        HEATSINK["z"][0],
        HEATSINK["z"][1],
        LAYERS_X["heatsink"][0],
        LAYERS_X["heatsink"][1],
        fc=HS_C,
        alpha=0.7,
        ec=INK,
        lw=0.8,
    )
    rect(
        ax,
        GRILLE["z"][0],
        GRILLE["z"][1],
        -INNER["hw"] - 2.3,
        -INNER["hw"] + 0.3,
        fc="white",
        ec=VENT_C,
        lw=1.2,
        ls="--",
    )
    for lv in LOUVERS:
        rect(ax, lv["z"][0], lv["z"][1], -INNER["hw"] - 2.6, -INNER["hw"] + 0.6, fc="none", ec=VENT_C, lw=1.0, ls=":")
    ax.text(
        63,
        -36,
        "heatsink inside; grille 60 x 30 in the port wall over it, louvers fore and aft",
        fontsize=7.5,
        ha="center",
        va="top",
        color=HS_C,
    )
    ax.text(
        63,
        35.5,
        "Aleph: sled wall (x 21.6..25.6), four 4 mm standoffs, base, standoffs, carrier, SO-DIMM,\n"
        "module, lid, heatsink; power end aft toward the bay",
        fontsize=7,
        ha="center",
        va="bottom",
        color="#555555",
    )
    # nose parts
    hw_in = [interp(top, z) - WALL - 0.5 for z in VTX_Z]
    vtx = [(VTX_Z[0], hw_in[0]), (VTX_Z[1], hw_in[1]), (VTX_Z[1], -hw_in[1]), (VTX_Z[0], -hw_in[0])]
    ax.add_patch(Polygon(vtx, closed=True, fc=NOSE_C, ec=INK, lw=0.6))
    rect(ax, SERVO_Z[0], SERVO_Z[1], -18.5, 18.5, fc=NOSE_C, ec=INK, lw=0.6)
    rect(ax, 234, 253, -10, 10, fc=NOSE_C, ec=INK, lw=0.6)
    for s in (1, -1):
        rect(ax, 234, 250, s * 13 - 3, s * 13 + 3, fc=NOSE_C, ec=INK, lw=0.5)
    ax.text(207.5, 31, "VTX mount\nz 203..212", fontsize=7, ha="center", va="bottom")
    ax.text(222, -21, "servo", fontsize=7, ha="center", va="top")
    ax.text(243.5, -18, "camera", fontsize=7, ha="center", va="top")
    ax.text(
        222,
        -40,
        "width law: 30 to z 202, Hermite to 13.1 at 249.3 (end slope -0.40);\nSprite nose dashed",
        fontsize=7,
        ha="center",
        va="top",
    )
    # axes and stations
    ax.annotate("", xy=(295, -70), xytext=(-70, -70), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(295, -76, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-70, -45), xytext=(-70, -70), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-67, -47, "x (starboard)", fontsize=8)
    for z, lab in [
        (-20, "-20"),
        (0, "0"),
        (19, "19"),
        (107, "107"),
        (117, "117"),
        (WALL_END, "202"),
        (MORPH[1], "225"),
        (TIP_Z, "249.3"),
    ]:
        ax.plot([z, z], [-67, -64], color=INK, lw=0.6)
        ax.text(z, -68.5, lab, fontsize=7, ha="center", va="top")
    ax.set_xlim(-75, 300)
    ax.set_ylim(-80, 50)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph-v2, iteration 2: plan view with the cover removed (mm, assembly frame)", fontsize=11, loc="left"
    )
    fig.tight_layout()
    fig.savefig(OUT / "plan-view.png", dpi=170)
    plt.close(fig)


def nose():
    fig, axes = plt.subplots(1, 4, figsize=(22, 6.8), gridspec_kw={"width_ratios": [1, 1, 1, 1.9]})
    wall_end = nose_section(WALL_END)
    for ax, z in zip(axes[:3], (210.0, 225.0, 240.0)):
        ax.set_aspect("equal")
        ax.add_patch(Polygon(wall_end, closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
        outer = nose_section(z)
        ax.add_patch(Polygon(outer, closed=True, fc=BODY, ec=INK, lw=1.4))
        ax.add_patch(Polygon(inner_of(outer), closed=True, fc="white", ec=INK, lw=0.8))
        cover = outer[outer[:, 1] >= split_y(z)]
        ax.plot(cover[:, 0], cover[:, 1], color=COVER_C, lw=3.0, alpha=0.8)
        ax.plot([-40, 40], [split_y(z)] * 2, color=INK, lw=0.6, ls=":")
        w, c, k = herm(z, *W_LAW), herm(z, *C_LAW), herm(z, *K_LAW)
        b = smooth((z - MORPH[0]) / (MORPH[1] - MORPH[0]))
        ax.text(
            0,
            -44,
            f"half width {w:.2f}, crown {c:.2f}, keel {k:.2f}\nsplit y {split_y(z):.1f}; ellipse blend {b:.2f}",
            fontsize=7.5,
            ha="center",
            va="top",
        )
        ax.set_xlim(-40, 40)
        ax.set_ylim(-52, 42)
        ax.axis("off")
        ax.set_title(f"z = {z:.0f}", fontsize=9)
    axes[0].text(0, 38.5, "wall-end section z 202 dashed; cover blue", fontsize=7, ha="center", color="#555555")
    axes[2].add_patch(Circle((0, -2.3), 9.0, fc="none", ec=NOSE_C, lw=1.0, ls="--"))
    axes[2].text(0, 8, "camera", fontsize=7, ha="center", color="#555555")
    # the three laws against the Sprite's measured nose
    ax = axes[3]
    for spec, pts, lab, col in (
        (W_LAW, NOSE_HALF_WIDTH, "half width", INK),
        (C_LAW, COVER_TOP, "crown (cover)", COVER_C),
        (K_LAW, NOSE_BOTTOM, "keel (shell)", ESC_C),
    ):
        zmax = COVER_TIP_Z if spec is C_LAW else TIP_Z
        ax.plot(*zip(*law(spec, 120, zmax)), color=col, lw=1.6, label=f"v2 {lab}")
        ax.plot(*zip(*pts), "o", ms=3.5, mfc="none", color=col, label=f"Sprite {lab}")
    ax.plot(
        [z for z in np.linspace(WALL_END, TIP_Z, 60)],
        [split_y(z) for z in np.linspace(WALL_END, TIP_Z, 60)],
        color=INK,
        lw=0.9,
        ls=":",
        label="split",
    )
    for z in STATIONS:
        ax.axvline(z, color="#dddddd", lw=0.6, zorder=0)
    ax.axvspan(*MORPH, color="#f3efe6", zorder=-1)
    ax.text(213.5, 1.5, "section morph\n202..225", fontsize=7, ha="center")
    ax.set_xlim(120, 260)
    ax.set_xlabel("z (mm)")
    ax.set_ylabel("y or x (mm)")
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.set_title("cubic Hermite laws (slope 0 at the start, the Sprite's slope at the tip); stations grey", fontsize=9)
    fig.suptitle("sprite-aleph-v2, iteration 2: the nose (mm, assembly frame)", fontsize=11, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "nose.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    side_elevation()
    sections()
    plan_view()
    nose()
    print("wrote", *(OUT / f"{n}.png" for n in ("side-elevation", "sections", "plan-view", "nose")))
