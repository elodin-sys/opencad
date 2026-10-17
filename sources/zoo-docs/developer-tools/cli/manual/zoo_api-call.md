Source URL: https://zoo.dev/docs/developer-tools/cli/manual/zoo_api-call
Title: zoo api-call

# zoo api-call

Perform operations on CAD files.

Perform operations on CAD files.

### Subcommands

* [zoo api-call status](./zoo_api-call_status)

### Options

<dl class="flags">
   <dt><code>-d/--debug</code></dt>
   <dd>Print debug info<br/>Default value: <code>false</code></dd>

   <dt><code>--host</code></dt>
   <dd>Zoo API host to use for all commands (e.g., "api.zoo.dev" or "http://localhost:8888"). Overrides the configured default host</dd>

   <dt><code>-h/--help</code></dt>
   <dd>Print help (see a summary with '-h')</dd>
</dl>


### About


    # convert a step file to an obj file
    $ zoo file convert ./input.step ./output.obj
