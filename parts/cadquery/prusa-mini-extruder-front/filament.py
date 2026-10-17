import cadquery as cq
from params import (
    filamentDiameter,
    filamentDirX,
    filamentDirY,
    filamentEntryAxisX,
    filamentEntryAxisY,
    filamentEntryEnd,
    filamentEntryStart,
    filamentTransverseEnd,
    filamentTransverseX,
    filamentZ,
)

_OVERRUN = 0.01


def apply(body):
    """Cut only the two documented, finite filament surface segments."""
    assert filamentDiameter > 0.0, "infeasible: filamentDiameter must be positive"
    assert filamentTransverseEnd > 0.0, "infeasible: transverse segment must have positive length"
    assert 0.0 < filamentEntryStart < filamentEntryEnd, "infeasible: angled segment extents must be ordered"
    direction_length = (filamentDirX**2 + filamentDirY**2) ** 0.5
    assert direction_length > 0.0, "infeasible: angled segment direction must be nonzero"
    dx, dy = filamentDirX / direction_length, filamentDirY / direction_length
    assert dx > 0.0 and dy > 0.0, "infeasible: angled segment must point into the upper-right web"

    radius = filamentDiameter / 2.0
    over = _OVERRUN
    start_x = filamentEntryAxisX + dx * (filamentEntryStart - over)
    start_y = filamentEntryAxisY + dy * (filamentEntryStart - over)
    end_x = filamentEntryAxisX + dx * (filamentEntryEnd + over)
    end_y = filamentEntryAxisY + dy * (filamentEntryEnd + over)

    # These are the assigned region limits, not additional design parameters.
    # Both exact D4 surfaces touch z=28 tangentially; no material below it is cut.
    assert 28.0 <= filamentZ - radius and filamentZ + radius <= 32.0, (
        "infeasible: filament cuts leave the assigned vertical region"
    )
    assert 12.5 <= filamentTransverseX - radius and filamentTransverseX + radius <= 23.5, (
        "infeasible: transverse cut leaves the assigned x region"
    )
    assert filamentTransverseEnd + over <= 13.9, "infeasible: transverse cut must stop short of the front face"
    assert 12.5 <= start_x - radius * dy and end_x + radius * dy <= 23.5, (
        "infeasible: angled cut leaves the assigned x region"
    )
    assert 0.1 <= start_y - radius * dx and end_y + radius * dx <= 13.9, (
        "infeasible: angled cut must stop short of the shared y faces"
    )

    # XZ points toward -Y. Start outside y=0, then extrude toward +Y.
    transverse_tool = (
        cq.Workplane("XZ", origin=(filamentTransverseX, -over, filamentZ))
        .circle(radius)
        .extrude(-(filamentTransverseEnd + 2.0 * over))
    )
    # The remote axis origin is only a datum: begin at the finite start extent.
    # Put the circular seam in the supported lower quadrant of the web. This
    # avoids loose UV bounds on one long, trimmed cylinder intersection curve.
    angled_plane = cq.Plane(origin=(start_x, start_y, filamentZ), xDir=(-dy, dx, -1.0), normal=(dx, dy, 0.0))
    angled_tool = cq.Workplane(angled_plane).circle(radius).extrude(filamentEntryEnd - filamentEntryStart + 2.0 * over)
    cutters = transverse_tool.union(angled_tool, clean=True)
    return body.cut(cutters, clean=True)
