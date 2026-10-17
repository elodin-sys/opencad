"""The two finite filament passages, cut from the finished exterior web."""

from math import hypot

from build123d import Align, Cylinder, Plane
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
    lugMaxZ,
    plateThickness,
)

overrun = 0.03
region_min_x = 12.5
region_max_x = 23.5
region_min_z = 28.0
region_max_z = 32.0


def apply(body):
    """Fuse the passage tools before performing one subtraction."""
    radius = filamentDiameter / 2.0
    axis_length = hypot(filamentDirX, filamentDirY)
    assert radius > 0.0, "infeasible: filamentDiameter must be positive"
    assert axis_length > 0.0, "infeasible: the angled filament axis must be nonzero"
    dx, dy = filamentDirX / axis_length, filamentDirY / axis_length
    assert dx > 0.0 and dy > 0.0, "infeasible: the entry must approach along positive x and y"
    assert region_min_z <= filamentZ - radius, "infeasible: the bore cuts below the filament region"
    assert filamentZ + radius <= region_max_z, "infeasible: the bore cuts above the filament region"
    assert filamentZ + radius <= lugMaxZ - 0.1, "infeasible: the bore must preserve the web peak"
    assert region_min_x <= filamentTransverseX - radius, "infeasible: the transverse bore exceeds its region"
    assert filamentTransverseX + radius <= region_max_x, "infeasible: the transverse bore exceeds its region"
    assert 0.0 < filamentTransverseEnd < plateThickness - 0.1 - overrun, "infeasible: transverse bore depth"

    # The remote axis point is only a datum.  Use the specified finite entry
    # interval; extending back to that datum would cut unrelated web stock.
    assert 0.0 < filamentEntryStart < filamentEntryEnd, "infeasible: entry stations must be ordered"
    entry_start = filamentEntryStart - overrun
    entry_end = filamentEntryEnd + overrun
    start_x = filamentEntryAxisX + dx * entry_start
    start_y = filamentEntryAxisY + dy * entry_start
    end_x = filamentEntryAxisX + dx * entry_end
    end_y = filamentEntryAxisY + dy * entry_end
    assert region_min_x <= start_x - radius * dy, "infeasible: the entry cuts left of the filament region"
    assert end_x + radius * dy <= region_max_x, "infeasible: the entry cuts right of the filament region"
    assert 0.1 <= start_y - radius * dx, "infeasible: the entry reaches the y=0 datum"
    assert end_y + radius * dx <= plateThickness - 0.1, "infeasible: the entry reaches the rear datum"

    transverse = Plane(origin=(filamentTransverseX, -overrun, filamentZ), z_dir=(0.0, 1.0, 0.0)) * Cylinder(
        radius,
        filamentTransverseEnd + 2.0 * overrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    angled = Plane(origin=(start_x, start_y, filamentZ), z_dir=(dx, dy, 0.0)) * Cylinder(
        radius,
        entry_end - entry_start,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cutter = transverse.fuse(angled)
    shaped = body - cutter
    assert shaped.is_valid, "infeasible: filament subtraction produced an invalid solid"
    assert len(shaped.solids()) == 1, "infeasible: filament subtraction disconnected the web"
    return shaped
