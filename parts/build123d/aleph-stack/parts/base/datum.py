from build123d import Align, Box, Pos, RectangleRounded, extrude
from params import (
    capXMax,
    capXMin,
    capYMax,
    capYMin,
    capZMin,
    cornerRadius,
    erm5XMax,
    erm5XMin,
    erm5YMax,
    erm5YMin,
    erm5ZMax,
    ixXMax,
    ixXMin,
    ixYMax,
    ixYMin,
    ixZMax,
    jst1XMax,
    jst1XMin,
    jst1YMax,
    jst1YMin,
    jst2XMax,
    jst2XMin,
    jst2YMax,
    jst2YMin,
    jstZMax,
    molexXMax,
    molexXMin,
    molexYMax,
    molexYMin,
    molexZMax,
    pcbLength,
    pcbThickness,
    pcbWidth,
    sdXMax,
    sdXMin,
    sdYMax,
    sdYMin,
    sdZMin,
    usbc1XMax,
    usbc1XMin,
    usbc1YMax,
    usbc1YMin,
    usbc2XMax,
    usbc2XMin,
    usbc2YMax,
    usbc2YMin,
    usbcZMax,
)

assert pcbLength > 2 * cornerRadius, "infeasible: cornerRadius exceeds pcbLength"
assert pcbWidth > 2 * cornerRadius, "infeasible: cornerRadius exceeds pcbWidth"
assert pcbThickness > 0, "infeasible: pcbThickness must be positive"
assert cornerRadius >= 0, "infeasible: cornerRadius must be non-negative"
assert erm5XMin < erm5XMax, "infeasible: erm5 x extent"
assert erm5YMin < erm5YMax, "infeasible: erm5 y extent"
assert erm5ZMax > pcbThickness, "infeasible: erm5ZMax must clear the PCB top"
assert ixXMin < ixXMax, "infeasible: ix x extent"
assert ixYMin < ixYMax, "infeasible: ixYMin must be below ixYMax"
assert ixZMax > pcbThickness, "infeasible: ixZMax must clear the PCB top"
assert molexXMin < molexXMax, "infeasible: molex x extent"
assert molexYMin < molexYMax, "infeasible: molex y extent"
assert molexZMax > pcbThickness, "infeasible: molexZMax must clear the PCB top"
assert usbc1XMin < usbc1XMax, "infeasible: usbc1 x extent"
assert usbc1YMin < usbc1YMax, "infeasible: usbc1 y extent"
assert usbc2XMin < usbc2XMax, "infeasible: usbc2 x extent"
assert usbc2YMin < usbc2YMax, "infeasible: usbc2 y extent"
assert usbcZMax > pcbThickness, "infeasible: usbcZMax must clear the PCB top"
assert jst1XMin < jst1XMax, "infeasible: jst1 x extent"
assert jst1YMin < jst1YMax, "infeasible: jst1 y extent"
assert jst2XMin < jst2XMax, "infeasible: jst2 x extent"
assert jst2YMin < jst2YMax, "infeasible: jst2 y extent"
assert jstZMax > pcbThickness, "infeasible: jstZMax must clear the PCB top"
assert sdXMin < sdXMax, "infeasible: sd x extent"
assert sdYMin < sdYMax, "infeasible: sd y extent"
assert sdZMin < 0, "infeasible: sdZMin must be below the PCB bottom"
assert capXMin < capXMax, "infeasible: cap x extent"
assert capYMin < capYMax, "infeasible: cap y extent"
assert capZMin < 0, "infeasible: capZMin must be below the PCB bottom"


def _box(x0, y0, z0, x1, y1, z1):
    assert x1 > x0 and y1 > y0 and z1 > z0, "infeasible: box extents must be positive"
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


pcb = extrude(
    RectangleRounded(pcbLength, pcbWidth, cornerRadius, align=(Align.MIN, Align.MIN)),
    pcbThickness,
)
erm5 = _box(erm5XMin, erm5YMin, pcbThickness, erm5XMax, erm5YMax, erm5ZMax)
ix_connector = _box(ixXMin, ixYMin, pcbThickness, ixXMax, ixYMax, ixZMax)
molex = _box(molexXMin, molexYMin, pcbThickness, molexXMax, molexYMax, molexZMax)
usbc1 = _box(usbc1XMin, usbc1YMin, pcbThickness, usbc1XMax, usbc1YMax, usbcZMax)
usbc2 = _box(usbc2XMin, usbc2YMin, pcbThickness, usbc2XMax, usbc2YMax, usbcZMax)
jst1 = _box(jst1XMin, jst1YMin, pcbThickness, jst1XMax, jst1YMax, jstZMax)
jst2 = _box(jst2XMin, jst2YMin, pcbThickness, jst2XMax, jst2YMax, jstZMax)
micro_sd = _box(sdXMin, sdYMin, sdZMin, sdXMax, sdYMax, 0.0)
bottom_cap = _box(capXMin, capYMin, capZMin, capXMax, capYMax, 0.0)

datum = pcb + erm5 + ix_connector + molex + usbc1 + usbc2 + jst1 + jst2 + micro_sd + bottom_cap
