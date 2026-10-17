Source URL: https://zoo.dev/docs/developer-tools/api/orgs/list-the-file-conversions-that-have-been-processed-for-a-given-dataset-owned-by-the-caller%27s-org
Title: List the file conversions that have been processed for a given dataset owned by the caller's org.

# List the file conversions that have been processed for a given dataset owned by the caller's org.

`GET /org/datasets/{id}/conversions`

This endpoint returns lightweight conversion summaries only (including `phase`), and intentionally omits converted KCL output and snapshot image payloads for speed. Use the optional `filter` query parameter to filter results (example: `?filter=status:success`). Use `q` to search by conversion id or file path and `phase` to narrow the pipeline stage.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| sort_by | query | ConversionSortMode | no |  |
| filter | query | string | no | Optional filter string for conversions (example: `status:success`). |
| q | query | string | no | Optional search text matched against conversion id or file path. |
| phase | query | string | no | Optional conversion phase filter. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/org/datasets/{id}/conversions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
