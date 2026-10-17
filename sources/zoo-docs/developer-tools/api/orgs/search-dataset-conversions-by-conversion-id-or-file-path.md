Source URL: https://zoo.dev/docs/developer-tools/api/orgs/search-dataset-conversions-by-conversion-id-or-file-path
Title: Search dataset conversions by conversion ID or file path.

# Search dataset conversions by conversion ID or file path.

`GET /org/datasets/{id}/search/conversions`

Supports exact conversion-ID matching and fuzzy file-path matching.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| q | query | string | no | Search text matched against conversion id or file path. |
| sort_by | query | ConversionSortMode | no | Requested sort mode for matched conversions. |
| filter | query | string | no | Optional filter string for conversions (example: `status:success`). |
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
curl "https://api.zoo.dev/org/datasets/{id}/search/conversions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
