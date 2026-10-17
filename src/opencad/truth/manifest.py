"""Case manifest schema and registry loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from opencad.io import sha256_file
from opencad.paths import TRUTH

Axis = Literal["x", "y", "z"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PinnedFile(Strict):
    path: str = Field(description="relative to the case directory")
    kind: Literal["text", "image", "drawing", "mesh", "table", "cad", "yaml", "other"]
    sha256: str
    units: str | None = None
    note: str = ""


class ReferenceIngest(Strict):
    mesh: str = Field(description="inputs/... mesh path, relative to the case directory")
    units: str
    axes: str | None = None
    datum: str = "min"
    expect_size_mm: list[float] | None = None
    sections: list[str] = Field(default_factory=list, description="extra section planes, e.g. z=3.5")


class ProfileIngest(Strict):
    table: str
    units: str
    sheet: str | None = None
    columns: list[int] = [0, 1]
    sides: list[list[int]] | None = Field(default=None, description="column pairs per side, e.g. [[0,1],[2,3]] for PS then SS listed LE->TE")
    skip: int = 0
    scale_to_mm: float | None = Field(
        default=None,
        description="overrides UNIT_TO_MM[units] when the table is nondimensional (e.g. x/c)",
    )


class Arm(Strict):
    id: str
    design: str = Field(description="designs/<design> produced for this arm")
    mode: Literal["reconstruction", "analysis"] = Field(default="reconstruction", description="machine cases: reconstruction = the worker builds the "
                                                        "geometry from the sources; analysis = the worker is given the reference CAD among its inputs")
    ecr: str | None = Field(default=None, description="change-request label: score results/<design>/ecr/<ecr>/handoff/ instead of the base handoff")
    inputs: list[str] = Field(description="subset of manifest inputs (paths) the agent may see")
    images: list[str] = Field(default_factory=list, description="inputs attached to Codex as images")
    reference: ReferenceIngest | None = None
    profile: ProfileIngest | None = None
    notes: str = ""


class From(Strict):
    file: str = Field(description="truth/... file the value is measured from at score time")
    measure: Literal["bbox_size", "bbox", "volume", "surface_area", "center_of_mass", "section", "mesh"]


class Observable(Strict):
    id: str
    kind: Literal["bbox_size", "volume", "surface_area", "center_of_mass", "section", "face", "deviation", "profile2d", "not_matching", "dimension", "solid_count",
                  "cylinder", "cylinder_count", "plane", "solid", "clearance", "passage", "thickness", "probe", "teeth", "gear_mesh"]
    required: bool = True
    # generic expectation: literal or measured from a truth file
    expected: Any = None
    from_: From | None = Field(default=None, alias="from")
    tolerance: float | None = None
    tolerance_rel: float | None = None
    # section / face / dimension
    plane: Axis | None = None
    at: float | None = None
    normal: Literal["+", "-"] | None = None
    area_tolerance_rel: float | None = None
    center: tuple[float, float] | None = Field(default=None, description="face: in-plane (u,v) centroid")
    mode: Literal["one", "sum"] = Field(default="one", description="face: one assigned face, or explicit sum of every hit")
    # deviation / profile2d / not_matching
    reference: str | None = Field(default=None, description="truth/... mesh, STEP or coordinate table")
    reference_units: str | None = None
    reference_sheet: str | None = None
    reference_sides: list[list[int]] | None = Field(default=None, description="profile2d: column pairs per side of the coordinate table")
    reference_skip: int = 0
    chord_tolerance: float | None = Field(default=None, description="profile2d: chord length tolerance (mm)")
    stagger_tolerance_deg: float | None = Field(default=None, description="profile2d: chord-angle tolerance (deg)")
    chord_definition: Literal["farthest_pair", "landmarks"] = Field(
        default="farthest_pair",
        description="profile2d: farthest sample pair, or first-to-last of side 1 (LE to TE)",
    )
    reference_closed: bool = Field(
        default=True,
        description="profile2d: closed loop (default) or open polyline (one-way distance, no area/chord)",
    )
    reference_scale: float | None = Field(
        default=None,
        description="profile2d: multiply table coordinates by this to get mm, overriding reference_units",
    )
    outer_only: bool = Field(default=False, description="profile2d: compare only the largest closed loop of the section (ignore bores); area is that loop's area")
    p95_max: float | None = None
    hausdorff_max: float | None = None
    silhouette_iou_min: float | None = None
    min_distance: float | None = Field(default=None, description="not_matching: p95 to the wrong reference must exceed this")
    # dimension: bbox extent along an axis, or distance between two named planes
    axis: Axis | None = None
    # cylinder / cylinder_count / plane: an axis (or plane) given by a point and a direction, absolute mm
    point: list[float] | None = Field(default=None, description="cylinder: any point on the axis; plane: a point on the plane")
    direction: list[float] | None = Field(default=None, description="cylinder: axis direction; plane: outward normal; cylinder_count: optional axis filter")
    radius: float | None = Field(default=None, description="cylinder / cylinder_count: nominal radius (mm)")
    radius_tolerance: float | None = Field(default=None, description="cylinder / cylinder_count: radius band (default 0.05 mm)")
    cyl_kind: Literal["hole", "pin", "any"] = Field(default="any", description="cylinder: concave (hole/bore) or convex (pin/boss/shaft)")
    t_range: list[float] | None = Field(default=None, description="cylinder: expected extent along the axis from `point`, to tell stacked coaxial cylinders apart")
    length: float | None = Field(default=None, description="cylinder: expected extent along the axis (mm)")
    length_tolerance: float | None = None
    expected_min: int | None = Field(default=None, description="cylinder_count: at least this many")
    # solid (point = a point inside the body; expected/from = volume); section/profile2d/teeth may be scoped to a solid observable id
    solid: str | None = Field(default=None, description="id of a `solid` observable whose body this check is scoped to")
    # clearance
    a: str | None = Field(default=None, description="clearance / gear_mesh: solid observable id, hardware name, or 'all'")
    b: str | None = None
    min_gap: float | None = None
    max_gap: float | None = None
    # passage
    point_b: list[float] | None = None
    pitch: float | None = None
    seal_radius: float | None = None
    plugs: list[list[list[float]]] | None = None
    expect_connected: bool = True
    volume_min: float | None = None
    volume_max: float | None = None
    # thickness
    stat: Literal["min", "p01", "p05"] | None = None
    min: float | None = Field(default=None, description="thickness: required minimum of `stat`")
    samples: int | None = None
    region: list[list[float]] | None = None
    max_thickness: float | None = None
    # probe
    state: Literal["void", "solid"] | None = None
    points: list[list[float]] | None = None
    # teeth / gear_mesh
    module: float | None = None
    axis_a: list[list[float]] | None = None
    axis_b: list[list[float]] | None = None
    ratio: float | None = None
    pitch_deg: float | None = None
    steps: int | None = None
    backlash_max: float | None = None
    note: str = ""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def _args(self) -> "Observable":
        if self.kind in ("section", "face") and (self.plane is None or self.at is None):
            raise ValueError(f"observable {self.id}: {self.kind} needs plane and at")
        if self.kind == "face" and self.normal is None:
            raise ValueError(f"observable {self.id}: face needs normal")
        if self.kind in ("deviation", "profile2d", "not_matching") and not self.reference:
            raise ValueError(f"observable {self.id}: {self.kind} needs reference")
        if self.kind == "dimension" and self.axis is None:
            raise ValueError(f"observable {self.id}: dimension needs axis")
        if self.kind == "cylinder" and (self.point is None or self.direction is None or self.radius is None):
            raise ValueError(f"observable {self.id}: cylinder needs point, direction and radius")
        if self.kind == "cylinder_count" and (self.radius is None or (self.expected is None and self.expected_min is None)):
            raise ValueError(f"observable {self.id}: cylinder_count needs radius and expected or expected_min")
        if self.kind == "plane" and (self.point is None or self.direction is None):
            raise ValueError(f"observable {self.id}: plane needs point and direction")
        if self.kind == "solid" and self.point is None:
            raise ValueError(f"observable {self.id}: solid needs point (inside the body)")
        if self.kind == "clearance" and (self.a is None or self.b is None):
            raise ValueError(f"observable {self.id}: clearance needs a and b")
        if self.kind == "passage" and (self.point is None or self.point_b is None):
            raise ValueError(f"observable {self.id}: passage needs point and point_b")
        if self.kind == "thickness" and self.min is None:
            raise ValueError(f"observable {self.id}: thickness needs min")
        if self.kind == "probe" and (self.state is None or not self.points):
            raise ValueError(f"observable {self.id}: probe needs state and points")
        if self.kind == "teeth" and (self.point is None or self.direction is None or self.at is None or self.module is None or self.expected is None):
            raise ValueError(f"observable {self.id}: teeth needs point, direction, at, module, expected")
        if self.kind == "gear_mesh" and None in (self.a, self.b, self.axis_a, self.axis_b, self.ratio, self.pitch_deg):
            raise ValueError(f"observable {self.id}: gear_mesh needs a, b, axis_a, axis_b, ratio, pitch_deg")
        for k in ("point", "direction"):
            v = getattr(self, k)
            if v is not None and len(v) != 3:
                raise ValueError(f"observable {self.id}: {k} needs three components")
        return self


class PerformanceObservable(Strict):
    """A measured (A), numerical-reference (N) or analytic (C) value a machine's simulations must predict; X marks a proposed
    extension with no inherited validation (reported, never scored). Scored by z = |pred - ref| / sqrt(u_meas^2 + u_num^2 + u_input^2)
    against `z_max`, or by an absolute `tolerance` when the reference is exact."""

    id: str = Field(description="the contract observable id that must carry the prediction")
    quantity: str
    unit: str
    case: str | None = None
    evidence: Literal["A", "N", "C", "X"]
    status: Literal["available", "unavailable"] = "available"
    value: float | None = None
    series: str | None = Field(default=None, description="truth/... CSV of (x, y) reference points; the prediction must carry a matching series")
    x_column: int = 0
    y_column: int = 1
    skip: int = 1
    uncertainty: float | None = Field(default=None, ge=0, description="standard uncertainty of the reference, same unit")
    u_input: float | None = Field(default=None, ge=0, description="standard uncertainty propagated from the declared inputs")
    z_max: float = Field(default=2.0, gt=0)
    tolerance: float | None = Field(default=None, gt=0, description="absolute band for an exact (analytic) reference")
    digitized: bool = False
    split: Literal["development", "held_out"] = "development"
    required: bool = True
    source: str = ""
    note: str = ""
    where: str = Field(default="", description="where to predict it (a probe station, averaging), shown to the drafter; never a value")

    @model_validator(mode="after")
    def _ref(self) -> "PerformanceObservable":
        if self.status == "available" and self.evidence != "X":
            if self.value is None and self.series is None:
                raise ValueError(f"performance {self.id}: an available reference needs value or series")
            if self.uncertainty is None and self.tolerance is None:
                raise ValueError(f"performance {self.id}: state the reference uncertainty (z-score) or an absolute tolerance")
        return self


class DownstreamTarget(Strict):
    name: str
    value: float
    uncertainty: float | None = None
    units: str = ""
    note: str = ""


class Source(Strict):
    citation: str
    urls: list[str] = Field(default_factory=list)
    accessed: str
    revision: str = ""
    license: str = ""


class CaseManifest(Strict):
    id: str
    title: str
    kind: Literal["part", "machine"] = Field(default="part", description="machine: arms name an assembly; observables score the assembled STEP and "
                                                                         "`performance` scores the simulations")
    truth_class: Literal["A", "B", "C", "D", "E"]
    role: Literal["validation", "calibration"]
    source: Source
    intent: str
    inputs: list[PinnedFile]
    truth: list[PinnedFile]
    arms: list[Arm]
    observables: list[Observable]
    performance: list[PerformanceObservable] = Field(default_factory=list)
    hardware: list[dict[str, Any]] = Field(default_factory=list, description="evaluator-side envelopes (box / cylinder / step) for clearance observables")
    downstream_targets: list[DownstreamTarget] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _refs(self) -> "CaseManifest":
        inputs = {i.path for i in self.inputs}
        truths = {t.path for t in self.truth}
        for a in self.arms:
            for p in a.inputs + a.images:
                if p not in inputs:
                    raise ValueError(f"arm {a.id}: {p} is not a manifest input")
            if a.reference and a.reference.mesh not in inputs:
                raise ValueError(f"arm {a.id}: reference mesh {a.reference.mesh} is not a manifest input")
        for o in self.observables:
            if o.reference and o.reference not in truths:
                raise ValueError(f"observable {o.id}: reference {o.reference} is not a truth file")
            if o.from_ and o.from_.file not in truths:
                raise ValueError(f"observable {o.id}: from.file {o.from_.file} is not a truth file")
        ids = [o.id for o in self.observables]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate observable ids")
        perf = [p.id for p in self.performance]
        if len(set(perf)) != len(perf):
            raise ValueError("duplicate performance ids")
        if self.performance and self.kind != "machine":
            raise ValueError("performance observables belong to machine cases (kind: machine)")
        for p in self.performance:
            if p.series and p.series not in truths:
                raise ValueError(f"performance {p.id}: series {p.series} is not a truth file")
        solids = {o.id for o in self.observables if o.kind == "solid"}
        hardware = {h.get("name") for h in self.hardware}
        for o in self.observables:
            if o.kind == "clearance":
                for side in (o.a, o.b):
                    if side not in solids | hardware | {"all"}:
                        raise ValueError(f"observable {o.id}: clearance body {side!r} is not a solid observable, hardware name or 'all'")
            if o.kind == "gear_mesh" and (o.a not in solids or o.b not in solids):
                raise ValueError(f"observable {o.id}: gear_mesh bodies must be solid observables")
            if o.solid is not None and o.solid not in solids:
                raise ValueError(f"observable {o.id}: solid {o.solid!r} is not a solid observable")
        return self


CLASS_MEANING = {
    "A": "physical measurement of the real object",
    "B": "reference geometry published by the benchmark authors",
    "C": "derived arithmetically from published dimensions",
    "D": "self-consistency only",
    "E": "illustrative",
}


def case_dir(case_id: str) -> Path:
    return TRUTH / "cases" / case_id


def load_manifest(case_id: str) -> CaseManifest:
    p = case_dir(case_id) / "manifest.yaml"
    return CaseManifest.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")))


def load_registry() -> dict[str, Any]:
    p = TRUTH / "registry.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {"cases": []}


def verify_pins(case_id: str, m: CaseManifest) -> list[str]:
    problems = []
    d = case_dir(case_id)
    for group in (m.inputs, m.truth):
        for f in group:
            p = d / f.path
            if not p.exists():
                problems.append(f"{case_id}: missing {f.path}")
            elif sha256_file(p) != f.sha256:
                problems.append(f"{case_id}: sha256 mismatch for {f.path}")
    return problems
