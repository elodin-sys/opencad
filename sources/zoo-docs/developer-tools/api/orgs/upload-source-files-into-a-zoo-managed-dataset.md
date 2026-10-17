Source URL: https://zoo.dev/docs/developer-tools/api/orgs/upload-source-files-into-a-zoo-managed-dataset
Title: Upload source files into a Zoo-managed dataset.

# Upload source files into a Zoo-managed dataset.

`POST /org/datasets/{id}/uploads`

This endpoint accepts `multipart/form-data` where each file part becomes a source object in the dataset. Exact `<proprietary CAD filename>.json` converter dumps are also accepted and associated with their original CAD file. Paths are normalized and must be relative.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| multipart/form-data | string |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 202 | successfully enqueued operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/datasets/{id}/uploads" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
