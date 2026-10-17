Source URL: https://zoo.dev/docs/developer-tools/api/orgs/return-aggregate-conversion-stats-for-a-dataset-owned-by-the-caller%27s-org
Title: Return aggregate conversion stats for a dataset owned by the caller's org.

# Return aggregate conversion stats for a dataset owned by the caller's org.

`GET /org/datasets/{id}/stats`

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
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/org/datasets/{id}/stats" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
