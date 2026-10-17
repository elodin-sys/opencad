Source URL: https://zoo.dev/docs/developer-tools/api/orgs/fetch-a-single-dataset-by-id-so-long-as-it-belongs-to-the-authenticated-org
Title: Fetch a single dataset by ID so long as it belongs to the authenticated org.

# Fetch a single dataset by ID so long as it belongs to the authenticated org.

`GET /org/datasets/{id}`

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
curl "https://api.zoo.dev/org/datasets/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
