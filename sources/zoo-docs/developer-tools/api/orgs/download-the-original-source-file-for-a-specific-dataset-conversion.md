Source URL: https://zoo.dev/docs/developer-tools/api/orgs/download-the-original-source-file-for-a-specific-dataset-conversion
Title: Download the original source file for a specific dataset conversion.

# Download the original source file for a specific dataset conversion.

`GET /org/datasets/{id}/conversions/{conversion_id}/original`

An endpoint within the Zoo API.

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
| default |  | */* |

## Example

```bash
curl "https://api.zoo.dev/org/datasets/{id}/conversions/{conversion_id}/original" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
