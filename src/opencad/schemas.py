"""PartContract: the single source of design intent for a part.

Every number carries provenance and a digital comparison tolerance. Stages read the
contract; none of them may relax it.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Provenance = Literal[
    "stated",  # quoted from a requirement/document
    "measured",  # read from a drawing or image, with pixel evidence
    "measured (reference model)",  # from a reference mesh/coordinate ingest
    "derived",  # computed from other contract values; formula required
    "inferred",  # engineering judgement; rationale required
    "defaulted",  # template/default; rationale required
]

Axis = Literal["x", "y", "z"]
Vec3 = tuple[float, float, float]

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# `zoo kcl lint` Z0001 (lowerCamelCase) rejects a run of three capitals anywhere or two at the end: usbCX, holeID, abcXYZw
_LINT_BAD_CASE = re.compile(r"^[^a-z]|_|[A-Z]{3}|[A-Z]{2}$")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Units(Strict):
    length: Literal["mm", "cm", "m", "in", "ft"] = "mm"
    angle: Literal["deg", "rad"] = "deg"


class Datum(Strict):
    name: str
    description: str


class Frame(Strict):
    origin: str = Field(description="where [0,0,0] is on the part, in words")
    axes: dict[Axis, str] = Field(description="meaning of +x, +y, +z")
    datums: list[Datum] = []

    @model_validator(mode="after")
    def _all_axes(self) -> Frame:
        missing = {"x", "y", "z"} - set(self.axes)
        if missing:
            raise ValueError(f"frame.axes must describe x, y and z (missing {sorted(missing)})")
        return self


class Envelope(Strict):
    min: Vec3
    max: Vec3
    tolerance: float = Field(gt=0, description="absolute, contract length unit")

    @model_validator(mode="after")
    def _ordered(self) -> Envelope:
        if any(hi < lo for lo, hi in zip(self.min, self.max)):
            raise ValueError("envelope.max must be >= envelope.min on every axis")
        return self

    @property
    def size(self) -> Vec3:
        return tuple(hi - lo for lo, hi in zip(self.min, self.max))  # type: ignore[return-value]

    @property
    def volume(self) -> float:
        sx, sy, sz = self.size
        return sx * sy * sz


class EditExpectation(Strict):
    volume_delta: float | None = Field(default=None, description="expected analytic volume change, length unit cubed")
    direction: Literal["increase", "decrease", "none"] | None = None
    tolerance_rel: float = Field(default=0.02, gt=0)
    bbox_delta: Vec3 | None = Field(default=None, description="expected change of the bbox size")


class EditSweep(Strict):
    """Parameter regeneration with no agent: the harness sets each value and re-exports; the part must stay valid and keep its pinned interfaces."""

    values: list[float] | None = Field(default=None, description="absolute values to set")
    min: float | None = None
    max: float | None = None
    steps: int | None = Field(default=None, ge=2)

    @model_validator(mode="after")
    def _one_form(self) -> EditSweep:
        if self.values is None and (self.min is None or self.max is None or self.steps is None):
            raise ValueError("sweep needs `values` or `min`, `max` and `steps`")
        return self

    def sequence(self) -> list[float]:
        if self.values is not None:
            return list(self.values)
        assert self.min is not None and self.max is not None and self.steps is not None
        return [self.min + (self.max - self.min) * i / (self.steps - 1) for i in range(self.steps)]


class EditTest(Strict):
    delta: float = Field(description="added to the parameter value")
    expect: EditExpectation = EditExpectation()
    sweep: EditSweep | None = Field(default=None, description="regeneration over a declared range; every value must rebuild a valid part with its pinned interfaces intact")
    infeasible_deltas: list[float] = Field(default_factory=list, description="deltas that make the part impossible; the KCL must fail an assert (explicit failure), never build a distorted part")


class Parameter(Strict):
    name: str = Field(description="KCL identifier; must appear as a depth-0 constant in the part (any module)")
    value: float
    unit: str = Field(description="mm, deg, or '' for dimensionless")
    provenance: Provenance
    tolerance: float = Field(gt=0, description="digital comparison threshold in `unit`")
    source: str | None = Field(default=None, description="document, figure, or reference this came from")
    formula: str | None = Field(default=None, description="required for derived values")
    rationale: str | None = Field(default=None, description="required for inferred/defaulted values")
    edit_test: EditTest | None = None
    description: str = ""

    @model_validator(mode="after")
    def _provenance_rules(self) -> Parameter:
        if not _IDENT.match(self.name):
            raise ValueError(f"parameter name {self.name!r} is not a KCL identifier")
        if _LINT_BAD_CASE.search(self.name):
            raise ValueError(f"parameter name {self.name!r} fails KCL lint Z0001 (lowerCamelCase: no underscore, no run of three capitals, no capitals at the end; write usbCx, not usbCX)")
        if self.provenance in ("measured", "measured (reference model)", "stated") and not self.source:
            raise ValueError(f"parameter {self.name}: provenance {self.provenance!r} requires `source`")
        if self.provenance == "derived" and not self.formula:
            raise ValueError(f"parameter {self.name}: derived values require `formula`")
        if self.provenance in ("inferred", "defaulted") and not self.rationale:
            raise ValueError(f"parameter {self.name}: {self.provenance} values require `rationale`")
        return self


class SectionExpect(Strict):
    area: float | None = Field(default=None, description="total solid area of the section")
    area_tolerance_rel: float = Field(default=0.01, gt=0)
    loops: int | None = Field(default=None, description="outer boundary loop count (holes not counted)")
    holes: int | None = Field(default=None, description="inner boundary loop count")
    islands_min: int | None = None


class Section(Strict):
    id: str
    plane: Axis
    at: float
    expect: SectionExpect = SectionExpect()
    description: str = ""


class FaceSpec(Strict):
    """A named planar face that must exist (meshing boundaries, mating faces)."""

    name: str
    plane: Axis
    at: float
    normal: Literal["+", "-"]
    area: float | None = None
    area_tolerance_rel: float = Field(default=0.01, gt=0)
    tolerance: float | None = Field(default=None, description="plane position tolerance; defaults to envelope tolerance")
    center: tuple[float, float] | None = Field(
        default=None,
        description="optional in-plane (u,v) centroid so coplanar repeated faces (tabs, legs) can be told apart",
    )
    mode: Literal["one", "sum"] = Field(
        default="one",
        description="one: assign a single measured face; sum: add every hit on the plane (must be explicit)",
    )


class CylinderSpec(Strict):
    """A cylindrical feature (hole, bore, pin, boss, shaft) located by its axis: the check that says "hole H3 is 0.7 mm off its axis"."""

    name: str
    point: Vec3 = Field(description="any point on the nominal axis")
    direction: Vec3 = Field(description="nominal axis direction (sign irrelevant)")
    kind: Literal["hole", "pin", "any"] = Field(default="any", description="hole: concave (bore); pin: convex (boss, shaft)")
    radius: float | None = Field(default=None, gt=0)
    diameter: float | None = Field(default=None, gt=0)
    radius_tolerance: float = Field(default=0.05, gt=0)
    axis_tolerance: float | None = Field(default=None, gt=0, description="max perpendicular axis offset; defaults to envelope tolerance")
    length: float | None = Field(default=None, gt=0, description="expected extent along the axis")
    length_tolerance: float = Field(default=0.05, gt=0)
    t_range: tuple[float, float] | None = Field(default=None, description="expected extent along the axis from `point`, to tell stacked coaxial cylinders apart")
    description: str = ""

    @model_validator(mode="after")
    def _size(self) -> CylinderSpec:
        if (self.radius is None) == (self.diameter is None):
            raise ValueError(f"cylinder {self.name}: give exactly one of radius or diameter")
        if all(abs(x) < 1e-12 for x in self.direction):
            raise ValueError(f"cylinder {self.name}: direction is zero")
        return self

    @property
    def r(self) -> float:
        return self.radius if self.radius is not None else self.diameter / 2  # type: ignore[operator]


class PlaneSpec(Strict):
    """A planar face with an arbitrary outward normal (ramps, chamfer-like inclined faces, drafted walls)."""

    name: str
    point: Vec3 = Field(description="a point on the nominal plane")
    normal: Vec3 = Field(description="outward normal of the face")
    area: float | None = Field(default=None, gt=0)
    area_tolerance_rel: float = Field(default=0.01, gt=0)
    tolerance: float | None = Field(default=None, gt=0, description="plane position tolerance; defaults to envelope tolerance")
    angle_tolerance_deg: float = Field(default=0.5, gt=0)
    description: str = ""


class DimensionSpec(Strict):
    """A distance: the bbox extent along an axis, or the separation of two named faces along that axis."""

    name: str
    axis: Axis
    expected: float
    tolerance: float | None = Field(default=None, gt=0)
    tolerance_rel: float | None = Field(default=None, gt=0)
    between: tuple[str, str] | None = Field(default=None, description="two FaceSpec names; omitted = bbox extent along `axis`")
    description: str = ""

    @model_validator(mode="after")
    def _one_tol(self) -> DimensionSpec:
        if self.tolerance is None and self.tolerance_rel is None:
            raise ValueError(f"dimension {self.name}: needs `tolerance` or `tolerance_rel`")
        return self

    def within(self, actual: float) -> tuple[bool, float]:
        band = self.tolerance if self.tolerance is not None else abs(self.expected) * (self.tolerance_rel or 0)
        return abs(actual - self.expected) <= band, band


class SolidSelector(Strict):
    """A named body in a multi-solid deliverable, identified by a point inside it."""

    name: str
    contains_point: Vec3
    volume: Quantity | None = None
    description: str = ""


class ExcludeCylinder(Strict):
    point: Vec3
    direction: Vec3
    radius: float = Field(gt=0)
    length: float = Field(gt=0)


class HardwareEnvelope(Strict):
    """Evaluator-side geometry the part must respect: a board, a plug body, a keep-out, a purchased component (box, cylinder or placed STEP)."""

    name: str
    kind: Literal["box", "cylinder", "step"]
    min: Vec3 | None = None
    max: Vec3 | None = None
    point: Vec3 | None = None
    direction: Vec3 | None = None
    radius: float | None = Field(default=None, gt=0)
    length: float | None = Field(default=None, gt=0)
    path: str | None = Field(default=None, description="STEP file relative to the design directory")
    translate: Vec3 | None = None
    scale: float | None = Field(default=None, gt=0)
    exclude_cylinders: list[ExcludeCylinder] = Field(default_factory=list, description="cylinders subtracted from the envelope (standoff rings)")
    description: str = ""

    @model_validator(mode="after")
    def _args(self) -> HardwareEnvelope:
        if self.kind == "box" and (self.min is None or self.max is None):
            raise ValueError(f"hardware {self.name}: box needs min and max")
        if self.kind == "cylinder" and None in (self.point, self.direction, self.radius, self.length):
            raise ValueError(f"hardware {self.name}: cylinder needs point, direction, radius, length")
        if self.kind == "step" and not self.path:
            raise ValueError(f"hardware {self.name}: step needs path")
        return self


class ClearanceSpec(Strict):
    """No interference between two bodies (`all`, a solid name or a hardware name), optionally a gap band."""

    name: str
    a: str
    b: str
    min_gap: float = Field(default=0.0, ge=0)
    max_gap: float | None = Field(default=None, ge=0)
    interference_tolerance: float = Field(default=1e-3, gt=0)
    description: str = ""


class PassageSpec(Strict):
    """An interior air path between two probe points, with the ports sealed by plugs or a closing radius."""

    name: str
    point_a: Vec3
    point_b: Vec3
    pitch: float = Field(default=0.5, gt=0)
    seal_radius: float | None = Field(default=None, gt=0)
    plugs: list[tuple[Vec3, Vec3]] = Field(default_factory=list)
    expect_connected: bool = True
    volume_min: float | None = Field(default=None, ge=0)
    volume_max: float | None = Field(default=None, gt=0)
    description: str = ""


class ThicknessSpec(Strict):
    """Minimum wall thickness by inward ray casting on the exported STL."""

    name: str
    min: float = Field(gt=0)
    stat: Literal["min", "p01", "p05"] = "p05"
    samples: int = Field(default=6000, ge=100)
    region: tuple[Vec3, Vec3] | None = None
    max_thickness: float | None = Field(default=None, gt=0)
    description: str = ""


class ProbeSpec(Strict):
    name: str
    state: Literal["void", "solid"]
    points: list[Vec3] = Field(min_length=1)
    description: str = ""


class CylinderCountSpec(Strict):
    name: str
    radius: float | None = Field(default=None, gt=0)
    diameter: float | None = Field(default=None, gt=0)
    radius_tolerance: float = Field(default=0.05, gt=0)
    kind: Literal["hole", "pin", "any"] = "any"
    direction: Vec3 | None = None
    region: tuple[Vec3, Vec3] | None = Field(default=None, description="count only cylinders whose axis centre lies in this box (min, max)")
    expected: int | None = Field(default=None, ge=0)
    expected_min: int | None = Field(default=None, ge=1)
    description: str = ""

    @model_validator(mode="after")
    def _args(self) -> CylinderCountSpec:
        if (self.radius is None) == (self.diameter is None):
            raise ValueError(f"cylinder count {self.name}: give exactly one of radius or diameter")
        if self.expected is None and self.expected_min is None:
            raise ValueError(f"cylinder count {self.name}: needs expected or expected_min")
        return self

    @property
    def r(self) -> float:
        return self.radius if self.radius is not None else self.diameter / 2  # type: ignore[operator]


class GearSpec(Strict):
    """Tooth count of a gear body from a section normal to its axis."""

    name: str
    solid: str | None = Field(default=None, description="SolidSelector name; the whole shape when omitted")
    point: Vec3
    direction: Vec3
    at: float = Field(description="section station along the axis from `point`")
    module: float = Field(gt=0)
    teeth: int = Field(ge=3)
    description: str = ""


class MeshSpec(Strict):
    """Two gear bodies rotated about their axes through one pitch: no interference, flank gap inside the backlash band."""

    name: str
    a: str
    b: str
    axis_a: tuple[Vec3, Vec3]
    axis_b: tuple[Vec3, Vec3]
    ratio: float = Field(gt=0, description="teeth_a / teeth_b")
    pitch_deg: float = Field(gt=0)
    steps: int = Field(default=6, ge=2)
    backlash_max: float = Field(default=0.3, gt=0)
    description: str = ""


class Verify(Strict):
    method: Literal["bbox", "section", "void", "solid", "count", "face", "cylinder", "plane", "dimension"]
    section: str | None = Field(default=None, description="Section.id for method=section/count")
    points: list[Vec3] | None = Field(default=None, description="probe points for void/solid")
    face: str | None = Field(default=None, description="FaceSpec.name for method=face")
    cylinder: str | None = Field(default=None, description="CylinderSpec.name for method=cylinder")
    plane: str | None = Field(default=None, description="PlaneSpec.name for method=plane")
    dimension: str | None = Field(default=None, description="DimensionSpec.name for method=dimension")
    count: int | None = None
    note: str = ""

    @model_validator(mode="after")
    def _args(self) -> Verify:
        if self.method in ("void", "solid") and not self.points:
            raise ValueError(f"verify {self.method} needs `points`")
        if self.method in ("section", "count") and not self.section:
            raise ValueError(f"verify {self.method} needs `section`")
        for m in ("face", "cylinder", "plane", "dimension"):
            if self.method == m and not getattr(self, m):
                raise ValueError(f"verify {m} needs `{m}`")
        return self


class Feature(Strict):
    id: str
    kind: Literal[
        "extrude", "revolve", "sweep", "loft", "hole", "pocket", "cut", "fillet", "chamfer", "shell",
        "pattern", "boss", "rib", "wall", "cavity", "channel", "profile", "other",
    ]
    description: str
    parameters: list[str] = Field(default_factory=list, description="Parameter names driving this feature")
    count: int | None = None
    verify: list[Verify] = Field(default_factory=list)
    optional: bool = Field(default=False, description="cosmetic; failure is disclosed, not fatal")


class Interface(Strict):
    name: str
    description: str
    must_not_change: bool = True
    checks: list[str] = Field(
        default_factory=list,
        description="acceptance items (face, cylinder, plane, dimension, section, symmetry names) that pin this interface; preserved across edits, "
        "so pin only items that none of this contract's edit tests move or resize",
    )


class Quantity(Strict):
    expected: float
    tolerance: float | None = Field(default=None, gt=0, description="absolute")
    tolerance_rel: float | None = Field(default=None, gt=0)
    provenance: Provenance = "derived"
    note: str = ""

    @model_validator(mode="after")
    def _one_tol(self) -> Quantity:
        if self.tolerance is None and self.tolerance_rel is None:
            raise ValueError("quantity needs `tolerance` or `tolerance_rel`")
        return self

    def within(self, actual: float) -> tuple[bool, float]:
        err = abs(actual - self.expected)
        band = self.tolerance if self.tolerance is not None else abs(self.expected) * (self.tolerance_rel or 0)
        return err <= band, band


class PointQuantity(Strict):
    expected: Vec3
    tolerance: float = Field(gt=0, description="absolute per-axis")
    provenance: Provenance = "derived"
    note: str = ""

    def within(self, actual: Vec3) -> tuple[bool, Vec3]:
        errs = tuple(abs(a - e) for a, e in zip(actual, self.expected))
        return all(e <= self.tolerance for e in errs), errs  # type: ignore[return-value]


class Deviation(Strict):
    p95_max: float = Field(gt=0, description="95th percentile point-to-surface distance vs reference")
    hausdorff_max: float | None = Field(default=None, gt=0)
    silhouette_iou_min: float | None = Field(default=None, gt=0, le=1)


class SymmetrySpec(Strict):
    """Mirror-plane surface agreement: sample the mesh, reflect, measure point-to-surface distance."""

    name: str
    plane: Axis
    at: float = 0.0
    max_deviation: float = Field(default=0.1, gt=0, description="max point-to-surface distance after reflection, mm")
    p95_deviation: float = Field(default=0.05, gt=0, description="95th percentile of the same distance, mm")
    source: str | None = Field(default=None, description="document that states a band tighter than the defaults; required for one")


class BlockoutBand(Strict):
    volume_min: float = Field(ge=0)
    volume_max: float = Field(gt=0)


class Acceptance(Strict):
    bbox_tolerance: float | None = Field(default=None, gt=0, description="defaults to envelope.tolerance")
    volume: Quantity | None = None
    surface_area: Quantity | None = None
    center_of_mass: PointQuantity | None = None
    solid_count: int = Field(default=1, ge=1)
    sections: list[Section] = Field(default_factory=list)
    faces: list[FaceSpec] = Field(default_factory=list)
    cylinders: list[CylinderSpec] = Field(default_factory=list)
    planes: list[PlaneSpec] = Field(default_factory=list)
    dimensions: list[DimensionSpec] = Field(default_factory=list)
    solids: list[SolidSelector] = Field(default_factory=list)
    hardware: list[HardwareEnvelope] = Field(default_factory=list)
    clearances: list[ClearanceSpec] = Field(default_factory=list)
    passages: list[PassageSpec] = Field(default_factory=list)
    thickness: list[ThicknessSpec] = Field(default_factory=list)
    probes: list[ProbeSpec] = Field(default_factory=list)
    cylinder_counts: list[CylinderCountSpec] = Field(default_factory=list)
    gears: list[GearSpec] = Field(default_factory=list)
    meshes: list[MeshSpec] = Field(default_factory=list)
    deviation: Deviation | None = None
    symmetry: list[SymmetrySpec] = Field(default_factory=list)
    blockout: BlockoutBand | None = None
    export_volume_tolerance_rel: float = Field(default=0.002, gt=0, description="KCL vs STEP vs STL agreement")


class Reference(Strict):
    path: str = Field(description="relative to the design directory")
    kind: Literal["text", "image", "drawing", "mesh", "table", "cad", "reference-model", "other"]
    role: Literal["authoritative", "illustrative"]
    sha256: str | None = None
    units: str | None = None
    revision: str | None = None
    note: str = ""


class PartContract(Strict):
    schema_version: Literal[1] = 1
    name: str
    intent: str = Field(min_length=8)
    units: Units = Units()
    material: str | None = None
    density_kg_m3: float | None = Field(default=None, gt=0)
    process: str | None = None
    frame: Frame
    envelope: Envelope
    parameters: list[Parameter] = Field(min_length=1)
    features: list[Feature] = Field(min_length=1)
    interfaces: list[Interface] = Field(default_factory=list)
    acceptance: Acceptance
    references: list[Reference] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    release_status: Literal["training-only", "reconstruction", "prototype"] = "reconstruction"

    @model_validator(mode="after")
    def _cross_refs(self) -> PartContract:
        names = [p.name for p in self.parameters]
        dupes = {n for n in names if names.count(n) > 1}
        if dupes:
            raise ValueError(f"duplicate parameter names: {sorted(dupes)}")
        fids = [f.id for f in self.features]
        if len(set(fids)) != len(fids):
            raise ValueError("duplicate feature ids")
        sections = {s.id for s in self.acceptance.sections}
        faces = {f.name for f in self.acceptance.faces}
        cylinders = {c.name for c in self.acceptance.cylinders}
        planes = {p.name for p in self.acceptance.planes}
        dimensions = {d.name for d in self.acceptance.dimensions}
        for group, label in ((faces, "face"), (cylinders, "cylinder"), (planes, "plane"), (dimensions, "dimension")):
            items = getattr(self.acceptance, label + "s")
            if len(group) != len(items):
                raise ValueError(f"duplicate {label} names in acceptance")
        solids = {s.name for s in self.acceptance.solids}
        hardware = {h.name for h in self.acceptance.hardware}
        extra: dict[str, set[str]] = {}
        for attr in ("solids", "hardware", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes", "symmetry"):
            attr_names = [x.name for x in getattr(self.acceptance, attr)]
            if len(set(attr_names)) != len(attr_names):
                raise ValueError(f"duplicate names in acceptance.{attr}")
            extra[attr] = set(attr_names)
        collide = extra["symmetry"] & (sections | faces | cylinders | planes | dimensions)
        if collide:
            raise ValueError(f"symmetry names collide with other acceptance items: {sorted(collide)}")
        bodies = solids | hardware | {"all"}
        for cl in self.acceptance.clearances:
            for side in (cl.a, cl.b):
                if side not in bodies:
                    raise ValueError(f"clearance {cl.name} references unknown body {side!r} (solids, hardware or 'all')")
        for g in self.acceptance.gears:
            if g.solid is not None and g.solid not in solids:
                raise ValueError(f"gear {g.name} references unknown solid {g.solid!r}")
        for ms in self.acceptance.meshes:
            for side in (ms.a, ms.b):
                if side not in solids:
                    raise ValueError(f"mesh {ms.name} references unknown solid {side!r}")
        for d in self.acceptance.dimensions:
            for fn in d.between or ():
                if fn not in faces:
                    raise ValueError(f"dimension {d.name} references unknown face {fn!r}")
        for f in self.features:
            for pn in f.parameters:
                if pn not in names:
                    raise ValueError(f"feature {f.id} references unknown parameter {pn!r}")
            for v in f.verify:
                if v.section and v.section not in sections:
                    raise ValueError(f"feature {f.id} references unknown section {v.section!r}")
                if v.face and v.face not in faces:
                    raise ValueError(f"feature {f.id} references unknown face {v.face!r}")
                if v.cylinder and v.cylinder not in cylinders:
                    raise ValueError(f"feature {f.id} references unknown cylinder {v.cylinder!r}")
                if v.plane and v.plane not in planes:
                    raise ValueError(f"feature {f.id} references unknown plane {v.plane!r}")
                if v.dimension and v.dimension not in dimensions:
                    raise ValueError(f"feature {f.id} references unknown dimension {v.dimension!r}")
        known = sections | faces | cylinders | planes | dimensions | set().union(*(v for k, v in extra.items() if k != "hardware"))
        for i in self.interfaces:
            for chk in i.checks:
                if chk not in known:
                    raise ValueError(f"interface {i.name} references unknown acceptance item {chk!r}")
        if self.acceptance.blockout and self.acceptance.blockout.volume_max < self.acceptance.blockout.volume_min:
            raise ValueError("acceptance.blockout.volume_max < volume_min")
        for s in self.acceptance.sections:
            lo, hi = self.envelope.min["xyz".index(s.plane)], self.envelope.max["xyz".index(s.plane)]
            if not (lo <= s.at <= hi):
                raise ValueError(f"section {s.id} at {s.plane}={s.at} lies outside the envelope [{lo}, {hi}]")
        return self

    # convenience -----------------------------------------------------------------
    def parameter(self, name: str) -> Parameter:
        for p in self.parameters:
            if p.name == name:
                return p
        raise KeyError(name)

    @property
    def bbox_tolerance(self) -> float:
        return self.acceptance.bbox_tolerance or self.envelope.tolerance

    def blockout_band(self) -> tuple[float, float]:
        if self.acceptance.blockout:
            return self.acceptance.blockout.volume_min, self.acceptance.blockout.volume_max
        return 0.5 * self.envelope.volume, self.envelope.volume * (1 + 1e-6)

    def provenance_summary(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self.parameters:
            out[p.provenance] = out.get(p.provenance, 0) + 1
        return out

    def interface_checks(self) -> list[str]:
        """Acceptance item names pinned by must_not_change interfaces (the preserved set for edits and change requests)."""
        out: list[str] = []
        for i in self.interfaces:
            if i.must_not_change:
                out += [c for c in i.checks if c not in out]
        return out


# ---------------------------------------------------------------------------------------------------------------------
# AssemblyContract: part contracts placed by joints and driven through transmissions, with the fluid regions, named
# boundaries, operating cases and simulations that predict the declared observables. Measured performance references
# stay in the evaluator's truth manifest; the contract states only what to predict and the requirements the sources give.

JointKind = Literal["rigid", "revolute", "slider", "cylindrical", "ball", "planar"]
BoundaryRole = Literal[
    "inlet", "outlet", "wall", "rotating_wall", "moving_wall", "interface", "symmetry", "opening", "contact",
    "heat_flux", "convection", "radiation", "fixed", "load", "other",
]
Physics = Literal[
    "kinematic", "thermal_transient", "thermal_steady", "structural_static", "modal", "thermoelastic", "cfd_steady",
    "cfd_transient", "reduced",
]


def _norm(v: Vec3) -> float:
    return sum(x * x for x in v) ** 0.5


class JointFrame(Strict):
    """A joint axis in one body's own frame (its part contract frame, millimetres)."""

    origin: Vec3
    axis: Vec3 = (0.0, 0.0, 1.0)
    ref: Vec3 | None = Field(default=None, description="zero-angle direction perpendicular to `axis`; needed for a rigid joint and for a phased revolute rest angle")

    @model_validator(mode="after")
    def _dirs(self) -> JointFrame:
        if _norm(self.axis) < 1e-12:
            raise ValueError("joint frame axis is zero")
        if self.ref is not None:
            if _norm(self.ref) < 1e-12:
                raise ValueError("joint frame ref is zero")
            if abs(sum(a * b for a, b in zip(self.axis, self.ref))) / (_norm(self.axis) * _norm(self.ref)) > 1e-3:
                raise ValueError("joint frame ref must be perpendicular to axis")
        return self


class Drive(Strict):
    """What moves a joint: a motor at a speed (or a speed history), or nothing (free, driven through a transmission)."""

    kind: Literal["motor", "free"] = "motor"
    speed: float | None = Field(default=None, description="rpm for a rotation, mm/s for a translation, at the reference operating case")
    case_value: str | None = Field(default=None, description="operating-case value key that sets the speed per case (e.g. speedRpm)")
    history: list[tuple[float, float]] = Field(default_factory=list, description="(time s, speed) piecewise-linear speed history: a braking or start-up profile")
    description: str = ""


class Joint(Strict):
    """Child body frame placed on the parent body frame: the axes coincide, `offset` along the parent axis, `angle` about it."""

    name: str
    kind: JointKind
    parent: str
    child: str
    parent_frame: JointFrame
    child_frame: JointFrame
    offset: float = Field(default=0.0, description="rest (child origin - parent origin) . parent axis, mm")
    angle: float = Field(default=0.0, description="rest angle of the child ref from the parent ref about the parent axis, deg (checked when both refs are given)")
    flip: bool = Field(default=False, description="child axis anti-parallel to the parent axis")
    limits: tuple[float, float] | None = Field(default=None, description="motion range from rest: deg (rotation) or mm (translation)")
    drive: Drive | None = None
    closure: bool = Field(default=False, description="closes a kinematic loop (a four-bar's last pin): both bodies are placed through other joints, this "
                                                     "joint is not part of the tree, and the evaluator solves the loop so its frames stay coincident at every pose")
    position_tolerance: float = Field(default=0.05, gt=0)
    angle_tolerance_deg: float = Field(default=0.5, gt=0)
    description: str = ""

    @property
    def rotates(self) -> bool:
        return self.kind in ("revolute", "cylindrical", "ball")


class GearMeshCheck(Strict):
    pitch_deg: float = Field(gt=0, description="one tooth pitch of the driver")
    steps: int = Field(default=12, ge=2)
    backlash_max: float = Field(default=0.3, gt=0)
    interference_tolerance: float = Field(default=1e-3, gt=0)


class Transmission(Strict):
    """Couples two joints: driven displacement = ratio x driver displacement (the sign carries the sense)."""

    name: str
    kind: Literal["gear", "belt", "chain", "roller", "screw", "cam", "linkage", "other"]
    driver: str
    driven: str
    ratio: float = Field(description="deg/deg for two rotations, mm/deg for a rack or screw; negative for an opposite sense")
    carrier: str | None = Field(default=None, description="epicyclic mesh: the carrier arm's joint. `ratio` applies to displacements relative to the carrier "
                                                          "(a joint mounted on the carrier already moves with it); a rigid driver is a fixed ring or sun")
    mesh: GearMeshCheck | None = Field(default=None, description="gear: a meshing sweep of the two bodies through one driver pitch")
    description: str = ""

    @model_validator(mode="after")
    def _ratio(self) -> Transmission:
        if self.ratio == 0:
            raise ValueError(f"transmission {self.name}: ratio is zero")
        return self


class AssemblyPart(Strict):
    """One body instance. Several instances may share a design (three rollers, one roller design)."""

    name: str = Field(description="body name used by joints, clearances, boundaries and `placements`")
    kind: Literal["modelled", "purchased", "derived"] = Field(default="modelled", description="modelled: its own part design; purchased: catalog geometry built by the evaluator; derived: built in the assembly source from other bodies (a fluid region)")
    design: str | None = Field(default=None, description="designs/<design> part bundle (modelled)")
    intent: str = Field(default="", description="modelled: the part's drafting intent in its own frame, with every dimension and interface it must provide")
    catalog: HardwareEnvelope | None = Field(default=None, description="purchased: evaluator-built geometry in the part's own frame")
    role: Literal["solid", "fluid", "compliant", "construction"] = Field(
        default="solid", description="construction: a supplied solid staged as an input only to build derived bodies (e.g. a flow-region model); never placed or exported")
    material: str | None = None
    density_kg_m3: float | None = Field(default=None, gt=0)
    description: str = ""

    @model_validator(mode="after")
    def _kind(self) -> AssemblyPart:
        if not _IDENT.match(self.name):
            raise ValueError(f"part name {self.name!r} is not an identifier")
        if self.kind == "modelled" and not self.design:
            raise ValueError(f"part {self.name}: modelled parts need `design`")
        if self.kind == "purchased" and self.catalog is None:
            raise ValueError(f"part {self.name}: purchased parts need `catalog` geometry")
        if self.role == "fluid" and self.kind != "derived":
            raise ValueError(f"part {self.name}: a fluid body is derived (built in the assembly source), not {self.kind}")
        if self.role == "construction" and self.kind == "derived":
            raise ValueError(f"part {self.name}: a construction input is supplied (purchased or modelled), not derived")
        return self

    @property
    def placed(self) -> bool:
        return self.role != "construction"


class CapPlane(Strict):
    name: str
    point: Vec3
    normal: Vec3 = Field(description="outward from the fluid")


class FluidVolume(Strict):
    """A fluid region bounded by `walls`, with `minus` bodies inside it and the ports closed by `caps`."""

    name: str
    body: str | None = Field(default=None, description="the derived fluid body the assembly source builds; omitted: evaluator-derived only")
    walls: list[str] = Field(min_length=1)
    minus: list[str] = Field(default_factory=list)
    caps: list[CapPlane] = Field(default_factory=list)
    seed: Vec3 = Field(description="a point inside the fluid, at least 1 mm from every wall")
    volume: Quantity | None = None
    hausdorff_max: float = Field(default=0.2, gt=0, description="derived region vs the source's fluid body, mm")
    description: str = ""


class Boundary(Strict):
    """A named boundary patch: the faces of `body` picked by one selector, in the assembly frame at rest."""

    name: str
    role: BoundaryRole
    body: str
    select: Literal["plane", "cylinder", "touching", "region", "rest"] = Field(description="rest: every face no other boundary of this body claims")
    point: Vec3 | None = None
    normal: Vec3 | None = Field(default=None, description="plane: outward normal of the face")
    direction: Vec3 | None = Field(default=None, description="cylinder: axis direction")
    radius: float | None = Field(default=None, gt=0)
    touching: str | None = Field(default=None, description="touching: faces of `body` lying on this other body's surface")
    region: tuple[Vec3, Vec3] | None = Field(default=None, description="region: faces whose centroid lies in this box (min, max)")
    tolerance: float = Field(default=0.05, gt=0)
    area: Quantity | None = None
    description: str = ""

    @model_validator(mode="after")
    def _args(self) -> Boundary:
        need = {"plane": ("point", "normal"), "cylinder": ("point", "direction", "radius"), "touching": ("touching",), "region": ("region",)}
        missing = [k for k in need.get(self.select, ()) if getattr(self, k) is None]
        if missing:
            raise ValueError(f"boundary {self.name}: select {self.select} needs {missing}")
        return self


class OperatingCase(Strict):
    id: str
    values: dict[str, float] = Field(description="named operating inputs, e.g. {speedRpm: 3500, flowLMin: 6.0}")
    units: dict[str, str] = Field(default_factory=dict)
    split: Literal["development", "held_out"] = "development"
    source: str | None = None
    description: str = ""


class InputValue(Strict):
    """A physical simulation input (material property, load, boundary value) with provenance; never fitted to a result."""

    value: float
    unit: str
    provenance: Provenance
    source: str | None = None
    formula: str | None = None
    rationale: str | None = None
    uncertainty: float | None = Field(default=None, ge=0, description="standard uncertainty in `unit` (u_input)")

    @model_validator(mode="after")
    def _provenance_rules(self) -> InputValue:
        if self.provenance in ("measured", "measured (reference model)", "stated") and not self.source:
            raise ValueError(f"input {self.value} {self.unit}: provenance {self.provenance!r} requires `source`")
        if self.provenance == "derived" and not self.formula:
            raise ValueError(f"input {self.value} {self.unit}: derived values require `formula`")
        if self.provenance in ("inferred", "defaulted") and not self.rationale:
            raise ValueError(f"input {self.value} {self.unit}: {self.provenance} values require `rationale`")
        return self


class RefinementRegion(Strict):
    """A zone meshed finer by the refinement levels that name it (OpenFOAM refinementRegions). `rotor_tip` is the annulus about the
    rotor's joint axis spanning its tip radius over the axial reach of its tips (a tip gap); `cylinder` and `box` are in the assembly
    frame, mm."""

    name: str
    shape: Literal["rotor_tip", "cylinder", "box"]
    body: str | None = Field(default=None, description="rotor_tip: the rotating body (default the simulation's rotor)")
    inside_mm: float = Field(default=2.0, ge=0, description="rotor_tip: radial depth inside the tip radius")
    outside_mm: float = Field(default=3.0, ge=0, description="rotor_tip: radial reach past the tip radius (the gap and a margin)")
    axial_margin_mm: float = Field(default=5.0, ge=0, description="rotor_tip: axial margin past the tips")
    point1: Vec3 | None = None
    point2: Vec3 | None = None
    radius: float | None = Field(default=None, gt=0)
    min: Vec3 | None = None
    max: Vec3 | None = None
    description: str = ""

    @model_validator(mode="after")
    def _shape(self) -> RefinementRegion:
        missing = [k for k in {"cylinder": ("point1", "point2", "radius"), "box": ("min", "max")}.get(self.shape, ()) if getattr(self, k) is None]
        if missing:
            raise ValueError(f"refinement region {self.name}: shape {self.shape} needs {missing}")
        return self


class RefinementLevel(Strict):
    """One mesh of a refinement ladder: `factor` scales every cell size; `regions` refines named regions that many levels past the finest
    surface cells (each level halves the cell size); `iterations` overrides settings.iterations on this mesh."""

    factor: float = Field(gt=0)
    regions: dict[str, int] = Field(default_factory=dict)
    iterations: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _levels(self) -> RefinementLevel:
        if any(n < 1 for n in self.regions.values()):
            raise ValueError(f"refinement level {self.factor:g}: region levels start at 1 (omit a region the level does not refine)")
        return self

    @property
    def label(self) -> str:
        return f"{self.factor:g}" + "".join(f"-{k}{v}" for k, v in sorted(self.regions.items()))


class Simulation(Strict):
    """One analysis over the assembled geometry. Inputs are physics with provenance; settings are numerics only."""

    id: str
    physics: Physics
    solver: str = Field(description="calculix, openfoam, or reduced:<model>")
    cases: list[str] = Field(default_factory=list, description="operating case ids")
    bodies: list[str] = Field(default_factory=list)
    inputs: dict[str, InputValue] = Field(default_factory=dict, description="named physical inputs; per-body material properties as <body>.<property>")
    settings: dict[str, float | int | str | bool | list[float]] = Field(default_factory=dict, description="numerical settings: time step, end time, mesh size, iterations")
    outputs: list[str] = Field(default_factory=list, description="observable ids this analysis predicts")
    regions: list[RefinementRegion] = Field(default_factory=list, description="openfoam: zones the refinement levels refine further, by name")
    refinement: list[float | RefinementLevel] = Field(
        default_factory=lambda: [1.0, 0.5],
        description="mesh levels, coarse to fine, the last one the prediction: a size factor, or {factor, regions, iterations}. Each step refines "
                    "everywhere (a smaller factor) or only inside regions (more region levels); three levels give the grid-convergence index")
    description: str = ""

    @model_validator(mode="after")
    def _solver(self) -> Simulation:
        if self.solver not in ("calculix", "openfoam") and not self.solver.startswith("reduced:"):
            raise ValueError(f"simulation {self.id}: solver must be calculix, openfoam or reduced:<model>, got {self.solver!r}")
        names = [r.name for r in self.regions]
        if len(set(names)) != len(names):
            raise ValueError(f"simulation {self.id}: duplicate refinement region names {names}")
        levels = self.levels()
        for lv in levels:
            if set(lv.regions) - set(names):
                raise ValueError(f"simulation {self.id}: refinement level {lv.label} names unknown regions {sorted(set(lv.regions) - set(names))}")
        labels = [lv.label for lv in levels]
        if len(set(labels)) != len(labels):
            raise ValueError(f"simulation {self.id}: duplicate refinement levels {labels}")
        return self

    def levels(self) -> list[RefinementLevel]:
        return [lv if isinstance(lv, RefinementLevel) else RefinementLevel(factor=float(lv)) for lv in self.refinement]


class ObservableSpec(Strict):
    """A prediction the pipeline must report: what, where, how averaged. `min`/`max`/`expected` are source requirements or
    analytic checks, never a measured result (those live in the truth manifest)."""

    id: str
    quantity: str = Field(description="e.g. max_temperature, pressure_rise, velocity_magnitude, transmission_ratio, volume_per_rev; kinematic: "
                                       "joint_value, joint_range, point_x, point_y, point_z")
    unit: str
    simulation: str | None = Field(default=None, description="the simulation that predicts it; omitted: kinematics or domains")
    case: str | None = None
    body: str | None = None
    joint: str | None = Field(default=None, description="joint_value / joint_range: the joint whose displacement from rest is reported")
    motion: str | None = Field(default=None, description="kinematic observables: the acceptance motion whose drive is the input; without `at`, a series over its range")
    at: float | None = Field(default=None, description="kinematic observables: the drive's displacement from rest (deg or mm) at which to report")
    location: Vec3 | None = None
    line: tuple[Vec3, Vec3] | None = None
    averaging: Literal["instantaneous", "time_averaged", "phase_averaged", "maximum", "minimum", "integral", "final", "steady"] = "steady"
    min: float | None = None
    max: float | None = None
    expected: Quantity | None = None
    description: str = ""


class MotionSweep(Strict):
    """Drive one joint through a range; transmissions propagate; every pose must stay interference-free."""

    name: str
    drive: str = Field(description="joint name")
    range: tuple[float, float]
    steps: int = Field(default=24, ge=2)
    interference_tolerance: float = Field(default=1e-3, gt=0, description="mm3 per body pair")
    pairs: list[tuple[str, str]] = Field(default_factory=list, description="only these pairs; default: every pair in relative motion")
    description: str = ""


class AssemblyAcceptance(Strict):
    bbox_tolerance: float | None = Field(default=None, gt=0)
    solid_count: int | None = Field(default=None, ge=1, description="defaults to the number of bodies")
    mass_kg: Quantity | None = None
    center_of_mass: PointQuantity | None = None
    clearances: list[ClearanceSpec] = Field(default_factory=list)
    motions: list[MotionSweep] = Field(default_factory=list)
    agreement_volume_rel: float = Field(default=1e-4, gt=0, description="placed body vs its part handoff STEP")
    agreement_hausdorff: float = Field(default=0.05, gt=0)


class AssemblyContract(Strict):
    schema_version: Literal[1] = 1
    kind: Literal["assembly"] = "assembly"
    name: str
    intent: str = Field(min_length=8)
    units: Units = Units()
    frame: Frame
    envelope: Envelope
    datum_part: str
    parts: list[AssemblyPart] = Field(min_length=1)
    parameters: list[Parameter] = Field(default_factory=list, description="assembly-level values: centre distances, offsets, ratios")
    joints: list[Joint] = Field(default_factory=list)
    transmissions: list[Transmission] = Field(default_factory=list)
    fluid_volumes: list[FluidVolume] = Field(default_factory=list)
    boundaries: list[Boundary] = Field(default_factory=list)
    operating_cases: list[OperatingCase] = Field(default_factory=list)
    observables: list[ObservableSpec] = Field(default_factory=list)
    simulations: list[Simulation] = Field(default_factory=list)
    acceptance: AssemblyAcceptance = AssemblyAcceptance()
    references: list[Reference] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    release_status: Literal["training-only", "reconstruction", "prototype"] = "reconstruction"

    @model_validator(mode="after")
    def _cross_refs(self) -> AssemblyContract:
        def unique(label: str, names: list[str]) -> set[str]:
            dupes = sorted({n for n in names if names.count(n) > 1})
            if dupes:
                raise ValueError(f"duplicate {label}: {dupes}")
            return set(names)

        unique("part names", [p.name for p in self.parts])
        bodies = {p.name for p in self.parts if p.placed}
        joints = unique("joint names", [j.name for j in self.joints])
        cases = unique("operating case ids", [c.id for c in self.operating_cases])
        observables = unique("observable ids", [o.id for o in self.observables])
        sims = unique("simulation ids", [s.id for s in self.simulations])
        unique("transmission names", [t.name for t in self.transmissions])
        unique("fluid volume names", [f.name for f in self.fluid_volumes])
        unique("boundary names", [b.name for b in self.boundaries])
        unique("parameter names", [p.name for p in self.parameters])
        unique("clearance names", [c.name for c in self.acceptance.clearances])
        unique("motion names", [m.name for m in self.acceptance.motions])
        if self.datum_part not in bodies:
            raise ValueError(f"datum_part {self.datum_part!r} is not a part")
        children: dict[str, str] = {}
        for j in self.joints:
            for side in (j.parent, j.child):
                if side not in bodies:
                    raise ValueError(f"joint {j.name} references unknown body {side!r}")
            if j.parent == j.child:
                raise ValueError(f"joint {j.name}: parent and child are the same body")
            if j.closure:
                continue
            if j.child == self.datum_part:
                raise ValueError(f"joint {j.name}: the datum part {self.datum_part!r} cannot be a joint child")
            if j.child in children:
                raise ValueError(f"body {j.child!r} is the child of two joints ({children[j.child]}, {j.name}); joints form a tree "
                                 "(the joint that closes a loop is `closure: true`)")
            children[j.child] = j.name
            if j.kind == "rigid" and (j.parent_frame.ref is None or j.child_frame.ref is None):
                raise ValueError(f"joint {j.name}: a rigid joint needs `ref` on both frames")
        parent_of = {j.child: j.parent for j in self.joints if not j.closure}
        for b in bodies - {self.datum_part}:
            if b not in parent_of:
                raise ValueError(f"body {b!r} is not attached: every body except the datum part is the child of exactly one joint")
            seen, cur = {b}, b
            while cur != self.datum_part:
                cur = parent_of.get(cur, self.datum_part)
                if cur in seen:
                    raise ValueError(f"joint cycle through {sorted(seen)}")
                seen.add(cur)
        for t in self.transmissions:
            for side in (t.driver, t.driven):
                if side not in joints:
                    raise ValueError(f"transmission {t.name} references unknown joint {side!r}")
            if t.driver == t.driven:
                raise ValueError(f"transmission {t.name}: driver and driven are the same joint")
            if t.carrier is not None and (t.carrier not in joints or t.carrier in (t.driver, t.driven)):
                raise ValueError(f"transmission {t.name}: carrier {t.carrier!r} must be another joint of the assembly")
        for d in {t.driven for t in self.transmissions}:
            by = [t for t in self.transmissions if t.driven == d]
            if len(by) > 1 and any(t.carrier is None for t in by):  # an epicyclic loop drives a planet through two meshes
                raise ValueError(f"joint {d!r} is driven by two transmissions ({', '.join(t.name for t in by)})")
        by_name = {p.name: p for p in self.parts}
        for f in self.fluid_volumes:
            for b in [*f.walls, *f.minus]:
                if b not in bodies:
                    raise ValueError(f"fluid volume {f.name} references unknown body {b!r}")
            if f.body is not None and (f.body not in bodies or by_name[f.body].role != "fluid"):
                raise ValueError(f"fluid volume {f.name}: body {f.body!r} must be a part with role fluid")
        for b in self.boundaries:
            if b.body not in bodies:
                raise ValueError(f"boundary {b.name} references unknown body {b.body!r}")
            if b.touching is not None and b.touching not in bodies:
                raise ValueError(f"boundary {b.name} touches unknown body {b.touching!r}")
        for s in self.simulations:
            for c in s.cases:
                if c not in cases:
                    raise ValueError(f"simulation {s.id} references unknown operating case {c!r}")
            for b in s.bodies:
                if b not in bodies:
                    raise ValueError(f"simulation {s.id} references unknown body {b!r}")
            for o in s.outputs:
                if o not in observables:
                    raise ValueError(f"simulation {s.id} outputs unknown observable {o!r}")
        for o in self.observables:
            if o.simulation is not None and o.simulation not in sims:
                raise ValueError(f"observable {o.id} references unknown simulation {o.simulation!r}")
            if o.case is not None and o.case not in cases:
                raise ValueError(f"observable {o.id} references unknown operating case {o.case!r}")
            if o.body is not None and o.body not in bodies:
                raise ValueError(f"observable {o.id} references unknown body {o.body!r}")
            if o.joint is not None and o.joint not in joints:
                raise ValueError(f"observable {o.id} references unknown joint {o.joint!r}")
            if o.motion is not None and o.motion not in {m.name for m in self.acceptance.motions}:
                raise ValueError(f"observable {o.id} references unknown motion {o.motion!r}")
        for cl in self.acceptance.clearances:
            for side in (cl.a, cl.b):
                if side not in bodies | {"all"}:
                    raise ValueError(f"clearance {cl.name} references unknown body {side!r}")
        for m in self.acceptance.motions:
            if m.drive not in joints:
                raise ValueError(f"motion {m.name} drives unknown joint {m.drive!r}")
            for a, b in m.pairs:
                for side in (a, b):
                    if side not in bodies:
                        raise ValueError(f"motion {m.name} pair references unknown body {side!r}")
        return self

    # convenience -----------------------------------------------------------------
    def part(self, name: str) -> AssemblyPart:
        for p in self.parts:
            if p.name == name:
                return p
        raise KeyError(name)

    def joint(self, name: str) -> Joint:
        for j in self.joints:
            if j.name == name:
                return j
        raise KeyError(name)

    def designs(self) -> list[str]:
        """Distinct part designs in declaration order."""
        out: list[str] = []
        for p in self.parts:
            if p.kind == "modelled" and p.design and p.design not in out:
                out.append(p.design)
        return out

    @property
    def bbox_tolerance(self) -> float:
        return self.acceptance.bbox_tolerance or self.envelope.tolerance

    def expected_solids(self) -> int:
        return self.acceptance.solid_count or sum(1 for p in self.parts if p.placed)
