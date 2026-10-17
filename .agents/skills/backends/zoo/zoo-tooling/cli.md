# zoo CLI

Auth: `ZOO_API_TOKEN` env var (takes precedence) or `zoo auth login`; `ZOO_HOST`/`--host` for another API host.
Every command accepts `-d/--debug`, `-h`; API commands add `-f/--format json|yaml|table`, `--show-trace`, and `--allow-errors` (continue past non-fatal KCL problems; never for acceptance builds).
`<input>` is a `.kcl` file, a directory with `main.kcl`, or `-` for stdin; execution settings come from the nearest `project.toml`.
Manual: `zoo.dev/docs/developer-tools/cli/manual/zoo_<sub>_<cmd>`.

## zoo kcl
### `zoo kcl analyze`: Analyze multiple physical properties of objects in a kcl file.
- `--material-density (default 1)`: How dense is the material?
- `--material-density-unit (default kg:m3)`: What units are `material-density` measured in?
- `--volume-output-unit (default m3)`: What units do you want volumes shown in?
- `--mass-output-unit (default kg)`: What units do you want masses shown in?
- `--density-output-unit (default kg:m3)`: What units do you want densities shown in?
- `--surface-area-output-unit (default m2)`: What units do you want areas shown in?
- `--center-of-mass-output-unit (default m)`: What units do you want lengths shown in?
### `zoo kcl bounding-box`: Get the bounding box that contains everything in a KCL file.
- `-u/--output-unit`: Output unit
### `zoo kcl center-of-mass`: Get the center of mass of objects in a kcl file.
- `-u/--output-unit`: Output unit
### `zoo kcl density`: Get the density of objects in a kcl file.
- `-m/--material-mass`: Material mass
- `--material-mass-unit`: The unit of the material mass
- `-u/--output-unit`: Output unit
### `zoo kcl export`: Export a `kcl` file as any other supported CAD file format.
- `<output-dir>`: The path to a directory to output the files
- `-t/--output-format fbx|glb|gltf|obj|ply|step|stl`: A valid output file format
- `--deterministic`: If true, the output file should be deterministic, meaning any date or time information will be replaced with a fixed value
### `zoo kcl format`: Format a `kcl` file.
- `-w/--write`: Write the output back to the original file
- `-t/--tab-size (default 2)`: Size of a tab in spaces
- `--use-tabs`: Prefer tabs over spaces
- `--insert-final-newline (default true)`: How to handle the final newline in the file
### `zoo kcl lint`: Lint a KCL file for style issues.
- `--descriptions`: Print a long-form description of what the issue is, and the rational behind why
- `-s/--show-code`: Show where the offending KCL source code is
### `zoo kcl mass`: Get the mass of objects in a kcl file.
- `-m/--material-density`: Material density
- `--material-density-unit`: Material density unit
- `-u/--output-unit`: Output unit
### `zoo kcl snapshot`: Snapshot a render of a `kcl` file as any supported image format.
- `<output-file>`: The path to a file to output the image
- `-t/--output-format png|jpeg`: A valid output image format
- `--session`: If given, this command will reuse an existing KittyCAD modeling session
- `--replay`: If true, tell engine to store a replay
- `--angle front|top|right-side|four-ways|iso`: Which angle to take the snapshot from
- `--camera-style ortho|perspective`: Which style of camera to use for snapshots
- `--camera-padding (default 0.1)`: How much padding to use when zooming before the screenshot
### `zoo kcl surface-area`: Get the surface area of objects in a kcl file.
- `-u/--output-unit`: Output unit
### `zoo kcl view`: View a render of a `kcl` file in your terminal.
- `--angle front|top|right-side|four-ways|iso`: Which angle to take the snapshot from
- `--camera-style ortho|perspective`: Which style of camera to use for snapshots
- `--camera-padding (default 0.1)`: How much padding to use when zooming before the screenshot
### `zoo kcl volume`: Get the volume of an object in a kcl file.
- `-u/--output-unit`: Output unit

## Other commands
- `zoo alias` Create command shortcuts: `zoo alias delete` Delete an alias; `zoo alias list` List your aliases; `zoo alias set` Create a shortcut for a `zoo` command
- `zoo api` Makes an authenticated HTTP request to the Zoo API and…
- `zoo api-call` Perform operations on CAD files: `zoo api-call status` Perform operations for API calls
- `zoo app` Open a directory or file in the Zoo Design Studio…
- `zoo auth` Login, logout, and get the status of your authentication: `zoo auth login` Authenticate with an Zoo host; `zoo auth logout` Log out of an Zoo host; `zoo auth status`
- `zoo completion` Generate shell completion scripts
- `zoo config` Manage configuration for `zoo`: `zoo config get`; `zoo config list`; `zoo config set`
- `zoo file` Perform operations on CAD files: `zoo file center-of-mass`; `zoo file convert`; `zoo file density`; `zoo file mass`; `zoo file snapshot`; `zoo file surface-area`; `zoo file volume`
- `zoo generate` Generate various documentation files for the `zoo` command line: `zoo generate markdown` Generate markdown documentation
- `zoo ml` Perform machine learning (ML-Ephant) commands: `zoo ml kcl` KCL machine learning commands; `zoo ml kcl copilot`
- `zoo org` Manage Zoo organization resources: `zoo org dataset` Manage organization datasets; `zoo org dataset conversion` Manage one organization dataset conversion; `zoo org dataset conversion artifact` Write a conversion artifact; `zoo org dataset conversion download-original`; `zoo org dataset conversion kcl`; `zoo org dataset conversion retrigger` Retrigger one organization dataset conversion; `zoo org dataset conversion view` View a single organization dataset conversion; `zoo org dataset conversions`; `zoo org dataset conversions list` List conversions for an organization dataset; `zoo org dataset conversions search`; `zoo org dataset create` Create an organization dataset; `zoo org dataset delete` Delete an organization dataset; `zoo org dataset list` List organization datasets; `zoo org dataset retrigger` Retrigger conversions for an organization dataset; `zoo org dataset s3-policies`; `zoo org dataset semantic-search`; `zoo org dataset stats`; `zoo org dataset update` Update organization dataset metadata or storage credentials; `zoo org dataset upload` Upload files into a Zoo-managed organization dataset; `zoo org dataset view` View an organization dataset
- `zoo project` Manage Zoo projects: `zoo project categories`; `zoo project delete` Delete one of your uploaded projects; `zoo project download`; `zoo project list` List your projects; `zoo project publish`; `zoo project upload` Upload a local project; `zoo project view` View one of your projects
- `zoo say` Prints your text in a text bubble with Zoo as…
- `zoo start-session` Starts a modeling session
- `zoo open` Shortcut to open the Zoo documentation…
- `zoo update` Update the current running binary to the latest version
- `zoo user` Edit and view your user: `zoo user delete` Delete user; `zoo user edit` Edit user settings; `zoo user view` View user
- `zoo version` Prints the version of the program
- `zoo kcl` see above
