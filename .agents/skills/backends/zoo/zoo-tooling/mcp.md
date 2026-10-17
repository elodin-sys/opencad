# Zoo MCP

Server `zoo-mcp` (KittyCAD/mcp, Python 3.11-3.13). Run `uvx zoo-mcp` with `ZOO_API_TOKEN` in the environment; client config = command `uvx`, args `["zoo-mcp"]`, env `ZOO_API_TOKEN`, cwd = the design project. Prebuilt binaries on GitHub releases. No MCP fee, but hosted tools bill as API usage.
Codex: `codex -c 'mcp_servers.zoo.command="uvx"' -c 'mcp_servers.zoo.args=["zoo-mcp"]' -c mcp_servers.zoo.env.ZOO_API_TOKEN="$ZOO_API_TOKEN"`. Claude Code: `claude mcp add --scope project "Zoo-MCP" uv -- --directory "$PWD"/src/zoo_mcp run server.py`.

## Sessions
At most one persistent modeling session per server process. `get_modeling_sessions` recovers its id after a reconnect; otherwise `start_modeling_session`. Populate it with `execute_kcl`, `exec_kcl_project`, or `import_cad_file`; pass the same `session_id` to `snapshot` and scene-query tools; `stop_modeling_session` when done.
Session executions save an artifact graph (JSON path returned); sessionless `execute_kcl` has no artifact graph and more network overhead. Snapshots are orthographic, so on-image measurements are undistorted.

## Conventions
Tools with `kcl_code?, kcl_path?` need exactly one; `kcl_path` is a `.kcl` file or a directory holding `main.kcl`. Unit strings: length `mm cm m in ft yd`, mass `g kg lb`, density `kg:m3 lb:ft3`, area/volume `mm2 cm3` style. Export/convert formats: `fbx glb gltf obj ply step stl` (import also `sldprt`, `stp`). Failures may come back as strings: check the returned type before trusting a result.
`mock_execute_kcl` runs the interpreter without the engine: syntax, types, and `assert` fail fast, but face-dependent std code (`hole::*`, sketch-on-face queries) reports "The engine isn't available"; use `execute_kcl` for those. `lint_and_fix_kcl(kcl_path = dir)` rewrites files in place; pass `kcl_code` to keep sources untouched. `snapshot` with a `camera_view` list writes one composite `image.jpg` when `output_path` is a directory.

## Tools (46): `name(params)` -> return: purpose. `?` = optional.

### Execute and check KCL
- `execute_kcl(kcl_code?, kcl_path?, session_id?)` -> `ResultZooExecuteKcl`: Execute KCL code.
- `exec_kcl_project(session_id, kcl_code?, kcl_path?)` -> `str`: Run a KCL project on the server side and save its artifact graph.
- `format_kcl(kcl_code?, kcl_path?)` -> `str`: Format KCL code.
- `get_sketch_constraint_status(kcl_code?, kcl_path?)` -> `dict | str`: Execute KCL and return a report of sketch constraint status.
- `visualize_sketch(sketch_name, kcl_code?, kcl_path?, output_path?)` -> `ImageContent | str`: Render a named 2D KCL sketch as a solver-debug PNG.
- `lint_and_fix_kcl(kcl_code?, kcl_path?)` -> `tuple[str, list[str]]`: Lint and fix KCL code.
- `mock_execute_kcl(kcl_code?, kcl_path?)` -> `tuple[bool, str]`: Mock execute KCL code.

### Modeling sessions
- `start_modeling_session()` -> `str`: Open an empty modeling websocket for subsequent tools.
- `get_modeling_sessions()` -> `list[str]`: List modeling sessions owned by the current MCP server process.
- `import_cad_file(session_id, input_file)` -> `str`: Import a CAD file into an existing modeling session.
- `stop_modeling_session(session_id)` -> `None`: Close a persistent modeling websocket session.

### Export and convert
- `convert_cad_file(input_file, export_path, export_format)` -> `str`: Convert a CAD file from one format to another CAD file format.
- `export_kcl(kcl_code?, kcl_path?, export_path?, export_format?)` -> `str`: Export KCL code to a CAD file.

### Physical properties
- `calculate_center_of_mass(input_file, unit_length)` -> `dict | str`: Calculate the center of mass of a 3d object represented by the input file.
- `calculate_mass(input_file, unit_mass, unit_density, density)` -> `float | str`: Calculate the mass of a 3d object represented by the input file.
- `calculate_surface_area(input_file, unit_area)` -> `float | str`: Calculate the surface area of a 3d object represented by the input file.
- `calculate_volume(input_file, unit_volume)` -> `float | str`: Calculate the volume of a 3d object represented by the input file.
- `calculate_cad_physical_properties(input_file, unit_length, unit_mass, unit_density, density, unit_area, unit_volume)` -> `dict | str`: Calculate physical properties (volume, mass, surface area, center of mass, bounding box) of a CAD file.
- `calculate_kcl_physical_properties(kcl_code?, kcl_path?, unit_length?, unit_mass?, unit_density?, density?, unit_area?, unit_volume?)` -> `dict | str`
- `calculate_bounding_box_kcl(unit_length, kcl_code?, kcl_path?)` -> `dict | str`: Calculate the bounding box of a KCL model.
- `calculate_bounding_box_cad(input_file)` -> `dict | str`: Calculate the bounding box of a CAD file.

### Snapshots and images
- `snapshot(session_id, camera_view?, zoom?, highlight_edges?, max_image_dimension?, padding?, output_path?)` -> `ImageContent | str`: Render an open modeling session as an image.
- `save_image(image, output_path?)` -> `str`: Save an ImageContent object to disk.

### Scene queries (need a session)
- `get_face_info(face_id, session_id)` -> `FaceInfo`: Get the position, gradient, normal, and center of a face in a modeling session.
- `entity_distance(entity_id1, entity_id2, session_id, on_axis?)` -> `EntityGetDistance`: Get the minimum and maximum distance between two model entities.
- `set_selection_filter(entity_types, session_id)` -> `SetSelectionFilter`: Set which model entity types can be added to the "selection set".
- `select_entities(entity_ids, session_id)` -> `SelectReplace`: Replace the "selection set" with the given entities.
- `center_camera_on_selection(session_id, move_vantage?)` -> `DefaultCameraCenterToSelection`: Point the camera at the current "selection set".
- `highlight_set_entities(entity_ids, session_id)` -> `HighlightSetEntities`: Replace the currently highlighted entities.
- `curve_get_end_points(curve_id, session_id)` -> `CurveGetEndPoints`: Get the start and end points of a curve entity.
- `engine_util_evaluate_path(path_json, t, session_id)` -> `EngineUtilEvaluatePath`: Evaluate a serialized KCL path at parameter t.
- `curve_get_type(curve_id, session_id)` -> `CurveGetType`: Get whether a curve is a line, arc, or NURBS curve.
- `edge_get_length(edge_id, session_id)` -> `EdgeGetLength`: Get the length of an edge entity in the current scene units.
- `entity_get_all_child_uuids(entity_id, session_id)` -> `EntityGetAllChildUuids`: Get all child UUIDs belonging to an entity.
- `entity_get_index(entity_id, session_id)` -> `EntityGetIndex`: Get an entity's index within its parent.
- `entity_get_parent_id(entity_id, session_id)` -> `EntityGetParentId`: Get the UUID of an entity's parent.
- `entity_get_sketch_paths(entity_id, session_id)` -> `EntityGetSketchPaths`: Get the sketch path UUIDs belonging to an entity.

### Docs and samples lookup
- `list_kcl_docs()` -> `dict | str`: List all available KCL documentation topics organized by category.
- `search_kcl_docs(query, max_results?)` -> `list[dict] | str`: Search KCL documentation by keyword.
- `get_kcl_doc(doc_path)` -> `str`: Get the full content of a specific KCL documentation file.
- `list_kcl_samples()` -> `list[dict] | str`: List all available KCL sample projects.
- `search_kcl_samples(query, max_results?)` -> `list[dict] | str`: Search KCL samples by keyword.
- `get_kcl_sample(sample_name)` -> `SampleData | str`: Get the full content of a specific KCL sample including all files.

### Org datasets and skills
- `list_org_datasets()` -> `list[dict] | str`: List the datasets available to the user's organization.
- `list_org_skills()` -> `list[dict] | str`: List the skills available to the user's organization.
- `search_org_dataset_semantic(dataset_id, query, limit?)` -> `list[dict] | str`: Semantic-search a dataset for samples relevant to the query.
