Source URL: https://zoo.dev/docs/developer-tools/api/orgs/bulk-download-kcl-outputs-for-successful-dataset-conversions
Title: Bulk-download KCL outputs for successful dataset conversions.

# Bulk-download KCL outputs for successful dataset conversions.

`GET /org/datasets/{id}/bulk-download/kcl`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| default |  | */* |

## Example

```bash
curl "https://api.zoo.dev/org/datasets/{id}/bulk-download/kcl" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
