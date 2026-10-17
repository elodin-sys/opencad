Source URL: https://zoo.dev/docs/developer-tools/api/orgs/fetch-the-metadata-and-converted-output-for-a-single-dataset-conversion
Title: Fetch the metadata and converted output for a single dataset conversion.

# Fetch the metadata and converted output for a single dataset conversion.

`GET /org/datasets/{id}/conversions/{conversion_id}`

Unlike list/search endpoints, this returns the full conversion payload: latest output text plus decoded snapshot image payloads for original, raw-KCL, and salon-KCL stages.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | Dataset identifier. |
| conversion_id | path | Uuid | yes | Conversion identifier. |

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
curl "https://api.zoo.dev/org/datasets/{id}/conversions/{conversion_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
