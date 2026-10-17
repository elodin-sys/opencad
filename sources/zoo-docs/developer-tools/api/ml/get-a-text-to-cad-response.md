Source URL: https://zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response
Title: Get a text-to-CAD response.

# Get a text-to-CAD response.

`GET /user/text-to-cad/{id}`

This endpoint requires authentication by any Zoo user. The user must be the owner of the text-to-CAD model.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The id of the model to give feedback to. |

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
curl "https://api.zoo.dev/user/text-to-cad/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
