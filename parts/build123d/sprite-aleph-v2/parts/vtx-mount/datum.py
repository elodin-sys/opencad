"""Passed blockout, unchanged geometry in the identity assembly frame."""

from build123d import Align, Cylinder, Polygon, Pos, extrude
from params import (
    bossAxisZ,
    bossBackY,
    bossRadius,
    envelopeHalfWidth,
    envelopeMaxY,
    envelopeMinY,
    neckFlareTangentY,
    neckHalfWidth,
    plateThickness,
    plateTopZ,
    shoulderY,
    slotDepth,
    slotWidth,
    stepY,
)

assert plateThickness > 0, "plateThickness must be positive"
assert bossRadius > 0, "bossRadius must be positive"
assert envelopeMaxY > bossBackY, "boss must have positive axial length"
assert envelopeMinY < stepY < shoulderY, "plate stations must be ordered"
assert 0 < neckHalfWidth < envelopeHalfWidth, "neck must fit within the plate"
assert 0 < slotDepth < plateThickness, "slotDepth must leave positive skin"
assert slotWidth > 0, "slotWidth must be positive"

# Coarse unpierced plate and neck silhouette. No local pockets or notch details.
# These stations are envelope estimates, not the final normal-offset skin.
outline = Polygon(
    (-20.0, envelopeMinY),
    (20.0, envelopeMinY),
    (envelopeHalfWidth, stepY),
    (envelopeHalfWidth, shoulderY),
    (18.0, shoulderY),
    (neckHalfWidth, neckFlareTangentY),
    (neckHalfWidth, envelopeMaxY),
    (-neckHalfWidth, envelopeMaxY),
    (-neckHalfWidth, neckFlareTangentY),
    (-18.0, shoulderY),
    (-envelopeHalfWidth, shoulderY),
    (-envelopeHalfWidth, stepY),
    align=None,
)
plate = Pos(0, 0, plateTopZ - plateThickness) * extrude(outline, amount=plateThickness)
# The connected boss is part of this single printed body. Its axis stays at207.5;
# its lower surface is203.5, leaving the contract's203 minimum unresolved.
boss = Pos(0, bossBackY, bossAxisZ) * Cylinder(
    bossRadius,
    envelopeMaxY - bossBackY,
    rotation=(-90, 0, 0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
datum = plate + boss
