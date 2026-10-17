Source URL: https://zoo.dev/docs/developer-tools/cli/manual/zoo_org_dataset_s3-policies
Title: zoo org dataset s3-policies

# zoo org dataset s3-policies

Print IAM policies for onboarding an S3 organization dataset.

Print IAM policies for onboarding an S3 organization dataset.

### Options

<dl class="flags">
   <dt><code>--uri</code></dt>
   <dd>Dataset URI used to scope generated IAM policies</dd>

   <dt><code>--role-arn</code></dt>
   <dd>IAM role ARN Zoo should assume when reading the dataset</dd>

   <dt><code>--output-dir</code></dt>
   <dd>Write trust-policy.json, permission-policy.json, and bucket-policy.json to this directory</dd>

   <dt><code>-f/--format</code></dt>
   <dd>Command output format<br/>Possible values: <code>json | yaml | table</code></dd>

   <dt><code>-d/--debug</code></dt>
   <dd>Print debug info<br/>Default value: <code>false</code></dd>

   <dt><code>--host</code></dt>
   <dd>Zoo API host to use for all commands (e.g., "api.zoo.dev" or "http://localhost:8888"). Overrides the configured default host</dd>

   <dt><code>-h/--help</code></dt>
   <dd>Print help</dd>
</dl>


### See also

* [zoo org](./zoo_org)
* [zoo org dataset](./zoo_org_dataset)
