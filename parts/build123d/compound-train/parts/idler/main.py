import math

from build123d import (
    Align,
    BuildLine,
    CenterArc,
    Compound,
    Cylinder,
    Polyline,
    Pos,
    extrude,
    make_face,
)

gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
addendumCoeff = 1.0
dedendumCoeff = 1.25
backlashThinning = 0.05
gear40Teeth = 40.0
gear15Teeth = 15.0
gear40FaceWidth = 8.0
gear15FaceWidth = 8.0
boreDiameter = 8.0
flankPoints = 14.0
pitchRadius40 = gearModule * gear40Teeth / 2
tipRadius40 = pitchRadius40 + addendumCoeff * gearModule
rootRadius40 = pitchRadius40 - dedendumCoeff * gearModule
baseRadius40 = pitchRadius40 * math.cos(math.radians(pressureAngle))
pitchRadius15 = gearModule * gear15Teeth / 2
tipRadius15 = pitchRadius15 + addendumCoeff * gearModule
rootRadius15 = pitchRadius15 - dedendumCoeff * gearModule
baseRadius15 = pitchRadius15 * math.cos(math.radians(pressureAngle))
toothThickness = math.pi * gearModule / 2 - backlashThinning
totalHeight = gear40FaceWidth + gear15FaceWidth

assert gearModule > 0, "infeasible: gearModule must be positive"
assert gear40FaceWidth > 0, "infeasible: gear40FaceWidth must be positive"
assert gear15FaceWidth > 0, "infeasible: gear15FaceWidth must be positive"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"
assert gear40Teeth > 2, "infeasible: gear40Teeth must be greater than 2"
assert gear15Teeth > 2, "infeasible: gear15Teeth must be greater than 2"
assert toothThickness > 0, "infeasible: toothThickness must be positive"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90"
assert tipRadius40 > rootRadius40, "infeasible: 40-tooth tip must clear its root"
assert tipRadius15 > rootRadius15, "infeasible: 15-tooth tip must clear its root"
assert rootRadius15 > boreDiameter / 2, "infeasible: bore must fit inside the 15-tooth root"
assert tipRadius15 < rootRadius40, "infeasible: 15-tooth tip must sit inside the 40-tooth root"

# Tool faces run this far past the stock so no cutter face lies on a stock face.
OVERLAP = 0.05


def involute(phi):
    return math.tan(phi) - phi


def gear_face(teeth, pitch_r, tip_r, root_r, base_r):
    """Involute spur profile: tooth 0 centred on +x, arc lands, radial flank below the base."""
    teeth_n = round(teeth)
    points_n = round(flankPoints)
    alpha = math.radians(pressureAngle)
    inv_alpha = involute(alpha)
    # Profile shift adds 2 x m tan(alpha) at the pitch circle; zero at the contract value.
    half_thickness = toothThickness / 2 + (profileShift * gearModule * math.tan(alpha))
    psi_base = half_thickness / pitch_r + inv_alpha
    phi_tip = math.acos(min(1.0, base_r / tip_r))
    psi_tip = psi_base - involute(phi_tip)
    pitch = 2 * math.pi / teeth_n
    root_land = pitch - 2 * psi_base
    assert psi_tip > 0, "infeasible: tip land vanished"
    assert root_land > 0, "infeasible: root lands overlap"
    assert root_r < base_r, "infeasible: root must sit inside the base circle"
    t_tip = math.tan(phi_tip)

    def flank_point(center, sign, roll):
        phi = math.atan(roll) if roll > 0 else 0.0
        radius = base_r * math.sqrt(1 + roll * roll)
        psi = psi_base - involute(phi)
        angle = center + sign * psi
        return (radius * math.cos(angle), radius * math.sin(angle))

    with BuildLine() as outline:
        for i in range(teeth_n):
            center = i * pitch
            cw = [
                (
                    root_r * math.cos(center - psi_base),
                    root_r * math.sin(center - psi_base),
                )
            ]
            cw.extend(flank_point(center, -1, t_tip * k / (points_n - 1)) for k in range(points_n))
            Polyline(*cw)
            CenterArc(
                (0, 0),
                tip_r,
                math.degrees(center - psi_tip),
                math.degrees(2 * psi_tip),
            )
            ccw = [flank_point(center, 1, t_tip * k / (points_n - 1)) for k in range(points_n - 1, -1, -1)]
            ccw.append(
                (
                    root_r * math.cos(center + psi_base),
                    root_r * math.sin(center + psi_base),
                )
            )
            Polyline(*ccw)
            CenterArc(
                (0, 0),
                root_r,
                math.degrees(center + psi_base),
                math.degrees(root_land),
            )
    return make_face(outline.wire())


face40 = gear_face(gear40Teeth, pitchRadius40, tipRadius40, rootRadius40, baseRadius40)
face15 = gear_face(gear15Teeth, pitchRadius15, tipRadius15, rootRadius15, baseRadius15)

blank = extrude(face40, amount=totalHeight)
small = Pos(0, 0, gear40FaceWidth - OVERLAP) * extrude(face15, amount=gear15FaceWidth + 3 * OVERLAP)
outer = Pos(0, 0, gear40FaceWidth) * Cylinder(
    tipRadius40 + 1.0,
    gear15FaceWidth + OVERLAP,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cutter = outer - small
bore = Pos(0, 0, -OVERLAP) * Cylinder(
    boreDiameter / 2,
    totalHeight + 2 * OVERLAP,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = blank - Compound(children=[cutter, bore])
