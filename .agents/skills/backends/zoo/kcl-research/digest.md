# Zoo research digest

Five articles at `zoo.dev/research/<slug>`, reduced to what changes how an agent models, exports, or verifies. Cite the slug when a claim matters.

## Engine model (`zoo-cad-engine-overview`)
- B-rep with NURBS as the single primitive: fillets and blends are constrained B-splines, not special surfaces. Uniform primitives keep operations GPU-friendly and avoid the combinatorial cost of mixed representations. Implicit/SDF modelling was rejected: extracting a clean B-rep from a dense grid is costly and scales as N^3 in memory.
- Sweep = section curve C(u) carried along trajectory T(v) with an orientation function M(v). A straight perpendicular trajectory is an extrusion; an arc trajectory is a revolve. Trajectories made of lines and arcs decompose into extrusions and revolutions, each section piece times each path piece becoming one untrimmed face, joined into a manifold solid. Implication: paths built from lines and arcs are cheaper and more robust than free curves; the engine segments paths by curvature so the profile cannot fold over, so keep section size small relative to the tightest bend.
- Patterns are transformation matrices per instance and are moving to GPU instancing: instance count barely affects runtime, so prefer `patternLinear3d`/`patternCircular3d` over repeated function calls for identical bodies.
- Surface-surface intersection (booleans, trims, blends) is GPU brute force: both surfaces are densely sampled, near pairs kept within tolerance, refined by level of detail, thinned in parameter space (medial axis), split into branches, ordered, smoothed and fitted as B-splines. It is approximate by nature and depends on sampling. Implications: `tolerance` arguments on booleans and fillets are real knobs; tangent or coplanar surfaces have degenerate intersections and fail (see known issues); slightly offset tool bodies intersect cleanly.
- CAD-as-a-service by design: the app and the API share one engine surface, so anything Design Studio does is reachable from CLI, MCP, or REST.

## Why KCL is code (`introducing-kcl`)
- The KCL file is the whole model; there is no hidden kernel state. Text gives diffs, review, and merge tooling, and lets LLMs read and write designs.
- Functions are the parametric mechanism: a `gear(module, nTeeth, pressureAngle)` signature documents the driving dimensions; constants defined once flow through calculations.
- KCL is functional and pure: no mutation or loops, replication via patterns and `map`. Purity is what allows click-to-source mapping in the editor and future caching of identical calls.
- Stated goals: readable by engineers who do not code, expressive for experts; constraints were the acknowledged gap (since addressed by KCL 2 sketch blocks).

## File formats: which to emit (`a-practical-overview-of-cad-file-formats`)
- Four tiers by information kept: authoring (`sldprt`, `catpart`, `ipt`, `prt`) > kernel (`x_t`, `sat`, `3dm`) > intermediate B-rep (`step`, `iges`, `jt`, glTF + `KITTYCAD_boundary_representation`) > visual mesh (`stl`, `obj`, `ply`, `gltf`/`glb`, `fbx`, `3mf`).
- Choose STEP for downstream CAD/CAM, simulation, or anything needing exact surfaces and topology; choose a mesh only for rendering, slicing, or FEA preprocessors that tessellate anyway.
- Mesh facts that bite: STL has per-facet normals only and no shared vertices (50 bytes per triangle in binary); OBJ indexes shared vertices and carries per-vertex normals and UVs; PLY is self-describing with variable polygon size (importers triangulate, property names vary); glTF is JSON plus optional binary (`glb` bundles both) and can hold scenes and PBR materials.
- STEP is verbose EXPRESS text with hundreds of entity types (`edge_curve`, `vertex_point`, `b_spline_surface`, `cylindrical_surface`, ...); importers differ in coverage, so round-trip and measure rather than trusting a clean load. IGES surfaces lack reliable topology; STEP superseded it.
- Zoo's glTF B-rep extension stores mesh and exact B-rep together as compact JSON: solids -> shells -> faces (parametric surfaces bounded by loops) -> edges (parametric curves) -> vertices, each reference carrying a same/reverse sense sign.

## Zookeeper and agentic CAD (`zookeeper`)
- Zoo moved from direct text-to-B-rep generation to LLMs writing KCL once KCL became the app's definition of intent. Text-to-CAD (Dec 2023) was already an agent loop; Zookeeper (Design Studio v1.1, Jan 2026) is the conversational form.
- Why generative 3D research rarely ships: CAD is intent-based, feature by feature, and edits must preserve intent; meshes lack precision, editability, and CAM compatibility.
- Zookeeper's loop: plan, call tools, observe, replan. Its differentiating tools mirror what an external agent should use: execute KCL and read errors, search and read documentation, multi-view snapshots, and numeric checks (mass, centre of mass, volume, surface area). Behave the same way: run the model often, look at it from several views, measure.
- Roadmap: image prompts, reverse engineering STEP/STL into parametric KCL, fleets of agents working on separate features.

## Automation vision (`automating-your-workflow`)
- Treat hardware like software: every part in version control, every change triggering real-time checks (mass, centre of gravity, material, cost, manufacturability) and automated data extraction into PLM or Git, with GD&T and drawing checks gating release.
- Text-to-CAD is framed as the blank-canvas accelerator, not the finisher; engineers refine what it produces.
- Mapping to tooling: `zoo kcl analyze`, `zoo kcl export`, `zoo kcl snapshot` and the MCP physical-property tools are the building blocks for these checks.
