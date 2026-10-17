Source URL: https://zoo.dev/docs/developer-tools/api/ml/list-the-org-datasets-that-are-currently-attached-to-a-custom-ml-model-owned-by-the-caller%E2%80%99s-organization
Title: List the org datasets that are currently attached to a custom ML model owned by the caller’s organization.

# List the org datasets that are currently attached to a custom ML model owned by the caller’s organization.

`GET /ml/custom/models/{id}/datasets`

An endpoint within the Zoo API.

## Section

[ML](/docs/developer-tools/api/ml)

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
curl "https://api.zoo.dev/ml/custom/models/{id}/datasets" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
