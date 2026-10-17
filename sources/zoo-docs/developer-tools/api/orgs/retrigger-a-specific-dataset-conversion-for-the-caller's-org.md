Source URL: https://zoo.dev/docs/developer-tools/api/orgs/retrigger-a-specific-dataset-conversion-for-the-caller%27s-org
Title: Retrigger a specific dataset conversion for the caller's org.

# Retrigger a specific dataset conversion for the caller's org.

`POST /org/datasets/{id}/conversions/{conversion_id}/retrigger`

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
| 204 | resource updated |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/datasets/{id}/conversions/{conversion_id}/retrigger" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
