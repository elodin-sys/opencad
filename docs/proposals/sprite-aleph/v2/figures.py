"""Figures for the sprite-aleph design proposal, iteration 2. Run from the repo root:
.venv/bin/python docs/proposals/sprite-aleph/figures.py

Sprite-drone assembly frame (mm): z along the fuselage from the carbon plate top face toward the nose, y toward the top
cover, x lateral (starboard positive). Numbers match proposal.md; change them together.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

OUT = Path(__file__).parent

# ---- measured Sprite outlines (assembly frame) ----
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
# Sprite tail cone outer half-height (y) and half-width (x) by z, from the rear shell STL
CONE_Y = [
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
    (-26.5, 28.6),
    (-31.5, 27.9),
    (-41.5, 25.6),
    (-51.5, 22.3),
    (-61.5, 17.8),
    (-71.5, 12.9),
    (-81.5, 9.1),
    (-91.5, 4.8),
]

W, H, WALL = 50.0, 75.0, 2.0  # body section unchanged
ROOF_END, WALL_END = 33.0, 170.16
GROOVE_Y = (4.25, 8.25)
INNER_FLOOR_Y = -22.5  # Sprite internal floor over the corner cells, kept in the battery bay only
FLOOR_END_Z = 86.0

# battery bay
BATTERY = {
    "z": (5.0, 83.0),
    "y": (-22.5, 19.5),
    "x": (-19.5, 19.5),
}  # Tattu R-Line V5 1400 6S, on its side (39 wide, 42 tall)
POCKET_Z = (3.0, 86.0)
ALCOVE_Z = (86.0, 97.2)
XT60 = {"x": (4.0, 20.0), "z": (88.0, 96.0), "y": (-12.0, 12.0)}
MOLEX_PLUG = {"x": (-7.0, 0.1), "y": (6.1, 14.9), "z": (85.0, 97.2)}

# Aleph on edge: rail face at x = -13, 2.5 standoffs, heights from designs/aleph-stack; heatsink 58 x 38 x 18 (user)
RAIL_X = (-15.0, -13.0)
BOARD_Y = (-30.0, 22.5)
BOARD_Z = (98.5, 186.5)
HOLES_Y = (-27.0, 19.5)
HOLES_Z = (101.5, 183.5)
LAYERS_X = {
    "parts": (-12.47, -10.5),
    "base": (-10.5, -8.94),
    "standoff": (-8.94, 1.06),
    "carrier": (1.06, 2.63),
    "sodimm": (2.63, 13.49),
    "module": (9.19, 10.39),
    "lid": (10.39, 13.02),
    "heatsink": (13.02, 31.02),
}
SODIMM = {"y": (-28.5, -23.5), "z": (104.4, 180.6)}
MODULE = {"y": (-23.5, 21.5), "z": (107.7, 177.3)}
HS_CENTER = {"y": 1.3, "z": 142.5}
HEATSINK = {"y": (-17.7, 20.3), "z": (113.5, 171.5)}
LID = {"y": (-8.8, 11.4), "z": (131.4, 153.6)}
FAN_D = 38.0
WINDOW = {"z": (112.0, 173.0), "y": (-19.0, 12.5)}
NOTCH = {"z": (112.0, 173.0), "y": (12.5, 21.5)}
LOUVERS = [{"z": (100.0, 111.0), "y": (-17.0, 10.0)}, {"z": (174.0, 185.0), "y": (-17.0, 10.0)}]
ETH = {"x": (-8.94, -1.61), "y": (11.6, 25.0), "z": (158.1, 168.9)}
USBC_BASE = {"x": (-8.94, -4.0), "y": (14.8, 22.5), "z": (111.3, 120.3)}
JSTGH = {"x": (-8.94, -2.96), "y": (17.25, 22.1), "z": (122.5, 154.8)}

# tail bulb and ESC
BULB_R = 56.0
BULB_Z = (-6.0, -24.0)
SHOULDER_END = -48.0
PLATE_Z = (-8.0, -6.0)  # new rear mount clamp plate
STANDOFF = 7.0
ESC_PCB_Z = (-16.6, -15.0)
ESC_HOUSING_Z = (-17.0, -10.15)
ESC_U = 31.58  # PCB half-length along its long axis
ESC_V = 21.12  # PCB half-width
MR30_U = (20.98, 38.31)
MR30_V = [(4.05, 19.58), (-19.58, -4.05)]
PLUG_U = (38.31, 46.5)
ESC_HOLE_R = 15.25 * np.sqrt(2)  # 30.5 pattern turned 45 deg: holes on the axes
MOTOR_XY = 80.0
PROP_R = {"5 in": 63.5, "4 in": 50.8}

INK, OLD, BODY = "#222222", "#9a9a9a", "#f3efe6"
ESC_C, BAT_C, ALEPH_C, TRAY_C, VENT_C, NOSE_C, HS_C = (
    "#c8553d",
    "#e0a458",
    "#4c86a8",
    "#8d99ae",
    "#2a9d8f",
    "#b7b7a4",
    "#2f5d7a",
)


def stadium(cx, cy, w, h, n=48):
    r = w / 2
    top = [(cx + r * np.cos(np.radians(a)), cy + h / 2 - r + r * np.sin(np.radians(a))) for a in np.linspace(0, 180, n)]
    bot = [
        (cx + r * np.cos(np.radians(a)), cy - h / 2 + r + r * np.sin(np.radians(a))) for a in np.linspace(180, 360, n)
    ]
    return np.array(top + bot)


def interp(profile, z):
    pts = sorted(profile)  # np.interp needs increasing abscissae; the cone profiles run downward in z
    zs, vs = zip(*pts)
    return float(np.interp(z, zs, vs))


def tail_profile(axis):
    """Outer half-extent (y or x) of the new tail versus z: bulb, shoulder, then the Sprite cone."""
    cone = CONE_Y if axis == "y" else CONE_X
    r_end = interp(cone, SHOULDER_END)
    zs = np.linspace(BULB_Z[1], SHOULDER_END, 14)
    t = (zs - BULB_Z[1]) / (SHOULDER_END - BULB_Z[1])
    shoulder = [(z, BULB_R + (r_end - BULB_R) * (1 - np.cos(np.pi * tt)) / 2) for z, tt in zip(zs, t)]
    return [(BULB_Z[0], BULB_R), (BULB_Z[1], BULB_R)] + shoulder + [(z, r) for z, r in cone if z < SHOULDER_END]


def rot45(u, v):
    c = 1 / np.sqrt(2)
    return u * c - v * c, u * c + v * c


def side_elevation():
    fig, ax = plt.subplots(figsize=(16, 7.6))
    ax.set_aspect("equal")
    # plate, floor, new tail (bulb + shoulder + Sprite cone), rear mount plate
    ax.add_patch(Rectangle((-6, -37.5), 6, 75, fc="#3b3b3b", ec="none"))
    ax.add_patch(Rectangle((-6, -13.5), 6, 27.0, fc="white", ec="none"))
    ax.add_patch(Rectangle((0, -37.5), 2, 75, fc=BODY, ec=INK, lw=0.8))
    prof = tail_profile("y")
    tail = [(z, y) for z, y in prof] + [(z, -y) for z, y in reversed(prof)]
    ax.add_patch(Polygon(tail, closed=True, fc="none", ec=INK, lw=1.2))
    old_cone = [(-6, 36.0)] + CONE_Y + [(z, -y) for z, y in reversed(CONE_Y)] + [(-6, -36.0)]
    ax.add_patch(Polygon(old_cone, closed=True, fc="none", ec=OLD, lw=0.8, ls="--"))
    ax.add_patch(Rectangle((PLATE_Z[0], -29), 2, 58, fc=TRAY_C, ec=INK, lw=0.6))
    # ESC projected on the side view (its 45 deg footprint spans y +-41 with the connectors)
    ax.add_patch(Rectangle((ESC_PCB_Z[0], -37.3), 1.6, 74.6, fc=ESC_C, ec=INK, lw=0.6))
    ax.add_patch(
        Rectangle((ESC_HOUSING_Z[0], -41), ESC_HOUSING_Z[1] - ESC_HOUSING_Z[0], 82, fc=ESC_C, alpha=0.25, ec="none")
    )
    for yc in (0, 21.57, -21.57):
        ax.add_patch(Rectangle((-8 - STANDOFF, yc - 2.5), STANDOFF, 5, fc=TRAY_C, ec=INK, lw=0.5))
    ax.text(
        -38,
        0,
        "tail bulb D112\nESC flat at 45 deg\non 7 mm standoffs,\nconnectors along\ntwo arms (see plan)",
        fontsize=7.5,
        ha="center",
        va="center",
    )
    ax.text(-70, -47, "shoulder blends\ninto the Sprite cone\nby z = -48", fontsize=7, ha="center", va="top")
    ax.annotate(
        "Sprite cone (dashed):\n56 x 73 inside, too small",
        xy=(-20, 36),
        xytext=(-40, 66),
        fontsize=7,
        ha="center",
        color="#555555",
        arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.6},
    )
    for yv in (44, -44):
        ax.annotate(
            "",
            xy=(-9, yv),
            xytext=(-2, yv + (8 if yv > 0 else -8)),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    ax.text(-6, 58, "downwash inlets\nin the bulb top", fontsize=7, ha="center", color=VENT_C)
    # fuselage outline (unchanged)
    bottom = [(2, -37.5), (WALL_END, -37.5)] + NOSE_BOTTOM[1:]
    ax.plot(*zip(*bottom), color=INK, lw=1.4)
    ax.plot([2, ROOF_END], [37.5, 37.5], color=INK, lw=1.4)
    ax.plot([ROOF_END, ROOF_END], [37.5, 12.5], color=INK, lw=1.0)
    ax.plot([ROOF_END, WALL_END], [12.5, 12.5], color=INK, lw=1.0)
    ax.plot([WALL_END, WALL_END], [12.5, 0], color=INK, lw=1.0)
    ax.plot([WALL_END, 249.3], [0, 0], color=INK, lw=0.8, ls=":")
    ax.plot([249.3, 249.3], [0, -22.9], color=INK, lw=1.4)
    cover = [(ROOF_END, 37.5)] + COVER_TOP + [(256.7, 0), (WALL_END, 0), (WALL_END, 12.5), (ROOF_END, 12.5)]
    ax.add_patch(Polygon(cover, closed=True, fc="none", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((2, 12.5), ROOF_END - 2, 25, fc="none", ec=INK, hatch="////", lw=0))
    ax.text(17, 43, "roof lip\n(battery pocket)", fontsize=7.5, ha="center")
    ax.text(
        60,
        41.5,
        "top cover: Sprite's, with a notch\nfor the heatsink on the starboard edge",
        fontsize=7.5,
        ha="center",
        va="bottom",
    )
    ax.plot([28, 168], [GROOVE_Y[0]] * 2, color=OLD, lw=0.6)
    ax.plot([28, 168], [GROOVE_Y[1]] * 2, color=OLD, lw=0.6)
    # internal floor and duct (kept to z = 86), cable path
    ax.add_patch(Rectangle((2, INNER_FLOOR_Y - 1), FLOOR_END_Z - 2, 1, fc=BODY, ec=INK, lw=0.6))
    ax.plot([-4, -4, 5, 5, 90, 90], [-16, -29, -29, -29, -29, -10], color="#f2c14e", lw=1.8)
    ax.text(
        45,
        -30.5,
        "wire duct: ESC power and signal leads up through the plate hole",
        fontsize=7,
        ha="center",
        va="top",
        color="#8a6d1c",
    )
    # battery on the internal floor, cradle lips, strap, alcove
    ax.add_patch(
        Rectangle(
            (BATTERY["z"][0], BATTERY["y"][0]),
            BATTERY["z"][1] - BATTERY["z"][0],
            BATTERY["y"][1] - BATTERY["y"][0],
            fc=BAT_C,
            ec=INK,
            lw=0.8,
        )
    )
    ax.text(
        44,
        -1.5,
        "6S 1400 pack on its side\n78 x 39 x 42 (Tattu R-Line V5)\nslides 30 mm under the roof lip,\nstrap at the front",
        fontsize=8,
        ha="center",
        va="center",
    )
    for zs in (40, 70):
        ax.plot([zs, zs], [-23.5, 20.5], color=INK, lw=1.2)
    ax.add_patch(Rectangle((FLOOR_END_Z, -22.5), 2, 32, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((XT60["z"][0], XT60["y"][0]), 8, 24, fc="#f2c14e", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((MOLEX_PLUG["z"][0], MOLEX_PLUG["y"][0]), 12.2, 8.8, fc="#dddddd", ec=INK, lw=0.6))
    ax.annotate(
        "connector alcove z 86..97:\nXT60 socket (pack lead) and\nthe Aleph's 6S power plug",
        xy=(92, 13),
        xytext=(92, -52),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    # Aleph on edge: rail (nearest the viewer), base board face, connectors on the top edge, module and heatsink behind
    ax.add_patch(Rectangle((BOARD_Z[0], BOARD_Y[0]), 88, 52.5, fc=ALEPH_C, alpha=0.35, ec=INK, lw=0.8))
    ax.add_patch(Rectangle((MODULE["z"][0], MODULE["y"][0]), 69.6, 45, fc="none", ec=INK, lw=0.6, ls=":"))
    ax.add_patch(Rectangle((HEATSINK["z"][0], HEATSINK["y"][0]), 58, 38, fc=HS_C, alpha=0.25, ec=HS_C, lw=1.0, ls="--"))
    ax.add_patch(Circle((HS_CENTER["z"], HS_CENTER["y"]), FAN_D / 2, fc="none", ec=HS_C, lw=0.8, ls="--"))
    for zc in HOLES_Z:
        for yc in HOLES_Y:
            ax.add_patch(Circle((zc, yc), 1.45, fc="white", ec=INK, lw=0.6))
    for c, lab in ((ETH, "ETH"), (USBC_BASE, "USB-C"), (JSTGH, "JST-GH")):
        ax.add_patch(
            Rectangle(
                (c["z"][0], c["y"][0]), c["z"][1] - c["z"][0], c["y"][1] - c["y"][0], fc="#dddddd", ec=INK, lw=0.5
            )
        )
        ax.text((c["z"][0] + c["z"][1]) / 2, c["y"][1] + 1, lab, fontsize=6, ha="center", va="bottom")
    ax.add_patch(Rectangle((RAIL_X[0], 0), 0, 0, fc="none", ec="none"))
    ax.text(
        142.5,
        51,
        "Aleph on edge: base board against a port-side rail, service edge up,\nheatsink (dashed) through the starboard wall, fan face 6 mm outside the skin",
        fontsize=8,
        ha="center",
        va="bottom",
    )
    ax.add_patch(
        Rectangle(
            (WINDOW["z"][0], WINDOW["y"][0]), 61, WINDOW["y"][1] - WINDOW["y"][0], fc="none", ec=VENT_C, lw=1.2, ls="--"
        )
    )
    ax.add_patch(Rectangle((NOTCH["z"][0], NOTCH["y"][0]), 61, 9, fc="none", ec=VENT_C, lw=1.2, ls="--"))
    ax.annotate(
        "starboard wall window 61 x 31.5\nand 9 mm cover notch (far wall)",
        xy=(173, 15),
        xytext=(205, -50),
        fontsize=7.5,
        ha="center",
        color=VENT_C,
        arrowprops={"arrowstyle": "-", "color": VENT_C, "lw": 0.6},
    )
    for lv in LOUVERS:
        ax.add_patch(
            Rectangle(
                (lv["z"][0], lv["y"][0]),
                lv["z"][1] - lv["z"][0],
                lv["y"][1] - lv["y"][0],
                fc="none",
                ec=VENT_C,
                lw=1.0,
                ls=":",
            )
        )
    ax.text(142.5, -35, "fin exhaust louvers fore and aft (starboard)", fontsize=7, ha="center", va="top", color=VENT_C)
    # nose (unchanged, VTX mount reused)
    ax.add_patch(Rectangle((190, -22), 9, 55, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((214.8, -30.6), 14.3, 44.4, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((234, -12), 19, 19, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Circle((244.0, -2.28), 2.0, fc="white", ec=INK, lw=0.6))
    ax.text(194.5, 37, "VTX mount\n(reused)", fontsize=7, ha="center", va="bottom")
    ax.text(222, 17, "servo mount\n(unchanged)", fontsize=7, ha="center")
    ax.text(243.5, 10, "camera + tilt\n(unchanged)", fontsize=7, ha="center")
    ax.text(-3, -42, "carbon plate\n(unchanged)", fontsize=7, ha="center", va="top")
    # axes, stations, bay brackets
    ax.annotate("", xy=(275, -96), xytext=(-105, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(275, -103, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-105, -66), xytext=(-105, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-102, -68, "y (cover)", fontsize=8)
    for z, lab in [
        (-48, "-48"),
        (-24, "-24"),
        (0, "0"),
        (ROOF_END, "33"),
        (86, "86"),
        (97, "97"),
        (190, "190"),
        (249.3, "249"),
    ]:
        ax.plot([z, z], [-93, -89], color=INK, lw=0.6)
        ax.text(z, -99, lab, fontsize=7, ha="center", va="top")
    for z0, z1, lab in [
        (-48, -6, "tail bulb: ESC, RX/GPS"),
        (3, 86, "battery bay (Sprite interior)"),
        (86, 97, ""),
        (97.2, 190, "Aleph bay (on edge)"),
        (190, 256.7, "nose (unchanged parts)"),
    ]:
        yy = -74
        ax.plot([z0, z1], [yy, yy], color=INK, lw=1.0)
        ax.plot([z0, z0], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.plot([z1, z1], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.text((z0 + z1) / 2, yy - 3.5, lab, fontsize=7.5, ha="center", va="top")
    ax.text(
        -105,
        -60,
        "plate top face z = 0. Body section 50 x 75 unchanged (5 in props). Hover: nose up.",
        fontsize=7.5,
        ha="left",
    )
    ax.set_xlim(-110, 280)
    ax.set_ylim(-108, 72)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph, iteration 2: side elevation, port wall removed (mm, assembly frame)", fontsize=11, loc="left"
    )
    fig.tight_layout()
    fig.savefig(OUT / "side-elevation.png", dpi=170)
    plt.close(fig)


def draw_section(ax, cover=True):
    ax.add_patch(Polygon(stadium(0, 0, W, H), closed=True, fc=BODY, ec=INK, lw=1.4))
    ax.add_patch(Polygon(stadium(0, 0, W - 2 * WALL, H - 2 * WALL), closed=True, fc="white", ec=INK, lw=0.8))
    ax.plot([-W / 2, W / 2], [12.5, 12.5], color=INK, lw=0.6, ls=":")
    for s in (1, -1):
        x0 = s * (W / 2 - WALL)
        ax.add_patch(Rectangle((min(x0, x0 + s * 1.2), GROOVE_Y[0]), 1.2, 4.0, fc="white", ec=INK, lw=0.6))
        ax.add_patch(Rectangle((min(x0, x0 + s * 1.15), GROOVE_Y[0] + 0.05), 1.15, 3.9, fc=INK, ec="none"))


def sections():
    fig, axes = plt.subplots(1, 4, figsize=(21, 7.8), gridspec_kw={"width_ratios": [1.1, 1.1, 1.5, 1.3]})
    # (a) battery bay: the Sprite section as is
    ax = axes[0]
    ax.set_aspect("equal")
    draw_section(ax)
    ax.add_patch(Rectangle((-20.5, INNER_FLOOR_Y - 1), 41, 1, fc=BODY, ec=INK, lw=0.6))
    for s in (1, -1):
        ax.plot([s * 10.25, s * 10.25], [INNER_FLOOR_Y, -33.0], color=INK, lw=0.8)
    ax.text(0, -30, "duct:\n2 x 10 AWG\n+ 8-pin", fontsize=6.5, ha="center", va="center", color="#8a6d1c")
    for s in (1, -1):
        ax.add_patch(Rectangle((s * 19.5 if s > 0 else -21.5, INNER_FLOOR_Y), 2, 10, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(Rectangle((-19.5, INNER_FLOOR_Y), 39, 42, fc=BAT_C, ec=INK, lw=0.8))
    ax.text(
        0, -1.5, "6S pack\n39 wide, 42 tall\non the Sprite's\ninternal floor", fontsize=7.5, ha="center", va="center"
    )
    ax.plot([-19.5, -19.5, 19.5, 19.5], [-22.5, 21, 21, -22.5], color=INK, lw=1.2)
    ax.set_title("(a) battery bay, z = 65\nSprite section, unchanged", fontsize=9)
    # (b) Aleph bay
    ax = axes[1]
    ax.set_aspect("equal")
    draw_section(ax)
    # starboard window through the wall and the cover notch
    ax.add_patch(Rectangle((22.4, WINDOW["y"][0]), 3.2, WINDOW["y"][1] - WINDOW["y"][0], fc="white", ec="none"))
    th = np.linspace(np.degrees(np.arcsin((NOTCH["y"][1] - 12.5) / 25)), 0, 12)
    notch = [(25 * np.cos(np.radians(a)), 12.5 + 25 * np.sin(np.radians(a))) for a in th]
    notch += [(23 * np.cos(np.radians(a)), 12.5 + 23 * np.sin(np.radians(a))) for a in th[::-1]]
    ax.add_patch(Polygon(notch, closed=True, fc="white", ec="none"))
    ax.plot([22.4, 22.4], [WINDOW["y"][0], NOTCH["y"][1] - 0.5], color=VENT_C, lw=1.0, ls="--")
    # rail with bosses, board layers
    ax.add_patch(Rectangle((RAIL_X[0], -30.5), 2, 56.5, fc=TRAY_C, ec=INK, lw=0.6))
    for yc in HOLES_Y:
        ax.add_patch(Rectangle((RAIL_X[1], yc - 2.5), 2.5, 5, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["parts"][0], BOARD_Y[0] + 2), 1.97, 48.5, fc=ALEPH_C, alpha=0.3, ec="none"))
    ax.add_patch(Rectangle((LAYERS_X["base"][0], BOARD_Y[0]), 1.56, 52.5, fc=ALEPH_C, ec=INK, lw=0.6))
    for yc in HOLES_Y:
        ax.add_patch(Rectangle((LAYERS_X["standoff"][0], yc - 2.5), 10, 5, fc="#dddddd", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["carrier"][0], BOARD_Y[0]), 1.57, 52.5, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LAYERS_X["sodimm"][0], SODIMM["y"][0]), 10.86, 5, fc="#bbbbbb", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["module"][0], MODULE["y"][0]), 1.2, 45, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LAYERS_X["lid"][0], LID["y"][0]), 2.63, 20.2, fc="#555555", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["heatsink"][0], HEATSINK["y"][0]), 18, 38, fc=HS_C, alpha=0.6, ec=INK, lw=0.8))
    for yy in np.arange(-15, 18.1, 3.3):
        ax.plot([LAYERS_X["heatsink"][0] + 0.5, LAYERS_X["heatsink"][0] + 9.5], [yy, yy], color="white", lw=0.6)
    ax.add_patch(
        Rectangle(
            (ETH["x"][0], ETH["y"][0]),
            ETH["x"][1] - ETH["x"][0],
            ETH["y"][1] - ETH["y"][0],
            fc="#dddddd",
            ec=INK,
            lw=0.5,
        )
    )
    ax.text(-5.3, 27, "ETH / USB-C / JST-GH\nup, cover-off access", fontsize=6.5, ha="center", va="bottom")
    for dy in (-12, 0, 12):
        ax.annotate(
            "",
            xy=(31.5, HS_CENTER["y"] + dy),
            xytext=(40, HS_CENTER["y"] + dy),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    ax.text(41, HS_CENTER["y"] + 22, "fan draws\noutside air", fontsize=7, ha="center", color=VENT_C)
    ax.text(-19, -8, "rail\n8 mm\ncable\ngap", fontsize=6, ha="center", va="center", color="#555555")
    ax.text(22, -25, "6 mm\nout", fontsize=6.5, ha="center", va="center", color=HS_C)
    ax.set_title("(b) Aleph bay, z = 143\non edge; heatsink through the starboard wall", fontsize=9)
    for ax in axes[:2]:
        ax.set_xlim(-46, 46)
        ax.set_ylim(-46, 46)
        ax.axis("off")
    # (c) tail bulb from below, at z = -15
    ax = axes[2]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=11, solid_capstyle="round", zorder=0)
    ax.add_patch(Circle((0, 0), BULB_R, fc=BODY, ec=INK, lw=1.4, zorder=1))
    ax.add_patch(Circle((0, 0), BULB_R - 0.8, fc="white", ec=INK, lw=0.6, zorder=1))
    ax.add_patch(Polygon(stadium(0, 0, 57, 74), closed=True, fc="none", ec=OLD, lw=0.9, ls="--", zorder=2))
    ax.add_patch(Circle((0, 0), 13.5, fc="white", ec=INK, lw=0.6, ls=":", zorder=2))
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.add_patch(Circle((sx * 15, sy * 15), 1.55, fc="white", ec=INK, lw=0.6, zorder=4))
    # ESC at 45 deg: PCB, MR30 housings, plugs, holes, studs
    pcb = [rot45(u, v) for u, v in [(-ESC_U, -ESC_V), (ESC_U, -ESC_V), (ESC_U, ESC_V), (-ESC_U, ESC_V)]]
    ax.add_patch(Polygon(pcb, closed=True, fc=ESC_C, alpha=0.35, ec=ESC_C, lw=1.0, zorder=3))
    for sgn in (1, -1):
        for v0, v1 in MR30_V:
            hsg = [rot45(sgn * u, v) for u, v in [(MR30_U[0], v0), (MR30_U[1], v0), (MR30_U[1], v1), (MR30_U[0], v1)]]
            ax.add_patch(Polygon(hsg, closed=True, fc=ESC_C, alpha=0.7, ec=INK, lw=0.5, zorder=4))
            plg = [
                rot45(sgn * u, v)
                for u, v in [(PLUG_U[0], v0 + 1), (PLUG_U[1], v0 + 1), (PLUG_U[1], v1 - 1), (PLUG_U[0], v1 - 1)]
            ]
            ax.add_patch(Polygon(plg, closed=True, fc="none", ec=ESC_C, lw=0.9, ls="--", zorder=4))
            xm, ym = rot45(sgn * (PLUG_U[1] + 6), (v0 + v1) / 2)
            ax.annotate(
                "",
                xy=(xm + sgn * 12, ym + sgn * 12),
                xytext=(xm, ym),
                arrowprops={"arrowstyle": "->", "color": ESC_C, "lw": 0.9},
            )
    for xh, yh in [(0, ESC_HOLE_R), (0, -ESC_HOLE_R), (ESC_HOLE_R, 0), (-ESC_HOLE_R, 0)]:
        ax.add_patch(Circle((xh, yh), 1.75, fc="white", ec=ESC_C, lw=0.8, zorder=5))
    for u in (6, -6):
        xs, ys = rot45(u, -20)
        ax.add_patch(Circle((xs, ys), 2.55, fc="#f2c14e", ec=INK, lw=0.6, zorder=5))
    ax.text(
        0,
        -63,
        "plate hole D27 (dotted), M3 clamps at (+-15, +-15),\nESC 30.5 holes on the axes at r 21.6 (red), battery studs (yellow);\nmotor leads (arrows) run on into the arm undersides",
        fontsize=7,
        ha="center",
        va="top",
    )
    ax.text(-42, 42, "inlet slots\nunder the props", fontsize=6.5, ha="center", color=VENT_C)
    for a0 in (0, 90, 180, 270):
        for rr in (44, 48, 52):
            th2 = np.radians(np.linspace(a0 - 20, a0 + 20, 20))
            ax.plot(rr * np.cos(th2), rr * np.sin(th2), color=VENT_C, lw=1.4, zorder=3)
    ax.set_xlim(-72, 72)
    ax.set_ylim(-80, 62)
    ax.axis("off")
    ax.set_title("(c) tail bulb from below, z = -15\nESC at 45 deg under the plate", fontsize=9)
    # (d) prop plane
    ax = axes[3]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=9, solid_capstyle="round", zorder=0)
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        mx, my = sx * MOTOR_XY, sy * MOTOR_XY
        ax.add_patch(Circle((mx, my), PROP_R["5 in"], fc="none", ec=INK, lw=0.9))
        ax.add_patch(Circle((mx, my), 9, fc="#555555", ec="none"))
    ax.add_patch(Circle((0, 0), BULB_R, fc="none", ec=OLD, lw=0.8, ls="--"))
    ax.add_patch(Polygon(stadium(0, 0, W, H), closed=True, fc=BODY, ec=INK, lw=1.4))
    c = np.array([0, 12.5])
    d = np.hypot(MOTOR_XY - c[0], MOTOR_XY - c[1])
    px, py = c + 25 * (np.array([MOTOR_XY, MOTOR_XY]) - c) / d
    tip = np.array([MOTOR_XY, MOTOR_XY]) - PROP_R["5 in"] * (np.array([MOTOR_XY, MOTOR_XY]) - c) / d
    ax.plot([px, tip[0]], [py, tip[1]], color=ESC_C, lw=1.6, zorder=5)
    ax.text(
        40,
        2,
        f"{d - 25 - PROP_R['5 in']:.0f} mm to a 5 in prop,\nas the Sprite today\n(section unchanged)",
        fontsize=7.5,
        color=ESC_C,
        ha="left",
        va="center",
    )
    ax.text(
        0,
        -138,
        "5 in props solid. The bulb (dashed, D112) is under the plate,\n20 mm below the prop plane; the heatsink is 90 mm above it.",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    ax.set_xlim(-150, 150)
    ax.set_ylim(-160, 145)
    ax.axis("off")
    ax.set_title("(d) prop plane, looking down the fuselage\nmotors at (+-80, +-80)", fontsize=9)
    fig.suptitle(
        "sprite-aleph, iteration 2: cross-sections (x across, y toward the cover; mm)", fontsize=11, x=0.02, ha="left"
    )
    fig.tight_layout()
    fig.savefig(OUT / "sections.png", dpi=170)
    plt.close(fig)


def plan_view():
    fig, ax = plt.subplots(figsize=(16, 7.0))
    ax.set_aspect("equal")
    # body outline (unchanged) and the tail bulb in plan
    top = [(2, 25), (200.5, 25)] + [(z, w) for z, w in NOSE_HALF_WIDTH if z > 200.5]
    outline = top + [(z, -w) for z, w in reversed(top)]
    ax.add_patch(Polygon(outline, closed=True, fc=BODY, ec=INK, lw=1.4))
    prof = tail_profile("x")
    tail = [(z, x) for z, x in prof] + [(z, -x) for z, x in reversed(prof)]
    ax.add_patch(Polygon(tail, closed=True, fc="none", ec=INK, lw=1.2))
    old_cone = [(-6, 28.6)] + CONE_X + [(z, -x) for z, x in reversed(CONE_X)] + [(-6, -28.6)]
    ax.add_patch(Polygon(old_cone, closed=True, fc="none", ec=OLD, lw=0.8, ls="--"))
    ax.add_patch(Rectangle((-6, -25), 6, 50, fc="#3b3b3b", ec="none"))
    ax.add_patch(Rectangle((-6, -13.5), 6, 27, fc="white", ec="none"))
    ax.add_patch(Rectangle((2, -25), ROOF_END - 2, 50, fc="none", ec=INK, hatch="////", lw=0))
    ax.text(17.5, 30, "roof lip", fontsize=7.5, ha="center")
    # ESC in the bulb (plan projection of the 45 deg board: it spans x +-41 with the connectors)
    ax.add_patch(Rectangle((ESC_HOUSING_Z[0], -41), 6.85, 82, fc=ESC_C, alpha=0.25, ec=ESC_C, lw=0.8, ls="--"))
    ax.add_patch(Rectangle((ESC_PCB_Z[0], -37.3), 1.6, 74.6, fc=ESC_C, ec=INK, lw=0.6))
    ax.text(-36, 0, "bulb D112:\nESC at 45 deg\n(see section c)", fontsize=7.5, ha="center", va="center")
    ax.text(-30, -62, "shoulder to the\nSprite cone at z -48", fontsize=7, ha="center", va="top")
    # battery, cradle, alcove
    ax.add_patch(Rectangle((BATTERY["z"][0], -19.5), 78, 39, fc=BAT_C, alpha=0.85, ec=INK, lw=0.8))
    ax.text(44, 0, "6S pack 78 x 39\n(on its side, 42 tall)", fontsize=8, ha="center", va="center")
    for zs in (40, 70):
        ax.add_patch(Rectangle((zs - 1, -21.5), 2, 43, fc=INK, ec="none"))
    for s in (1, -1):
        ax.add_patch(Rectangle((POCKET_Z[0], s * 19.5 if s > 0 else -21.5), 83, 2, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(Rectangle((FLOOR_END_Z, -21.5), 2, 43, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((XT60["z"][0], XT60["x"][0]), 8, 16, fc="#f2c14e", ec=INK, lw=0.6))
    ax.text(92, 22.5, "XT60", fontsize=6.5, ha="center", va="bottom")
    ax.add_patch(Rectangle((MOLEX_PLUG["z"][0], MOLEX_PLUG["x"][0]), 12.2, 7.1, fc="#dddddd", ec=INK, lw=0.6))
    ax.text(92, -9, "6S\nplug", fontsize=6, ha="center", va="top")
    ax.text(
        44,
        -30,
        "battery cradle: strap slots and the\nalcove bulkhead, glued on the internal floor",
        fontsize=7,
        ha="center",
        va="top",
        color="#555555",
    )
    # Aleph layers seen from above (x strips along z)
    ax.add_patch(Rectangle((97.2, RAIL_X[0]), 92.8, 2, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((BOARD_Z[0], LAYERS_X["base"][0]), 88, 1.56, fc=ALEPH_C, ec=INK, lw=0.6))
    for zc in HOLES_Z:
        ax.add_patch(Rectangle((zc - 2.5, LAYERS_X["standoff"][0]), 5, 10, fc="#dddddd", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((BOARD_Z[0], LAYERS_X["carrier"][0]), 88, 1.57, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((SODIMM["z"][0], LAYERS_X["sodimm"][0]), 76.2, 10.86, fc="#cccccc", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((MODULE["z"][0], LAYERS_X["module"][0]), 69.6, 1.2, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LID["z"][0], LAYERS_X["lid"][0]), 22.2, 2.63, fc="#555555", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((HEATSINK["z"][0], LAYERS_X["heatsink"][0]), 58, 18, fc=HS_C, alpha=0.7, ec=INK, lw=0.8))
    ax.plot([HEATSINK["z"][0] - 1.5, HEATSINK["z"][1] + 1.5], [25, 25], color="white", lw=2.2)
    ax.plot([HEATSINK["z"][0] - 1.5, HEATSINK["z"][0] - 1.5], [22.4, 25.6], color=VENT_C, lw=1.0, ls="--")
    ax.plot([HEATSINK["z"][1] + 1.5, HEATSINK["z"][1] + 1.5], [22.4, 25.6], color=VENT_C, lw=1.0, ls="--")
    ax.text(
        142.5,
        36,
        "heatsink 58 x 38 x 18 through the starboard wall, fan face 6 mm outside",
        fontsize=7.5,
        ha="center",
        va="bottom",
        color=HS_C,
    )
    for lv in LOUVERS:
        ax.add_patch(Rectangle((lv["z"][0], 23.4), lv["z"][1] - lv["z"][0], 3.2, fc="none", ec=VENT_C, lw=1.0, ls=":"))
    ax.text(142.5, 43, "fin exhaust louvers fore and aft", fontsize=7, ha="center", va="bottom", color=VENT_C)
    ax.text(
        150,
        -30,
        "port rail (2 mm) with four M2.5 bosses on 82 x 46.5;\nthen base, standoffs, carrier, SO-DIMM, module, lid, heatsink",
        fontsize=7,
        ha="center",
        va="top",
        color="#555555",
    )
    # nose parts
    ax.add_patch(Rectangle((190, -23), 9, 46, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((214.8, -18.5), 14.3, 37, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((234, -10), 19, 20, fc=NOSE_C, ec=INK, lw=0.6))
    for s in (1, -1):
        ax.add_patch(Rectangle((234, s * 13 - 3), 16, 6, fc=NOSE_C, ec=INK, lw=0.5))
    ax.text(194.5, 27, "VTX mount\n(reused)", fontsize=7, ha="center", va="bottom")
    ax.text(222, -21, "servo", fontsize=7, ha="center", va="top")
    ax.text(243.5, -18, "camera", fontsize=7, ha="center", va="top")
    # axes and stations
    ax.annotate("", xy=(275, -80), xytext=(-70, -80), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(275, -86, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-70, -55), xytext=(-70, -80), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-67, -57, "x (starboard)", fontsize=8)
    for z, lab in [(-48, "-48"), (0, "0"), (ROOF_END, "33"), (86, "86"), (97, "97"), (190, "190"), (249.3, "249")]:
        ax.plot([z, z], [-77, -74], color=INK, lw=0.6)
        ax.text(z, -78.5, lab, fontsize=7, ha="center", va="top")
    ax.set_xlim(-75, 280)
    ax.set_ylim(-90, 62)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph, iteration 2: plan view with the cover removed (mm, assembly frame; Sprite tail cone dashed)",
        fontsize=11,
        loc="left",
    )
    fig.tight_layout()
    fig.savefig(OUT / "plan-view.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    side_elevation()
    sections()
    plan_view()
    print("wrote", OUT / "side-elevation.png", OUT / "sections.png", OUT / "plan-view.png")
