Source URL: https://zoo.dev/docs/developer-tools/api/ml/update-mutable-metadata-%28name%2C-system-prompt%29-for-a-custom-ml-model-owned-by-the-caller%27s-organization
Title: Update mutable metadata (name, system prompt) for a custom ML model owned by the caller's organization.

# Update mutable metadata (name, system prompt) for a custom ML model owned by the caller's organization.

`PUT /ml/custom/models/{id}`

An endpoint within the Zoo API.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateCustomModel |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/ml/custom/models/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
