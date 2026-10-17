Source URL: https://zoo.dev/docs/developer-tools/api/orgs/register-a-new-org-dataset
Title: Register a new org dataset.

# Register a new org dataset.

`POST /org/datasets`

If the dataset lives in S3, call `/org/dataset/s3/policies` first so you can generate the trust, permission, and bucket policies scoped to your dataset before invoking this endpoint.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | CreateOrgDataset |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/datasets" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
