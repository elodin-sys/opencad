"""Figures for the sprite-aleph design proposal. Run from the repo root: .venv/bin/python docs/proposals/sprite-aleph/figures.py

All coordinates are the sprite-drone assembly frame (mm): z along the fuselage from the carbon plate top face toward the
nose, y toward the top cover, x lateral. Numbers match proposal.md; change them there and here together.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

OUT = Path(__file__).parent

# ---- measured original outlines (assembly frame), from the source STLs ----
# fuselage bottom y_min(z) and cover top y_max(z); side walls end at z = 170.16, shell tip 249.3, cover tip 256.7
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
TAIL_CONE = [
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

# ---- new body ----
W_NEW, H = 62.0, 75.0  # outer width and height of the widened channel section
W_OLD = 50.0
WALL = 2.0
R_NEW = 20.0  # corner radius of the new section
FLARE = (2.0, 30.0)  # z range where the ring flares from 50 to 62 wide
BLEND = (195.0, 214.0)  # z range where the 62 wide channel blends back into the original nose
ROOF_END = 33.0
WALL_END = 170.16
GROOVE_Y = (4.25, 8.25)

# decks and components (z ranges, y ranges)
DECK_Y = (-19.0, -17.0)  # upper deck plate (battery cradle and Aleph tray)
ESC_TRAY_Y = (-35.5, -33.5)
ESC_PCB = {"z": (34.0, 97.15), "y": (-27.5, -25.9), "x": (-22.75, 19.5)}
ESC_PARTS_Y = (-32.1, -21.05)  # bottom-side parts to -4.58, top-side (MR30 tops) to +4.85 from the PCB top
ESC_HOUSING = [(27.3, 34.0), (97.15, 103.9)]
ESC_PLUGS = [(12.0, 27.3), (103.9, 119.0)]
MR30_X = [(-19.6, -4.05), (4.05, 19.6)]
BATTERY = {"z": (14.0, 92.0), "y": (-17.0, 25.0), "x": (-19.5, 19.5)}  # Tattu R-Line V5 1400 6S: 78 x 39 x 42
BATTERY_ALT = {"y": (-17.0, 31.0), "x": (-17.5, 17.5)}  # CNHL 1300 6S on its side: 35 x 48
POCKET_Z = (12.0, 96.0)
ALEPH_TRAY_Z = (97.5, 189.5)
BASE_Z = (98.5, 186.5)
BASE_X = (-25.0, 27.5)
STACK_Y0 = -14.5  # base board bottom face
# stack heights above the base bottom, from designs/aleph-stack (base 1.56, standoffs 10, carrier 1.57, spacers to 8.13, module 1.2, lid to 3.83, heatsink 15)
LAYERS = [
    ("base", 0.0, 1.56, BASE_X),
    ("carrier", 11.56, 13.13, BASE_X),
    ("module", 19.69, 20.89, (-24.0, 21.0)),
    ("SoC lid", 20.89, 23.52, (-13.9, 6.3)),
    ("heatsink + fan", 23.52, 38.52, (-23.8, 16.2)),
]
HEATSINK_Z = (112.0, 173.0)
FAN = {"x": -3.8, "z": 142.5, "d": 38.5}  # SoC lid centre: carrier (44.0, 21.19) -> drone x = -25 + 21.19
GRILLE_Z = (122.0, 163.0)
WINDOW = {"z": (114.0, 176.0), "y": (-16.0, -1.0)}
ESC_LOUVERS = {"z": (40.0, 95.0), "y": (-33.0, -22.0)}
ALEPH_LOUVERS = {"z": (105.0, 185.0), "y": (-12.0, 0.0)}
VTX = {"z": (190.0, 199.0), "y": (-22.0, 33.0), "x": (-28.0, 28.0)}
SERVO = {"z": (214.8, 229.1), "y": (-30.6, 13.8), "x": (-18.5, 18.5)}
CAMERA = {"z": (234.0, 253.0), "y": (-12.0, 7.0), "x": (-10.0, 10.0)}
MOTOR_XY = 80.0
PROP_R = {"4 in": 50.8, "3.5 in": 44.45, "5 in": 63.5}

INK = "#222222"
OLD = "#9a9a9a"
BODY = "#f3efe6"
ESC_C = "#c8553d"
BAT_C = "#e0a458"
ALEPH_C = "#4c86a8"
TRAY_C = "#8d99ae"
VENT_C = "#2a9d8f"
NOSE_C = "#b7b7a4"


def rounded_rect(cx, cy, w, h, r, n=24):
    """Closed outline of a rounded rectangle centred at (cx, cy)."""
    pts = []
    for sx, sy, a0 in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for a in np.linspace(a0, a0 + 90, n):
            pts.append((ccx + r * np.cos(np.radians(a)), ccy + r * np.sin(np.radians(a))))
    return np.array(pts)


def stadium(cx, cy, w, h, n=48):
    """The original 50 x 75 section: two semicircles of radius w/2 joined by straight sides."""
    r = w / 2
    top = [(cx + r * np.cos(np.radians(a)), cy + h / 2 - r + r * np.sin(np.radians(a))) for a in np.linspace(0, 180, n)]
    bot = [
        (cx + r * np.cos(np.radians(a)), cy - h / 2 + r + r * np.sin(np.radians(a))) for a in np.linspace(180, 360, n)
    ]
    return np.array(top + bot)


def interp(profile, z):
    zs, vs = zip(*profile)
    return float(np.interp(z, zs, vs))


def side_elevation():
    fig, ax = plt.subplots(figsize=(16, 7.2))
    ax.set_aspect("equal")
    # carbon plate, floor, tail cone, rear mount
    ax.add_patch(Rectangle((-6, -37.5), 6, 75, fc="#3b3b3b", ec="none"))
    ax.add_patch(Rectangle((-6, -34.0), 6, 9.0, fc="white", ec="none"))  # -y wire slot in the plate
    ax.add_patch(Rectangle((-6, -13.5), 6, 27.0, fc="white", ec="none"))  # D27 centre hole
    ax.add_patch(Rectangle((0, -37.5), 2, 75, fc=BODY, ec=INK, lw=0.8))
    cone = [(z, y) for z, y in TAIL_CONE] + [(z, -y) for z, y in reversed(TAIL_CONE)]
    ax.add_patch(Polygon(cone, closed=True, fc="none", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((-30, -36.6), 24, 73.2, fc="none", ec=OLD, lw=0.8, ls="--"))
    ax.text(
        -50,
        0,
        "tail cone\n(unchanged)\nFC bay now free:\nBEC / RX / GPS",
        ha="center",
        va="center",
        fontsize=8,
        color=INK,
    )
    # fuselage bottom line and roof / wall top / cover top
    bottom = [(2, -37.5), (WALL_END, -37.5)] + NOSE_BOTTOM[1:]
    ax.plot(*zip(*bottom), color=INK, lw=1.4)
    ax.plot([2, ROOF_END], [37.5, 37.5], color=INK, lw=1.4)  # roof
    ax.plot([ROOF_END, ROOF_END], [37.5, 12.5], color=INK, lw=1.0)
    ax.plot([ROOF_END, WALL_END], [12.5, 12.5], color=INK, lw=1.0)  # wall top edge
    ax.plot([WALL_END, WALL_END], [12.5, 0], color=INK, lw=1.0)
    ax.plot([WALL_END, 249.3], [0, 0], color=INK, lw=0.8, ls=":")  # nose split line
    ax.plot([249.3, 249.3], [0, -22.9], color=INK, lw=1.4)  # shell tip
    cover = [(ROOF_END, 37.5)] + COVER_TOP + [(256.7, 0), (WALL_END, 0), (WALL_END, 12.5), (ROOF_END, 12.5)]
    ax.add_patch(Polygon(cover, closed=True, fc="none", ec=INK, lw=1.2, ls="-"))
    ax.text(76, 41.5, "top cover (new, 62 wide; nose portion as original)", fontsize=8, ha="center", color=INK)
    ax.text(17, 44, "roof lip\n(battery pocket)", fontsize=7.5, ha="center", color=INK)
    ax.add_patch(Rectangle((2, 12.5), ROOF_END - 2, 25, fc="none", ec=INK, hatch="////", lw=0))
    # grooves (profile shown in the sections figure)
    ax.plot([30, 168], [GROOVE_Y[0]] * 2, color=OLD, lw=0.6)
    ax.plot([30, 168], [GROOVE_Y[1]] * 2, color=OLD, lw=0.6)
    # ESC tray, ESC, housings, plugs
    ax.add_patch(Rectangle((30, ESC_TRAY_Y[0]), 70, 2, fc=TRAY_C, ec=INK, lw=0.6))
    for zc in (50.3, 80.8):  # standoff columns at the 30.5 pattern
        ax.add_patch(Rectangle((zc - 2.5, -33.5), 5, 6, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(
        Rectangle(
            (ESC_PCB["z"][0], ESC_PARTS_Y[0]),
            ESC_PCB["z"][1] - ESC_PCB["z"][0],
            ESC_PARTS_Y[1] - ESC_PARTS_Y[0],
            fc=ESC_C,
            alpha=0.25,
            ec="none",
        )
    )
    ax.add_patch(
        Rectangle((ESC_PCB["z"][0], ESC_PCB["y"][0]), ESC_PCB["z"][1] - ESC_PCB["z"][0], 1.6, fc=ESC_C, ec=INK, lw=0.6)
    )
    for z0, z1 in ESC_HOUSING:
        ax.add_patch(Rectangle((z0, -27.9), z1 - z0, 6.9, fc=ESC_C, ec=INK, lw=0.6))
    for z0, z1 in ESC_PLUGS:
        ax.add_patch(Rectangle((z0, -28.5), z1 - z0, 8, fc="none", ec=ESC_C, lw=0.8, ls="--"))
    ax.annotate(
        "ARK 4IN1 ESC CONS on the floor deck\n(PCB 63 x 42, MR30s fore and aft)",
        xy=(58, -29),
        xytext=(55, -60),
        fontsize=8,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    ax.text(19, -46, "motor plugs\n(leads from the\nplate slot)", fontsize=7, ha="center", color=ESC_C)
    ax.text(128, -46, "plugs pass under\nthe Aleph tray", fontsize=7, ha="center", color=ESC_C)
    # battery deck and pack
    ax.add_patch(Rectangle((POCKET_Z[0], DECK_Y[0]), POCKET_Z[1] - POCKET_Z[0], 2, fc=TRAY_C, ec=INK, lw=0.6))
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
        53,
        4,
        "6S 1300-1400 pack\n78 x 39 x 42 (Tattu R-Line V5)\nslides 21 mm under the roof lip,\nstrap at the front",
        fontsize=8,
        ha="center",
        va="center",
    )
    for zs in (60, 86):
        ax.plot([zs, zs], [-19, 26], color=INK, lw=1.2)
    ax.add_patch(Rectangle((97.5, -10), 6.5, 12, fc="#f2c14e", ec=INK, lw=0.6))
    ax.annotate(
        "XT60 socket in the\ntray bulkhead",
        xy=(100.7, -9),
        xytext=(92, -46),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    # Aleph tray, legs, stack
    ax.add_patch(
        Rectangle((ALEPH_TRAY_Z[0], DECK_Y[0]), ALEPH_TRAY_Z[1] - ALEPH_TRAY_Z[0], 2, fc=TRAY_C, ec=INK, lw=0.6)
    )
    for z0 in (125, 155, 185.5):
        ax.add_patch(Rectangle((z0, -35.5), 4, 16.5, fc=TRAY_C, ec=INK, lw=0.5))
    ax.text(150, -27.5, "wiring tunnel", fontsize=7.5, ha="center", va="center", color="#555555")
    for name, h0, h1, _x in LAYERS:
        z0, z1 = BASE_Z if name in ("base", "carrier") else (HEATSINK_Z if name == "heatsink + fan" else (107.7, 177.3))
        if name == "SoC lid":
            z0, z1 = 131.4, 153.6
        ax.add_patch(
            Rectangle(
                (z0, STACK_Y0 + h0),
                z1 - z0,
                h1 - h0,
                fc=ALEPH_C,
                alpha=0.9 if name != "heatsink + fan" else 0.5,
                ec=INK,
                lw=0.6,
            )
        )
    for zc in (101.5, 183.5):  # M2.5 standoffs between the boards
        ax.add_patch(Rectangle((zc - 2.5, STACK_Y0 + 1.56), 5, 10, fc="#dddddd", ec=INK, lw=0.5))
    for zc in (101.5, 183.5):  # tray bosses
        ax.add_patch(Rectangle((zc - 3, DECK_Y[1]), 6, 2.5, fc=TRAY_C, ec=INK, lw=0.5))
    ax.text(142.5, STACK_Y0 + 32, "fan", fontsize=7, ha="center", color=INK)
    for dz in (-12, 0, 12):
        ax.annotate(
            "",
            xy=(142.5 + dz, STACK_Y0 + 38.6),
            xytext=(142.5 + dz, 36.0),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    ax.text(
        150,
        52,
        "Aleph stack, flat, fan up: base 88 x 52.5 on the tray,\nheatsink top at y = 24, 11 mm under the cover",
        fontsize=8,
        ha="center",
    )
    # grille, window, louvers
    for zg in np.arange(GRILLE_Z[0], GRILLE_Z[1] + 0.1, 4.0):
        ax.plot([zg, zg], [36.2, 38.8], color=VENT_C, lw=1.6)
    ax.text(142.5, 41.5, "intake grille in the cover", fontsize=7.5, ha="center", color=VENT_C)
    ax.add_patch(
        Rectangle(
            (WINDOW["z"][0], WINDOW["y"][0]),
            WINDOW["z"][1] - WINDOW["z"][0],
            WINDOW["y"][1] - WINDOW["y"][0],
            fc="none",
            ec=VENT_C,
            lw=1.2,
            ls="--",
        )
    )
    ax.annotate(
        "service window, port wall (62 x 15):\nEthernet, USB-C, JST-GH; louvered door",
        xy=(176, -8),
        xytext=(212, -50),
        fontsize=7.5,
        ha="center",
        color=VENT_C,
        arrowprops={"arrowstyle": "-", "color": VENT_C, "lw": 0.6},
    )
    ax.add_patch(
        Rectangle(
            (ESC_LOUVERS["z"][0], ESC_LOUVERS["y"][0]),
            ESC_LOUVERS["z"][1] - ESC_LOUVERS["z"][0],
            ESC_LOUVERS["y"][1] - ESC_LOUVERS["y"][0],
            fc="none",
            ec=VENT_C,
            lw=1.0,
            ls=":",
        )
    )
    ax.add_patch(
        Rectangle(
            (ALEPH_LOUVERS["z"][0], ALEPH_LOUVERS["y"][0]),
            ALEPH_LOUVERS["z"][1] - ALEPH_LOUVERS["z"][0],
            ALEPH_LOUVERS["y"][1] - ALEPH_LOUVERS["y"][0],
            fc="none",
            ec=VENT_C,
            lw=1.0,
            ls=":",
        )
    )
    ax.text(145, 2.5, "exhaust louvers, starboard wall", fontsize=7, color=VENT_C, ha="center")
    ax.text(67.5, -20.4, "ESC louvers, both walls", fontsize=7, color=VENT_C, ha="center")
    # nose: VTX mount, servo mount, camera, hinge
    ax.add_patch(Rectangle((VTX["z"][0], VTX["y"][0]), 9, VTX["y"][1] - VTX["y"][0], fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(
        Rectangle(
            (SERVO["z"][0], SERVO["y"][0]),
            SERVO["z"][1] - SERVO["z"][0],
            SERVO["y"][1] - SERVO["y"][0],
            fc=NOSE_C,
            ec=INK,
            lw=0.6,
        )
    )
    ax.add_patch(
        Rectangle(
            (CAMERA["z"][0], CAMERA["y"][0]),
            CAMERA["z"][1] - CAMERA["z"][0],
            CAMERA["y"][1] - CAMERA["y"][0],
            fc=NOSE_C,
            ec=INK,
            lw=0.6,
        )
    )
    ax.add_patch(Circle((244.0, -2.28), 2.0, fc="white", ec=INK, lw=0.6))
    ax.text(207, 41.5, "VTX mount\n(new, wider)", fontsize=7, ha="center")
    ax.text(222, 17, "servo mount\n(unchanged)", fontsize=7, ha="center")
    ax.text(243.5, 10, "camera + tilt\n(unchanged)", fontsize=7, ha="center")
    ax.text(-3, -42, "carbon plate\n(unchanged)", fontsize=7, ha="center", va="top")
    # frame and axes
    ax.annotate("", xy=(275, -92), xytext=(-100, -92), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(275, -99, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-100, -62), xytext=(-100, -92), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-97, -64, "y (cover)", fontsize=8)
    for z, lab in [(0, "0"), (ROOF_END, "33"), (97.5, "97.5"), (190, "190"), (214, "214"), (249.3, "249")]:
        ax.plot([z, z], [-89, -85], color=INK, lw=0.6)
        ax.text(z, -95, lab, fontsize=7, ha="center", va="top")
    ax.text(
        -100,
        -58,
        "plate top face z = 0. Hover attitude: nose up, motors at the bottom; y is horizontal in hover.",
        fontsize=7.5,
        ha="left",
    )
    # bay brackets
    for z0, z1, lab, yy in [
        (12, 96, "battery bay (upper deck) / ESC bay (floor deck)", -70),
        (97.5, 189.5, "Aleph bay (upper deck) / wiring tunnel (floor)", -70),
        (190, 256.7, "nose (unchanged parts)", -70),
    ]:
        ax.plot([z0, z1], [yy, yy], color=INK, lw=1.0)
        ax.plot([z0, z0], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.plot([z1, z1], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.text((z0 + z1) / 2, yy - 3.5, lab, fontsize=7.5, ha="center", va="top")
    ax.set_xlim(-105, 280)
    ax.set_ylim(-104, 62)
    ax.axis("off")
    ax.set_title("sprite-aleph: side elevation, port wall removed (mm, assembly frame)", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "side-elevation.png", dpi=170)
    plt.close(fig)


def draw_new_section(ax, with_cover=True):
    outer = rounded_rect(0, 0, W_NEW, H, R_NEW)
    inner = rounded_rect(0, 0, W_NEW - 2 * WALL, H - 2 * WALL, R_NEW - WALL)
    ax.add_patch(Polygon(outer, closed=True, fc=BODY, ec=INK, lw=1.4))
    ax.add_patch(Polygon(inner, closed=True, fc="white", ec=INK, lw=0.8))
    # split line (shell / cover) and tongue-and-groove
    ax.plot([-W_NEW / 2, W_NEW / 2], [12.5, 12.5], color=INK, lw=0.6, ls=":")
    for s in (1, -1):
        x0 = s * (W_NEW / 2 - WALL)
        ax.add_patch(
            Rectangle((min(x0, x0 + s * 1.2), GROOVE_Y[0]), 1.2, GROOVE_Y[1] - GROOVE_Y[0], fc="white", ec=INK, lw=0.6)
        )
        ax.add_patch(
            Rectangle(
                (min(x0, x0 + s * 1.15), GROOVE_Y[0] + 0.05), 1.15, GROOVE_Y[1] - GROOVE_Y[0] - 0.1, fc=INK, ec="none"
            )
        )
    if with_cover:
        ax.plot([0, 0], [-H / 2 - 4, -H / 2 - 1], color=INK, lw=0.5)


def sections():
    fig, axes = plt.subplots(1, 4, figsize=(19, 7.0), gridspec_kw={"width_ratios": [1, 1, 1, 1.35]})
    # (a) original section
    ax = axes[0]
    ax.set_aspect("equal")
    ax.add_patch(Polygon(stadium(0, 0, W_OLD, H), closed=True, fc=BODY, ec=INK, lw=1.4))
    ax.add_patch(Polygon(stadium(0, 0, W_OLD - 4, H - 4), closed=True, fc="white", ec=INK, lw=0.8))
    ax.plot([-23, 23], [-22.5, -22.5], color=INK, lw=0.8)
    for s in (1, -1):
        ax.plot([s * 10.25, s * 10.25], [-22.5, -33.5], color=INK, lw=0.8)
    ax.text(0, -29, "wire\nduct", fontsize=7, ha="center", va="center")
    ax.text(16.5, -29, "cell", fontsize=6.5, ha="center", va="center")
    ax.text(-16.5, -29, "cell", fontsize=6.5, ha="center", va="center")
    ax.plot([-25, 25], [12.5, 12.5], color=INK, lw=0.6, ls=":")
    ax.text(
        0, -5, "46 x 58 clear\n(4S-class pack\nand XT60 mount)", fontsize=8, ha="center", va="center", color="#555555"
    )
    ax.set_title("(a) Sprite today, z = 65\n50 x 75 stadium", fontsize=9)
    # (b) new battery / ESC bay
    ax = axes[1]
    ax.set_aspect("equal")
    draw_new_section(ax)
    ax.add_patch(Polygon(stadium(0, 0, W_OLD, H), closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
    ax.add_patch(
        Rectangle((-19, ESC_TRAY_Y[0]), 38, 2, fc=TRAY_C, ec=INK, lw=0.6)
    )  # flat floor spans |x| < 19 at y = -33.5
    for xc in (-15.25, 15.25):
        ax.add_patch(Rectangle((xc - 2.5, -33.5), 5, 6, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(
        Rectangle(
            (ESC_PCB["x"][0], ESC_PARTS_Y[0]),
            ESC_PCB["x"][1] - ESC_PCB["x"][0],
            ESC_PARTS_Y[1] - ESC_PARTS_Y[0],
            fc=ESC_C,
            alpha=0.25,
            ec="none",
        )
    )
    ax.add_patch(
        Rectangle((ESC_PCB["x"][0], ESC_PCB["y"][0]), ESC_PCB["x"][1] - ESC_PCB["x"][0], 1.6, fc=ESC_C, ec=INK, lw=0.6)
    )
    ax.add_patch(Rectangle((-29, DECK_Y[0]), 58, 2, fc=TRAY_C, ec=INK, lw=0.6))  # cradle glued wall to wall
    ax.add_patch(Rectangle((BATTERY["x"][0], BATTERY["y"][0]), 39, 42, fc=BAT_C, ec=INK, lw=0.8))
    ax.add_patch(Rectangle((BATTERY_ALT["x"][0], BATTERY_ALT["y"][0]), 35, 48, fc="none", ec=INK, lw=0.7, ls="--"))
    ax.text(0, 4, "6S pack\n39 x 42\n(dashed: 35 x 48\nCNHL on its side)", fontsize=7.5, ha="center", va="center")
    ax.text(0, -30.3, "ARK ESC, parts both sides", fontsize=6.5, ha="center", va="center", color=INK)
    for s in (1, -1):
        for yy in np.arange(-32, -22.5, 2.5):
            ax.plot([s * 31.6, s * 28.4], [yy, yy], color=VENT_C, lw=1.6)
    ax.text(0, 29.5, "62 x 75, R20", fontsize=8, ha="center", color="#555555")
    ax.set_title("(b) sprite-aleph, z = 65\nbattery over the ESC", fontsize=9)
    # (c) new Aleph bay
    ax = axes[2]
    ax.set_aspect("equal")
    draw_new_section(ax)
    ax.add_patch(Polygon(stadium(0, 0, W_OLD, H), closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
    ax.add_patch(Rectangle((-29, DECK_Y[0]), 58, 2, fc=TRAY_C, ec=INK, lw=0.6))
    for xl in (-17, 13):  # legs inside the R18 floor corners, from z = 125 on
        ax.add_patch(Rectangle((xl, -35.0), 4, 16.0, fc=TRAY_C, ec=INK, lw=0.5))
    ax.text(0, -27, "tunnel", fontsize=7, ha="center", va="center", color="#555555")
    for xc in (-22.0, 24.5):
        ax.add_patch(Rectangle((xc - 3, DECK_Y[1]), 6, 2.5, fc=TRAY_C, ec=INK, lw=0.5))
        ax.add_patch(Rectangle((xc - 2.5, STACK_Y0 + 1.56), 5, 10, fc="#dddddd", ec=INK, lw=0.5))
    for name, h0, h1, xr in LAYERS:
        ax.add_patch(
            Rectangle(
                (xr[0], STACK_Y0 + h0),
                xr[1] - xr[0],
                h1 - h0,
                fc=ALEPH_C,
                alpha=0.9 if name != "heatsink + fan" else 0.5,
                ec=INK,
                lw=0.6,
            )
        )
    ax.add_patch(Rectangle((-27.5, STACK_Y0 + 1.56), 2.5, 7.33, fc="#dddddd", ec=INK, lw=0.5))  # ix Ethernet overhang
    ax.text(FAN["x"], STACK_Y0 + 31, "heatsink\n+ fan", fontsize=7, ha="center", va="center", color=INK)
    ax.text(1.25, STACK_Y0 + 6.5, "base 88 x 52.5 / carrier / Orin Nano", fontsize=6.5, ha="center", va="center")
    for dx in (-10, 0, 10):
        ax.annotate(
            "",
            xy=(FAN["x"] + dx, STACK_Y0 + 38.6),
            xytext=(FAN["x"] + dx, 35.2),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    for xg in np.arange(-16, 16.1, 4.0):
        ax.plot([xg - 1.2, xg + 1.2], [37.9, 37.9], color=VENT_C, lw=3)
    ax.add_patch(
        Rectangle((-31.6, WINDOW["y"][0]), 3.2, WINDOW["y"][1] - WINDOW["y"][0], fc="white", ec=VENT_C, lw=1.2, ls="--")
    )
    ax.text(-36, -8.5, "service\nwindow", fontsize=7, ha="right", va="center", color=VENT_C)
    for yy in np.arange(-11, 0.1, 3.0):
        ax.plot([31.6, 28.4], [yy, yy], color=VENT_C, lw=1.6)
    ax.text(36, -5.5, "exhaust\nlouvers", fontsize=7, ha="left", va="center", color=VENT_C)
    ax.set_title("(c) sprite-aleph, z = 143\nAleph stack, fan under the cover grille", fontsize=9)
    for ax in axes[:3]:
        ax.set_xlim(-46, 46)
        ax.set_ylim(-46, 46)
        ax.axis("off")
    # (d) prop clearance plan at the prop plane
    ax = axes[3]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=9, solid_capstyle="round", zorder=0)
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        mx, my = sx * MOTOR_XY, sy * MOTOR_XY
        ax.add_patch(Circle((mx, my), PROP_R["4 in"], fc="none", ec=INK, lw=0.9))
        ax.add_patch(Circle((mx, my), PROP_R["5 in"], fc="none", ec=OLD, lw=0.7, ls=":"))
        ax.add_patch(Circle((mx, my), 9, fc="#555555", ec="none"))
    ax.add_patch(Polygon(stadium(0, 0, W_OLD, H), closed=True, fc="none", ec=OLD, lw=1.0, ls="--"))
    ax.add_patch(Polygon(rounded_rect(0, 0, W_NEW, H, R_NEW), closed=True, fc=BODY, ec=INK, lw=1.4))
    # nearest point of the new section to the +x+y motor: on the R20 corner arc, along the line to the arc centre
    cx, cy = W_NEW / 2 - R_NEW, H / 2 - R_NEW
    d = np.hypot(MOTOR_XY - cx, MOTOR_XY - cy)
    px, py = cx + R_NEW * (MOTOR_XY - cx) / d, cy + R_NEW * (MOTOR_XY - cy) / d
    tip4 = (MOTOR_XY - PROP_R["4 in"] * (MOTOR_XY - cx) / d, MOTOR_XY - PROP_R["4 in"] * (MOTOR_XY - cy) / d)
    ax.plot([px, tip4[0]], [py, tip4[1]], color=ESC_C, lw=1.6, zorder=5)
    ax.text(
        48,
        0,
        f"{d - R_NEW - PROP_R['4 in']:.0f} mm to a 4 in prop\n{d - R_NEW - PROP_R['5 in']:.0f} mm to a 5 in (dotted)",
        fontsize=7.5,
        color=ESC_C,
        ha="left",
        va="center",
    )
    ax.text(
        0,
        -138,
        "Sprite section dashed; 4 in props solid, 5 in dotted.\nSprite today clears a 4 in prop by 29 mm, a 5 in by 16 mm.",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    ax.set_xlim(-150, 150)
    ax.set_ylim(-160, 145)
    ax.axis("off")
    ax.set_title("(d) prop plane, looking down the fuselage\nmotors at (+-80, +-80)", fontsize=9)
    fig.suptitle("sprite-aleph cross-sections (x across, y toward the cover; mm)", fontsize=11, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "sections.png", dpi=170)
    plt.close(fig)


def plan_view():
    fig, ax = plt.subplots(figsize=(16, 6.2))
    ax.set_aspect("equal")
    # body outline (new) with flare and blend; original dashed
    zs_flare = np.linspace(FLARE[0], FLARE[1], 12)
    hw_flare = 25 + (31 - 25) * (1 - np.cos(np.pi * (zs_flare - FLARE[0]) / (FLARE[1] - FLARE[0]))) / 2
    zs_blend = np.linspace(BLEND[0], BLEND[1], 12)
    hw_end = interp(NOSE_HALF_WIDTH, BLEND[1])
    hw_blend = 31 + (hw_end - 31) * (1 - np.cos(np.pi * (zs_blend - BLEND[0]) / (BLEND[1] - BLEND[0]))) / 2
    nose = [(z, w) for z, w in NOSE_HALF_WIDTH if z > BLEND[1]] + [(249.3, 13.1)]
    top = list(zip(zs_flare, hw_flare)) + [(BLEND[0], 31)] + list(zip(zs_blend, hw_blend)) + nose
    outline = top + [(z, -w) for z, w in reversed(top)]
    ax.add_patch(Polygon(outline, closed=True, fc=BODY, ec=INK, lw=1.4))
    old = [(2, 25), (200.5, 25)] + [(z, w) for z, w in NOSE_HALF_WIDTH if z > 200.5]
    old_outline = old + [(z, -w) for z, w in reversed(old)]
    ax.add_patch(Polygon(old_outline, closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
    ax.add_patch(Rectangle((2, -31), ROOF_END - 2, 62, fc="none", ec=INK, hatch="////", lw=0))
    ax.text(17.5, 36, "roof lip", fontsize=7.5, ha="center")
    ax.text(16, -40, "flare 50 -> 62\nover z 2..30", fontsize=7, ha="center", va="top")
    ax.text(214, -44, "blend 62 -> Sprite nose\nover z 195..214", fontsize=7, ha="center", va="top")
    # tail cone cavity (under the plate) and plate slot
    ax.add_patch(Rectangle((-30, -25), 24, 50, fc="none", ec=OLD, lw=0.8, ls="--"))
    ax.text(-18, 0, "tail cone\nbay (free)", fontsize=7, ha="center", va="center", color="#555555")
    ax.add_patch(Rectangle((-6, -13.25), 6, 26.5, fc="white", ec=INK, lw=0.6))
    ax.text(-3, -18, "plate\nwire slot", fontsize=6, ha="center", va="top")
    # ESC (under the battery deck: dashed), housings, plugs
    ax.add_patch(
        Rectangle(
            (ESC_PCB["z"][0], ESC_PCB["x"][0]),
            ESC_PCB["z"][1] - ESC_PCB["z"][0],
            ESC_PCB["x"][1] - ESC_PCB["x"][0],
            fc=ESC_C,
            alpha=0.18,
            ec=ESC_C,
            lw=0.9,
            ls="--",
        )
    )
    for z0, z1 in ESC_HOUSING:
        for x0, x1 in MR30_X:
            ax.add_patch(Rectangle((z0, x0), z1 - z0, x1 - x0, fc=ESC_C, alpha=0.5, ec=ESC_C, lw=0.6))
    for z0, z1 in ESC_PLUGS:
        for x0, x1 in MR30_X:
            ax.add_patch(Rectangle((z0, x0 + 3), z1 - z0, x1 - x0 - 6, fc="none", ec=ESC_C, lw=0.8, ls="--"))
    for zc in (50.3, 80.8):
        for xc in (-15.25, 15.25):
            ax.add_patch(Circle((zc, xc), 1.75, fc="white", ec=ESC_C, lw=0.8))
    for zc in (59.6, 71.6):
        ax.add_patch(Circle((zc, -20.0), 2.55, fc="#f2c14e", ec=INK, lw=0.6))
    ax.text(
        65.6,
        -47,
        "ESC on the floor deck (dashed, under the pack):\n30.5 pattern, battery studs at port edge (yellow)",
        fontsize=7.5,
        ha="center",
        color=ESC_C,
    )
    # battery on the upper deck
    ax.add_patch(
        Rectangle(
            (BATTERY["z"][0], BATTERY["x"][0]),
            BATTERY["z"][1] - BATTERY["z"][0],
            39,
            fc=BAT_C,
            alpha=0.85,
            ec=INK,
            lw=0.8,
        )
    )
    ax.text(53, 0, "6S pack 78 x 39\n(upper deck)", fontsize=8, ha="center", va="center")
    for zs in (60, 86):
        ax.add_patch(Rectangle((zs - 1, -25), 2, 50, fc=INK, ec="none"))
    ax.add_patch(Rectangle((97.5, -27), 6.5, 16, fc="#f2c14e", ec=INK, lw=0.6))
    ax.text(100.7, -31, "XT60", fontsize=6.5, ha="center", va="top")
    # Aleph tray and stack footprint
    ax.add_patch(
        Rectangle((ALEPH_TRAY_Z[0], -29), ALEPH_TRAY_Z[1] - ALEPH_TRAY_Z[0], 58, fc=TRAY_C, alpha=0.35, ec=INK, lw=0.6)
    )
    ax.add_patch(Rectangle((BASE_Z[0], BASE_X[0]), 88, 52.5, fc=ALEPH_C, alpha=0.35, ec=INK, lw=0.8))
    for dz in (3.0, 85.0):
        for dx in (3.0, 49.5):
            ax.add_patch(Circle((BASE_Z[0] + dz, BASE_X[0] + dx), 1.45, fc="white", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((HEATSINK_Z[0], FAN["x"] - 20.0), 61, 40, fc=ALEPH_C, alpha=0.55, ec=INK, lw=0.8))
    ax.add_patch(Circle((FAN["z"], FAN["x"]), FAN["d"] / 2, fc="none", ec=INK, lw=0.8))
    ax.add_patch(Circle((FAN["z"], FAN["x"]), FAN["d"] / 2 + 2, fc="none", ec=VENT_C, lw=1.2, ls="--"))
    ax.text(FAN["z"], FAN["x"], "fan\n(grille above)", fontsize=7, ha="center", va="center", color="white")
    ax.text(
        142.5,
        40,
        "Aleph stack: base 88 x 52.5 with 82 x 46.5 M2.5 holes on the tray;\nservice edge (Ethernet, USB-C, JST-GH) faces the port wall",
        fontsize=7.5,
        ha="center",
        va="bottom",
    )
    # base board edge connectors on the port (service) edge
    for z0, z1, lab in [(116.1, 126.9, "ETH"), (130.2, 162.7, "JST-GH"), (164.7, 173.7, "USB-C")]:
        ax.add_patch(Rectangle((z0, -27.5), z1 - z0, 2.5, fc="#dddddd", ec=INK, lw=0.5))
        ax.text((z0 + z1) / 2, -25.0, lab, fontsize=5.5, ha="center", va="bottom")
    ax.add_patch(
        Rectangle((WINDOW["z"][0], -31.6), WINDOW["z"][1] - WINDOW["z"][0], 3.2, fc="white", ec=VENT_C, lw=1.2, ls="--")
    )
    ax.text(145, -35.5, "service window / louvered door (port wall)", fontsize=7, ha="center", va="top", color=VENT_C)
    ax.add_patch(
        Rectangle(
            (ALEPH_LOUVERS["z"][0], 28.4),
            ALEPH_LOUVERS["z"][1] - ALEPH_LOUVERS["z"][0],
            3.2,
            fc="none",
            ec=VENT_C,
            lw=1.0,
            ls=":",
        )
    )
    ax.text(145, 33.5, "exhaust louvers (starboard wall)", fontsize=7, ha="center", va="bottom", color=VENT_C)
    for s in (1, -1):
        ax.add_patch(
            Rectangle(
                (ESC_LOUVERS["z"][0], s * 30 - 1.6),
                ESC_LOUVERS["z"][1] - ESC_LOUVERS["z"][0],
                3.2,
                fc="none",
                ec=VENT_C,
                lw=1.0,
                ls=":",
            )
        )
    ax.text(67.5, 33.5, "ESC louvers (both walls)", fontsize=7, ha="center", va="bottom", color=VENT_C)
    # nose parts
    ax.add_patch(Rectangle((VTX["z"][0], VTX["x"][0]), 9, 56, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(
        Rectangle((SERVO["z"][0], SERVO["x"][0]), SERVO["z"][1] - SERVO["z"][0], 37, fc=NOSE_C, ec=INK, lw=0.6)
    )
    ax.add_patch(Rectangle((CAMERA["z"][0], CAMERA["x"][0]), 19, 20, fc=NOSE_C, ec=INK, lw=0.6))
    for s in (1, -1):
        ax.add_patch(Rectangle((234, s * 13 - 3), 16, 6, fc=NOSE_C, ec=INK, lw=0.5))
    ax.text(194.5, 31.5, "VTX mount", fontsize=7, ha="center", va="bottom")
    ax.text(222, -24, "servo", fontsize=7, ha="center", va="top")
    ax.text(243.5, -18, "camera", fontsize=7, ha="center", va="top")
    # axes and stations
    ax.annotate("", xy=(275, -62), xytext=(-40, -62), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(275, -68, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-40, -37), xytext=(-40, -62), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-37, -39, "x (starboard)", fontsize=8)
    for z, lab in [(0, "0"), (ROOF_END, "33"), (97.5, "97.5"), (190, "190"), (214, "214"), (249.3, "249")]:
        ax.plot([z, z], [-58, -55], color=INK, lw=0.6)
        ax.text(z, -60, lab, fontsize=7, ha="center", va="top")
    ax.set_xlim(-45, 280)
    ax.set_ylim(-72, 52)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph: plan view with the cover removed (mm, assembly frame; Sprite body dashed)",
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
