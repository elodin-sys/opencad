"""Figures for the sprite-aleph design proposal, iteration 3.1. Run from the repo root:
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

# ---- new body section: 60 x 75, straight sides for |y| <= 23.4, facets to a 35-wide crown and keel ----
HW, HH = 30.0, 37.5
SIDE_Y, CROWN_X = 23.4, 17.6
WALL = 2.0
INNER = {"hw": 28.0, "hh": 35.5, "side_y": 22.6, "crown_x": 16.4}
ROOF_END = 33.0
WALL_END = 198.0  # side walls run to z = 198 (Sprite 170.16) so the Aleph's forward bosses sit on a wall
SPLIT_Y = 22.0  # shell / cover split, inside the straight band; the groove sits at y 13..17
GROOVE_Y = (13.0, 17.0)
FLARE = (2.0, 10.0)  # cosine, steepest 45 deg printed standing; the full section by the pack's z 7
BLEND = (198.0, 214.0)  # width and height into the Sprite nose section
VTX_Z = (200.0, 209.0)
INNER_FLOOR_Y = -22.5
FLOOR_END_Z = 88.0

# battery bay and alcove
BATTERY = {"z": (7.0, 85.0), "y": (-22.5, 16.5), "x": (-21.0, 21.0)}  # reference Tattu V5 1400 flat: 78 x 42 x 39
BAT_ENV = {"z": (7.0, 88.0), "y": (-22.5, 19.5), "x": (-24.0, 24.0)}
POCKET_Z = (6.0, 88.0)
ALCOVE_Z = (90.0, 106.0)
XT60 = {"x": (-22.0, -6.0), "z": (91.0, 99.0), "y": (-12.0, 12.0)}
REGULATOR = {"x": (-15.9, 15.9), "y": (22.0, 33.0), "z": (40.0, 83.2)}  # optional Pololu D42V110F18, on the cover
MOLEX_PLUG = {"x": (9.8, 16.9), "y": (9.4, 18.1), "z": (92.0, 106.2)}

# Aleph on edge, base against the starboard wall on bosses; board plane x = 18.5. The stack is right-handed: service edge up
# and power end aft put its heatsink to port. asm (x, y, z) = (18.5 - sz, 24.75 - sy, 195.5 - sx) from the aleph-stack frame
XP = 18.5
BOARD_Y = (-27.75, 24.75)
BOARD_Z = (107.5, 195.5)
HOLES_Y = (-24.75, 21.75)
HOLES_Z = (110.5, 192.5)
BOSS_LEN = {HOLES_Y[0]: 7.6, HOLES_Y[1]: 9.5}
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
SODIMM = {"y": (-26.25, -21.25), "z": (113.4, 189.6)}
MODULE = {"y": (-21.25, 23.75), "z": (116.7, 186.3)}
HS_CENTER = {"y": 3.56, "z": 151.5}
HEATSINK = {"y": (-15.4, 22.6), "z": (122.5, 180.5)}
LID = {"y": (-6.5, 13.7), "z": (140.4, 162.6)}
FAN_D = 38.0
GRILLE = {"z": (121.0, 182.0), "y": (-16.0, 18.0)}
LOUVERS = [{"z": (109.0, 120.0), "y": (-14.0, 18.0)}, {"z": (183.0, 194.0), "y": (-14.0, 18.0)}]
ETH = {"x": (XP - 8.89, XP - 1.56), "y": (13.9, 27.25), "z": (167.1, 177.9)}
USBC_BASE = {"x": (XP - 6.5, XP - 1.56), "y": (17.0, 24.75), "z": (120.3, 129.3)}
JSTGH = {"x": (XP - 7.54, XP - 1.56), "y": (19.5, 24.4), "z": (131.5, 163.8)}

# tail: Sprite cone kept; ESC along y on 12 mm spacers on the M3 x 30 clamp screws
ESC_PCB_Z = (-20.6, -19.0)
ESC_HOUSING_Z = (-25.5, -18.6)
ESC_LONG = 31.58  # along y
ESC_X = (-22.75, 19.5)  # PCB across, hole pattern centred on the axis
MR30_Y = (31.58, 38.31)
PLUG_Y = (38.31, 46.5)
MR30_X = [(4.05, 19.58), (-19.58, -4.05)]
SLOT = {"z": (-27.0, -17.0), "x": (-22.5, 22.5)}
SPACER = 12.0
MOTOR_XY = 80.0
PROP_R = {"5 in": 63.5}

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


def faceted(hw, hh, side_y, crown_x):
    """Closed outline of the new section: straight sides, corner facets, flat crown and keel."""
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
    pts = sorted(profile)
    zs, vs = zip(*pts)
    return float(np.interp(z, zs, vs))


def blended(profile, v0):
    """Cosine blend from the body value v0 at BLEND[0] to the Sprite profile at BLEND[1], then the Sprite stations."""
    zs = np.linspace(BLEND[0], BLEND[1], 12)
    v1 = interp(profile, BLEND[1])
    vs = v0 + (v1 - v0) * (1 - np.cos(np.pi * (zs - BLEND[0]) / (BLEND[1] - BLEND[0]))) / 2
    return list(zip(zs, vs)) + [(z, v) for z, v in profile if z > BLEND[1]]


def side_elevation():
    fig, ax = plt.subplots(figsize=(17, 7.6))
    ax.set_aspect("equal")
    # plate, floor, Sprite tail cone, rear mount plate and side lands
    ax.add_patch(Rectangle((-6, -37.5), 6, 75, fc="#3b3b3b", ec="none"))
    ax.add_patch(Rectangle((-6, -13.5), 6, 27.0, fc="white", ec="none"))
    ax.add_patch(Rectangle((0, -37.5), 2, 75, fc=BODY, ec=INK, lw=0.8))
    cone = [(z, y) for z, y in CONE_Y] + [(z, -y) for z, y in reversed(CONE_Y)]
    ax.add_patch(Polygon(cone, closed=True, fc="none", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-7.2, -36.6), 1.2, 73.2, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((-13.3, 25.5), 7.3, 10.9, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(Rectangle((-13.3, -36.3), 7.3, 6.7, fc=TRAY_C, ec=INK, lw=0.5))
    # ESC along y: PCB, MR30 housings, plugs through the cone, spacers and nuts on the clamp screws
    for yc in (15, -15):
        ax.add_patch(Rectangle((-7.2 - SPACER, yc - 2.5), SPACER, 5, fc="#dddddd", ec=INK, lw=0.5))
        ax.add_patch(Rectangle((ESC_PCB_Z[0] - 2.4, yc - 2.75), 2.4, 5.5, fc="#bbbbbb", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((ESC_PCB_Z[0], -ESC_LONG), 1.6, 2 * ESC_LONG, fc=ESC_C, ec=INK, lw=0.6))
    for s in (1, -1):
        ax.add_patch(
            Rectangle((ESC_HOUSING_Z[0], min(s * MR30_Y[0], s * MR30_Y[1])), 6.9, 6.73, fc=ESC_C, ec=INK, lw=0.6)
        )
        ax.add_patch(
            Rectangle(
                (ESC_HOUSING_Z[0] + 0.5, min(s * PLUG_Y[0], s * PLUG_Y[1])),
                5.9,
                8.19,
                fc="none",
                ec=ESC_C,
                lw=0.9,
                ls="--",
            )
        )
        ax.plot([SLOT["z"][0], SLOT["z"][1]], [s * 36.5, s * 36.5], color="white", lw=2.5)
        ax.plot([SLOT["z"][0], SLOT["z"][1]], [s * 36.5, s * 36.5], color=VENT_C, lw=1.0, ls="--")
    ax.text(
        -44,
        8,
        "ESC along the cone's\nlong axis, 12 mm spacers\non the M3 clamp screws",
        fontsize=7,
        ha="center",
        va="center",
    )
    ax.annotate(
        "MR30s and plugs out through\ntwo 45 x 10 slots in the cone",
        xy=(-22, 44),
        xytext=(-52, 60),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    ax.text(
        -62,
        -44,
        "Sprite tail cone,\nrear mount ring cut at z -13,\nlaunch pad unchanged",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    # fuselage outline: flare (side view unchanged), roof, wall top, nose
    bottom = [(2, -37.5)] + blended(NOSE_BOTTOM, -37.5)
    ax.plot(*zip(*bottom), color=INK, lw=1.4)
    ax.plot([2, ROOF_END], [37.5, 37.5], color=INK, lw=1.4)
    ax.plot([ROOF_END, ROOF_END], [37.5, SPLIT_Y], color=INK, lw=1.0)
    ax.plot([ROOF_END, WALL_END], [SPLIT_Y, SPLIT_Y], color=INK, lw=1.0)
    ax.plot([WALL_END, WALL_END], [SPLIT_Y, 0], color=INK, lw=1.0)
    ax.plot([WALL_END, TIP_Z], [0, 0], color=INK, lw=0.8, ls=":")
    ax.plot([TIP_Z, TIP_Z], [0, -22.9], color=INK, lw=1.4)
    cover = (
        [(ROOF_END, 37.5)]
        + blended(COVER_TOP, 37.5)
        + [(COVER_TIP_Z, 0), (WALL_END, 0), (WALL_END, SPLIT_Y), (ROOF_END, SPLIT_Y)]
    )
    ax.add_patch(Polygon(cover, closed=True, fc="none", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((2, SPLIT_Y), ROOF_END - 2, 37.5 - SPLIT_Y, fc="none", ec=INK, hatch="////", lw=0))
    ax.text(15, 41, "roof lip\n(battery pocket)", fontsize=7.5, ha="center", va="bottom")
    ax.text(
        98,
        41.5,
        "top cover: 60 wide, Sprite length (224); flanks 22 deep, tongue at y 13..17",
        fontsize=7.5,
        ha="center",
        va="bottom",
    )
    ax.plot([30, WALL_END - 2], [GROOVE_Y[0]] * 2, color=OLD, lw=0.6)
    ax.plot([30, WALL_END - 2], [GROOVE_Y[1]] * 2, color=OLD, lw=0.6)
    ax.add_patch(
        Rectangle(
            (REGULATOR["z"][0], REGULATOR["y"][0]),
            REGULATOR["z"][1] - REGULATOR["z"][0],
            REGULATOR["y"][1] - REGULATOR["y"][0],
            fc="none",
            ec=INK,
            lw=0.8,
            ls="--",
        )
    )
    ax.text(61.6, 27.5, "optional 18 V regulator\non the cover", fontsize=6.5, ha="center", va="center")
    # internal floor, duct cable path, battery, alcove
    ax.add_patch(Rectangle((2, INNER_FLOOR_Y - 1), FLOOR_END_Z - 2, 1, fc=BODY, ec=INK, lw=0.6))
    ax.plot([-8, -8, 5, 5, 92, 92], [-16, -29, -29, -29, -29, -12], color="#f2c14e", lw=1.8)
    ax.text(
        45,
        -30.5,
        "wire duct: ESC power and signal leads up through the plate hole",
        fontsize=7,
        ha="center",
        va="top",
        color="#8a6d1c",
    )
    ax.add_patch(
        Rectangle((BATTERY["z"][0], BATTERY["y"][0]), 78, BATTERY["y"][1] - BATTERY["y"][0], fc=BAT_C, ec=INK, lw=0.8)
    )
    ax.add_patch(
        Rectangle(
            (BAT_ENV["z"][0], BAT_ENV["y"][0]),
            BAT_ENV["z"][1] - BAT_ENV["z"][0],
            BAT_ENV["y"][1] - BAT_ENV["y"][0],
            fc="none",
            ec=INK,
            lw=0.8,
            ls="--",
        )
    )
    ax.text(
        46,
        -3,
        "6S pack envelope 81 x 48 x 42, flat (dashed);\nTattu R-Line V5 1400 shown (78 x 42 x 39),\n26 mm under the roof lip",
        fontsize=8,
        ha="center",
        va="center",
    )
    for zs in (40, 70):
        ax.plot([zs, zs], [-23.5, 17.5], color=INK, lw=1.2)
    ax.add_patch(Rectangle((FLOOR_END_Z, -22.5), 2, 32, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((XT60["z"][0], XT60["y"][0]), 8, 24, fc="#f2c14e", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((MOLEX_PLUG["z"][0], MOLEX_PLUG["y"][0]), 14.2, 8.7, fc="#dddddd", ec=INK, lw=0.6))
    ax.annotate(
        "connector alcove z 90..106 (16 mm):\nXT60 socket for the pack lead,\nthe Aleph's 6S plug on its tail edge",
        xy=(98, 14),
        xytext=(96, -52),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    # Aleph: base board face, connectors on the top edge, module, heatsink, fan, screws from outside
    ax.add_patch(Rectangle((BOARD_Z[0], BOARD_Y[0]), 88, 52.5, fc=ALEPH_C, alpha=0.35, ec=INK, lw=0.8))
    ax.add_patch(Rectangle((MODULE["z"][0], MODULE["y"][0]), 69.6, 45, fc="none", ec=INK, lw=0.6, ls=":"))
    ax.add_patch(Rectangle((HEATSINK["z"][0], HEATSINK["y"][0]), 58, 38, fc=HS_C, alpha=0.25, ec=HS_C, lw=1.0, ls="--"))
    ax.add_patch(Circle((HS_CENTER["z"], HS_CENTER["y"]), FAN_D / 2, fc="none", ec=HS_C, lw=0.8, ls="--"))
    for zc in HOLES_Z:
        for yc in HOLES_Y:
            ax.add_patch(Circle((zc, yc), 2.2, fc="#dddddd", ec=INK, lw=0.8))
            ax.plot([zc - 1.3, zc + 1.3], [yc, yc], color=INK, lw=0.8)
    ax.annotate(
        "four M2.5 screws from outside through the\nstarboard wall and its bosses into the stack's standoffs",
        xy=(HOLES_Z[0], HOLES_Y[1]),
        xytext=(126, -62),
        fontsize=7.5,
        ha="center",
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.6},
    )
    for c, lab in ((ETH, "ETH"), (USBC_BASE, "USB-C"), (JSTGH, "JST-GH")):
        ax.add_patch(
            Rectangle(
                (c["z"][0], c["y"][0]), c["z"][1] - c["z"][0], c["y"][1] - c["y"][0], fc="#dddddd", ec=INK, lw=0.5
            )
        )
        ax.text((c["z"][0] + c["z"][1]) / 2, c["y"][1] + 1, lab, fontsize=6, ha="center", va="bottom")
    ax.text(
        151.5,
        51,
        "Aleph on edge, flush: base against the starboard wall (5 mm plenum on the fan side),\nservice edge up, heatsink inside behind a grille in the port wall",
        fontsize=8,
        ha="center",
        va="bottom",
    )
    ax.add_patch(
        Rectangle(
            (GRILLE["z"][0], GRILLE["y"][0]), 61, GRILLE["y"][1] - GRILLE["y"][0], fc="none", ec=VENT_C, lw=1.2, ls="--"
        )
    )
    for zg in np.arange(GRILLE["z"][0] + 3, GRILLE["z"][1], 4.0):
        ax.plot([zg, zg], [GRILLE["y"][0] + 1, GRILLE["y"][1] - 1], color=VENT_C, lw=0.5, alpha=0.6)
    ax.annotate(
        "fan grille in the port wall\n61 x 34 over the heatsink (removed wall)",
        xy=(182, 10),
        xytext=(218, -52),
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
    ax.text(151.5, -33.5, "fin exhaust louvers fore and aft (port)", fontsize=7, ha="center", va="top", color=VENT_C)
    # nose: VTX mount moved forward into the blend; servo and camera mounts at their Sprite stations
    ax.add_patch(Rectangle((VTX_Z[0], -22), VTX_Z[1] - VTX_Z[0], 53, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((214.8, -30.6), 14.3, 44.4, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((234, -12), 19, 19, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Circle((244.0, -2.28), 2.0, fc="white", ec=INK, lw=0.6))
    ax.text(204.5, 39, "VTX mount\nz 200..209\n(re-derived)", fontsize=7, ha="center", va="bottom")
    ax.text(222, 17, "servo mount\n(unchanged)", fontsize=7, ha="center")
    ax.text(250, 16, "camera + tilt\n(unchanged)", fontsize=7, ha="center")
    ax.text(-3, -42, "carbon plate\n(unchanged)", fontsize=7, ha="center", va="top")
    # axes, stations, bays
    ax.annotate("", xy=(295, -96), xytext=(-100, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(295, -103, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-100, -66), xytext=(-100, -96), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-97, -68, "y (cover)", fontsize=8)
    for z, lab in [
        (-20, "-20"),
        (0, "0"),
        (ROOF_END, "33"),
        (FLOOR_END_Z, "88"),
        (106, "106"),
        (WALL_END, "198"),
        (BLEND[1], "214"),
        (TIP_Z, "249.3"),
    ]:
        ax.plot([z, z], [-93, -89], color=INK, lw=0.6)
        ax.text(z, -99, lab, fontsize=7, ha="center", va="top")
    for z0, z1, lab in [
        (-30, -6, "ESC"),
        (POCKET_Z[0], POCKET_Z[1], "battery bay"),
        (ALCOVE_Z[0], ALCOVE_Z[1], ""),
        (106, WALL_END, "Aleph bay"),
        (VTX_Z[0], COVER_TIP_Z, "nose: Sprite parts"),
    ]:
        yy = -74
        ax.plot([z0, z1], [yy, yy], color=INK, lw=1.0)
        ax.plot([z0, z0], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.plot([z1, z1], [yy - 1.5, yy + 1.5], color=INK, lw=1.0)
        ax.text((z0 + z1) / 2, yy - 3.5, lab, fontsize=7.5, ha="center", va="top")
    ax.text(
        -100,
        -63,
        "plate top face z = 0. Body 60 x 75 faceted, Sprite length (shell 249.3 tall, fits a Bambu X1C). Hover: nose up.",
        fontsize=7.5,
        ha="left",
    )
    ax.set_xlim(-105, 300)
    ax.set_ylim(-108, 70)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph, iteration 3.1: side elevation, port wall removed (mm, assembly frame)", fontsize=11, loc="left"
    )
    fig.tight_layout()
    fig.savefig(OUT / "side-elevation.png", dpi=170)
    plt.close(fig)


def draw_section(ax):
    ax.add_patch(Polygon(faceted(HW, HH, SIDE_Y, CROWN_X), closed=True, fc=BODY, ec=INK, lw=1.4))
    ax.add_patch(Polygon(faceted(**INNER), closed=True, fc="white", ec=INK, lw=0.8))
    ax.add_patch(Polygon(stadium(0, 0, 50, 75), closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
    ax.plot([-HW, HW], [SPLIT_Y, SPLIT_Y], color=INK, lw=0.6, ls=":")
    for s in (1, -1):
        x0 = s * INNER["hw"]
        ax.add_patch(Rectangle((min(x0, x0 + s * 1.2), GROOVE_Y[0]), 1.2, 4.0, fc="white", ec=INK, lw=0.6))
        ax.add_patch(Rectangle((min(x0, x0 + s * 1.15), GROOVE_Y[0] + 0.05), 1.15, 3.9, fc=INK, ec="none"))


def inner_x_at(y):
    y = abs(y)
    if y <= INNER["side_y"]:
        return INNER["hw"]
    return INNER["hw"] - (y - INNER["side_y"]) / (INNER["hh"] - INNER["side_y"]) * (INNER["hw"] - INNER["crown_x"])


def sections():
    fig, axes = plt.subplots(1, 4, figsize=(21, 7.8), gridspec_kw={"width_ratios": [1.1, 1.1, 1.5, 1.3]})
    # (a) battery bay
    ax = axes[0]
    ax.set_aspect("equal")
    draw_section(ax)
    ax.add_patch(
        Rectangle(
            (-inner_x_at(INNER_FLOOR_Y) + 0.1, INNER_FLOOR_Y - 1),
            2 * inner_x_at(INNER_FLOOR_Y) - 0.2,
            1,
            fc=BODY,
            ec=INK,
            lw=0.6,
        )
    )
    for s in (1, -1):
        ax.plot([s * 11, s * 11], [INNER_FLOOR_Y, -34.0], color=INK, lw=0.8)
    ax.text(0, -30, "duct:\n2 x 10 AWG\n+ 8-pin", fontsize=6.5, ha="center", va="center", color="#8a6d1c")
    for s in (1, -1):
        ax.add_patch(Rectangle((24 if s > 0 else -26, INNER_FLOOR_Y), 2, 10, fc=TRAY_C, ec=INK, lw=0.5))
    ax.add_patch(Rectangle((-21, INNER_FLOOR_Y), 42, 39, fc=BAT_C, ec=INK, lw=0.8))
    ax.text(
        0,
        -3,
        "V5 1400 flat\n42 wide, 39 tall;\nenvelope 48 x 42\n(dashed)",
        fontsize=7.5,
        ha="center",
        va="center",
    )
    ax.plot([-24, -24, 24, 24], [-22.5, 19.5, 19.5, -22.5], color=INK, lw=1.0, ls="--")
    ax.add_patch(
        Rectangle(
            (REGULATOR["x"][0], REGULATOR["y"][0]),
            REGULATOR["x"][1] - REGULATOR["x"][0],
            REGULATOR["y"][1] - REGULATOR["y"][0],
            fc="none",
            ec=INK,
            lw=0.8,
            ls="--",
        )
    )
    ax.text(0, 27.5, "regulator (optional)", fontsize=6.5, ha="center", va="center")
    ax.text(0, 39.5, "60 x 75, faceted corners", fontsize=7.5, ha="center", color="#555555")
    ax.set_title("(a) battery bay, z = 60\nSprite section dashed", fontsize=9)
    # (b) Aleph bay
    ax = axes[1]
    ax.set_aspect("equal")
    draw_section(ax)
    # grille window through the port wall
    ax.add_patch(Rectangle((-HW - 0.4, GRILLE["y"][0]), 3.0, GRILLE["y"][1] - GRILLE["y"][0], fc="white", ec="none"))
    for yy in np.arange(GRILLE["y"][0] + 2, GRILLE["y"][1], 4.0):
        ax.plot([-HW - 0.2, -INNER["hw"] + 0.2], [yy, yy], color=VENT_C, lw=1.4)
    # bosses from the starboard wall to the board plane, screws from outside
    for yc in HOLES_Y:
        xw = inner_x_at(yc)
        ax.add_patch(Rectangle((XP, yc - 3.5), xw - XP, 7, fc=TRAY_C, ec=INK, lw=0.6))
        ax.plot([xw + 3.0, XP - 1.56 - 6], [yc, yc], color=INK, lw=1.4)
        ax.add_patch(Rectangle((xw + 2.6, yc - 2.2), 1.6, 4.4, fc=INK, ec="none"))
    ax.add_patch(Rectangle((LAYERS_X["parts"][0], BOARD_Y[0] + 2), 1.97, 48.5, fc=ALEPH_C, alpha=0.3, ec="none"))
    ax.add_patch(Rectangle((LAYERS_X["base"][0], BOARD_Y[0]), 1.56, 52.5, fc=ALEPH_C, ec=INK, lw=0.6))
    for yc in HOLES_Y:
        ax.add_patch(Rectangle((LAYERS_X["standoff"][0], yc - 2.5), 10, 5, fc="#dddddd", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["carrier"][0], BOARD_Y[0]), 1.57, 52.5, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LAYERS_X["sodimm"][0], SODIMM["y"][0]), 10.86, 5, fc="#bbbbbb", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["module"][0], MODULE["y"][0]), 1.2, 45, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LAYERS_X["lid"][0], LID["y"][0]), 2.63, 20.2, fc="#555555", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((LAYERS_X["heatsink"][0], HEATSINK["y"][0]), 18, 38, fc=HS_C, alpha=0.6, ec=INK, lw=0.8))
    for yy in np.arange(-13, 21, 3.3):
        ax.plot([LAYERS_X["heatsink"][1] - 9.5, LAYERS_X["heatsink"][1] - 0.5], [yy, yy], color="white", lw=0.6)
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
    ax.text(13, 29.5, "ETH / USB-C / JST-GH up", fontsize=6.5, ha="center", va="bottom")
    for dy in (-11, 0, 11):
        ax.annotate(
            "",
            xy=(LAYERS_X["heatsink"][0] - 0.5, HS_CENTER["y"] + dy),
            xytext=(-HW - 9, HS_CENTER["y"] + dy),
            arrowprops={"arrowstyle": "->", "color": VENT_C, "lw": 1.0},
        )
    ax.text(-HW - 10, HS_CENTER["y"] + 21, "outside air\nthrough the grille", fontsize=7, ha="center", color=VENT_C)
    ax.text(36.5, 0, "M2.5 screws\nfrom outside", fontsize=6.5, ha="center", va="center")
    ax.text(-25.5, -24, "5 mm\nplenum", fontsize=6.5, ha="center", va="center", color=HS_C)
    ax.set_title("(b) Aleph bay, z = 151\nflush against the starboard wall on bosses", fontsize=9)
    for ax in axes[:2]:
        ax.set_xlim(-47, 47)
        ax.set_ylim(-47, 47)
        ax.axis("off")
    # (c) tail from below at z = -22: Sprite cavity, ESC along y, connectors out through the +-y walls
    ax = axes[2]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=11, solid_capstyle="round", zorder=0)
    ax.add_patch(Polygon(stadium(0, 0, 57.2, 74.6), closed=True, fc=BODY, ec=INK, lw=1.4, zorder=1))
    ax.add_patch(Polygon(stadium(0, 0, 55.6, 73.0), closed=True, fc="white", ec=INK, lw=0.6, zorder=1))
    for s in (1, -1):
        th = np.linspace(-38, 38, 30)
        xs_ = 27.8 * np.sin(np.radians(th)) * 0.82
        ys_ = s * (36.5 - 27.8 * (1 - np.cos(np.radians(th))) * 0.3)
        ax.plot(xs_, ys_, color="white", lw=6, zorder=2)
        ax.plot(xs_, ys_, color=VENT_C, lw=1.0, ls="--", zorder=2)
    ax.add_patch(Circle((0, 0), 13.5, fc="white", ec=INK, lw=0.6, ls=":", zorder=2))
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.add_patch(Circle((sx * 15, sy * 15), 2.5, fc="#dddddd", ec=INK, lw=0.6, zorder=4))
        ax.add_patch(Circle((sx * 15, sy * 15), 1.55, fc="white", ec=INK, lw=0.5, zorder=5))
    ax.add_patch(
        Rectangle(
            (ESC_X[0], -ESC_LONG), ESC_X[1] - ESC_X[0], 2 * ESC_LONG, fc=ESC_C, alpha=0.35, ec=ESC_C, lw=1.0, zorder=3
        )
    )
    for s in (1, -1):
        for x0, x1 in MR30_X:
            ax.add_patch(
                Rectangle(
                    (x0, min(s * MR30_Y[0], s * MR30_Y[1])),
                    x1 - x0,
                    6.73,
                    fc=ESC_C,
                    alpha=0.7,
                    ec=INK,
                    lw=0.5,
                    zorder=4,
                )
            )
            ax.add_patch(
                Rectangle(
                    (x0 + 1, min(s * PLUG_Y[0], s * PLUG_Y[1])),
                    x1 - x0 - 2,
                    8.19,
                    fc="none",
                    ec=ESC_C,
                    lw=0.9,
                    ls="--",
                    zorder=4,
                )
            )
            xm = (x0 + x1) / 2
            sxm = 1 if xm > 0 else -1
            ax.annotate(
                "",
                xy=(xm + sxm * 14, s * 62),
                xytext=(xm, s * 48),
                arrowprops={"arrowstyle": "->", "color": ESC_C, "lw": 0.9},
            )
    for xs_, ys_ in [(-20.0, 6.0), (-20.0, -6.0)]:
        ax.add_patch(Circle((xs_, ys_), 2.55, fc="#f2c14e", ec=INK, lw=0.6, zorder=5))
    ax.text(
        0,
        -78,
        "Sprite cavity 56 x 73 inside; ESC 30.5 pattern on the frame's 30 x 30 clamp screws (0.25 mm offset:\nream the ESC holes to D3.8), battery studs yellow, plate hole dotted; each MR30 is 29 deg from its motor",
        fontsize=7,
        ha="center",
        va="top",
    )
    ax.set_xlim(-72, 72)
    ax.set_ylim(-95, 70)
    ax.axis("off")
    ax.set_title("(c) tail from below, z = -22\nESC along the cone's long axis", fontsize=9)
    # (d) prop plane
    ax = axes[3]
    ax.set_aspect("equal")
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        ax.plot([0, sx * 93.5], [0, sy * 93.5], color="#dadada", lw=9, solid_capstyle="round", zorder=0)
    for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        mx, my = sx * MOTOR_XY, sy * MOTOR_XY
        ax.add_patch(Circle((mx, my), PROP_R["5 in"], fc="none", ec=INK, lw=0.9))
        ax.add_patch(Circle((mx, my), 9, fc="#555555", ec="none"))
    ax.add_patch(Polygon(stadium(0, 0, 50, 75), closed=True, fc="none", ec=OLD, lw=1.0, ls="--"))
    ax.add_patch(Polygon(faceted(HW, HH, SIDE_Y, CROWN_X), closed=True, fc=BODY, ec=INK, lw=1.4))
    p, q = np.array([HW, SIDE_Y]), np.array([CROWN_X, HH])
    d = q - p
    t = np.clip(np.dot(np.array([80, 80]) - p, d) / np.dot(d, d), 0, 1)
    foot = p + t * d
    tip = np.array([80, 80]) - PROP_R["5 in"] * (np.array([80, 80]) - foot) / np.linalg.norm(np.array([80, 80]) - foot)
    ax.plot([foot[0], tip[0]], [foot[1], tip[1]], color=ESC_C, lw=1.6, zorder=5)
    gap = np.linalg.norm(np.array([80, 80]) - foot) - PROP_R["5 in"]
    ax.text(
        42,
        4,
        f"{gap:.0f} mm to a 5 in prop\n(Sprite 16, iteration 2: 14)",
        fontsize=7.5,
        color=ESC_C,
        ha="left",
        va="center",
    )
    ax.text(
        0,
        -138,
        "The fullest section that holds the flush-mounted stack:\nthe facets follow the prop circle. Bulging them costs clearance.",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    ax.set_xlim(-150, 150)
    ax.set_ylim(-160, 145)
    ax.axis("off")
    ax.set_title("(d) prop plane, looking down the fuselage\nmotors at (+-80, +-80)", fontsize=9)
    fig.suptitle(
        "sprite-aleph, iteration 3.1: cross-sections (x across, y toward the cover; mm)", fontsize=11, x=0.02, ha="left"
    )
    fig.tight_layout()
    fig.savefig(OUT / "sections.png", dpi=170)
    plt.close(fig)


def plan_view():
    fig, ax = plt.subplots(figsize=(17, 6.6))
    ax.set_aspect("equal")
    zs_flare = np.linspace(FLARE[0], FLARE[1], 12)
    hw_flare = 25 + (HW - 25) * (1 - np.cos(np.pi * (zs_flare - FLARE[0]) / (FLARE[1] - FLARE[0]))) / 2
    top = list(zip(zs_flare, hw_flare)) + blended(NOSE_HALF_WIDTH, HW)
    outline = top + [(z, -w) for z, w in reversed(top)]
    ax.add_patch(Polygon(outline, closed=True, fc=BODY, ec=INK, lw=1.4))
    old = [(2, 25), (200.5, 25)] + [
        (z, w)
        for z, w in [
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
    ]
    ax.add_patch(Polygon(old + [(z, -w) for z, w in reversed(old)], closed=True, fc="none", ec=OLD, lw=0.9, ls="--"))
    cone = [(z, x) for z, x in CONE_X] + [(z, -x) for z, x in reversed(CONE_X)]
    ax.add_patch(Polygon(cone, closed=True, fc="none", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-6, -25), 6, 50, fc="#3b3b3b", ec="none"))
    ax.add_patch(Rectangle((-6, -13.5), 6, 27, fc="white", ec="none"))
    ax.add_patch(Rectangle((2, -25), ROOF_END - 2, 50, fc="none", ec=INK, hatch="////", lw=0))
    ax.text(17.5, 34, "roof lip", fontsize=7.5, ha="center")
    ax.text(8, -38, "flare 50 -> 60\nover z 2..10", fontsize=7, ha="center", va="top")
    ax.text(206, -42, "blend 60 -> Sprite nose\nover z 198..214", fontsize=7, ha="center", va="top")
    ax.text(-45, 0, "Sprite tail cone\n(unchanged outline)", fontsize=7.5, ha="center", va="center", color="#555555")
    ax.add_patch(Rectangle((ESC_PCB_Z[0], ESC_X[0]), 1.6, ESC_X[1] - ESC_X[0], fc=ESC_C, ec=INK, lw=0.6))
    ax.text(-20, -32, "ESC (connectors\npoint +-y, see c)", fontsize=6.5, ha="center", va="top", color=ESC_C)
    # battery, cradle, alcove
    ax.add_patch(Rectangle((BATTERY["z"][0], -21), 78, 42, fc=BAT_C, alpha=0.85, ec=INK, lw=0.8))
    ax.add_patch(
        Rectangle((BAT_ENV["z"][0], -24), BAT_ENV["z"][1] - BAT_ENV["z"][0], 48, fc="none", ec=INK, lw=0.8, ls="--")
    )
    ax.text(46, 0, "6S pack: V5 1400 shown, envelope 81 x 48 dashed", fontsize=7.5, ha="center", va="center")
    for zs in (40, 70):
        ax.add_patch(Rectangle((zs - 1, -26), 2, 52, fc=INK, ec="none"))
    for s in (1, -1):
        ax.add_patch(
            Rectangle((POCKET_Z[0], 24 if s > 0 else -26), POCKET_Z[1] - POCKET_Z[0], 2, fc=TRAY_C, ec=INK, lw=0.5)
        )
    ax.add_patch(Rectangle((FLOOR_END_Z, -26), 2, 52, fc=TRAY_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((XT60["z"][0], XT60["x"][0]), 8, 16, fc="#f2c14e", ec=INK, lw=0.6))
    ax.text(95, -24.5, "XT60", fontsize=6.5, ha="center", va="top")
    ax.add_patch(Rectangle((MOLEX_PLUG["z"][0], MOLEX_PLUG["x"][0]), 14.2, 7.1, fc="#dddddd", ec=INK, lw=0.6))
    ax.text(99, 19, "6S plug", fontsize=6, ha="center", va="bottom")
    ax.text(
        44,
        -30,
        "battery cradle: strap slots and the\nalcove bulkhead, glued on the internal floor",
        fontsize=7,
        ha="center",
        va="top",
        color="#555555",
    )
    # Aleph layers from above: bosses on the port wall, stack, heatsink inside; grille strip on the starboard wall
    for zc in HOLES_Z:
        ax.add_patch(Rectangle((zc - 3.5, XP), 7, INNER["hw"] - XP, fc=TRAY_C, ec=INK, lw=0.5))
        ax.add_patch(Circle((zc, HW + 2.5), 2.0, fc="#dddddd", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((BOARD_Z[0], LAYERS_X["base"][0]), 88, 1.56, fc=ALEPH_C, ec=INK, lw=0.6))
    for zc in HOLES_Z:
        ax.add_patch(Rectangle((zc - 2.5, LAYERS_X["standoff"][0]), 5, 10, fc="#dddddd", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((BOARD_Z[0], LAYERS_X["carrier"][0]), 88, 1.57, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((SODIMM["z"][0], LAYERS_X["sodimm"][0]), 76.2, 10.86, fc="#cccccc", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((MODULE["z"][0], LAYERS_X["module"][0]), 69.6, 1.2, fc=ALEPH_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((LID["z"][0], LAYERS_X["lid"][0]), 22.2, 2.63, fc="#555555", ec=INK, lw=0.5))
    ax.add_patch(Rectangle((HEATSINK["z"][0], LAYERS_X["heatsink"][0]), 58, 18, fc=HS_C, alpha=0.7, ec=INK, lw=0.8))
    ax.add_patch(Rectangle((GRILLE["z"][0], -INNER["hw"] - 2.3), 61, 2.6, fc="white", ec=VENT_C, lw=1.2, ls="--"))
    ax.text(
        151.5,
        -36,
        "heatsink inside; fan grille 61 x 34 in the port wall over it",
        fontsize=7.5,
        ha="center",
        va="top",
        color=HS_C,
    )
    for lv in LOUVERS:
        ax.add_patch(
            Rectangle(
                (lv["z"][0], -INNER["hw"] - 2.6), lv["z"][1] - lv["z"][0], 3.2, fc="none", ec=VENT_C, lw=1.0, ls=":"
            )
        )
    ax.text(151.5, -41.5, "fin exhaust louvers fore and aft", fontsize=7, ha="center", va="top", color=VENT_C)
    ax.text(
        151.5,
        35.5,
        "four M2.5 screws from outside (starboard wall) through bosses into the stack's own standoffs;\nthen base, standoffs, carrier, SO-DIMM, module, lid, heatsink",
        fontsize=7,
        ha="center",
        va="bottom",
        color="#555555",
    )
    # nose parts: the VTX plate follows the blend's inner outline with 0.5 clearance
    hw_in = [interp(top, z) - WALL - 0.5 for z in VTX_Z]
    vtx = [(VTX_Z[0], hw_in[0]), (VTX_Z[1], hw_in[1]), (VTX_Z[1], -hw_in[1]), (VTX_Z[0], -hw_in[0])]
    ax.add_patch(Polygon(vtx, closed=True, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((214.8, -18.5), 14.3, 37, fc=NOSE_C, ec=INK, lw=0.6))
    ax.add_patch(Rectangle((234, -10), 19, 20, fc=NOSE_C, ec=INK, lw=0.6))
    for s in (1, -1):
        ax.add_patch(Rectangle((234, s * 13 - 3), 16, 6, fc=NOSE_C, ec=INK, lw=0.5))
    ax.text(204.5, 31, "VTX mount\n(re-derived)", fontsize=7, ha="center", va="bottom")
    ax.text(222, -21, "servo", fontsize=7, ha="center", va="top")
    ax.text(243.5, -18, "camera", fontsize=7, ha="center", va="top")
    # axes and stations
    ax.annotate("", xy=(295, -70), xytext=(-70, -70), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(295, -76, "z (nose)", fontsize=8, ha="right")
    ax.annotate("", xy=(-70, -45), xytext=(-70, -70), arrowprops={"arrowstyle": "->", "color": INK})
    ax.text(-67, -47, "x (starboard)", fontsize=8)
    for z, lab in [
        (-20, "-20"),
        (0, "0"),
        (ROOF_END, "33"),
        (FLOOR_END_Z, "88"),
        (106, "106"),
        (WALL_END, "198"),
        (BLEND[1], "214"),
        (TIP_Z, "249.3"),
    ]:
        ax.plot([z, z], [-67, -64], color=INK, lw=0.6)
        ax.text(z, -68.5, lab, fontsize=7, ha="center", va="top")
    ax.set_xlim(-75, 300)
    ax.set_ylim(-80, 50)
    ax.axis("off")
    ax.set_title(
        "sprite-aleph, iteration 3.1: plan view with the cover removed (mm, assembly frame; Sprite body dashed)",
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
