Source URL: https://zoo.dev/docs/developer-tools/api/ml/give-feedback-to-a-specific-ml-response
Title: Give feedback to a specific ML response.

# Give feedback to a specific ML response.

`POST /user/text-to-cad/{id}`

This can be a text-to-CAD creation or iteration.

This endpoint requires authentication by any Zoo user. The user must be the owner of the ML response, in order to give feedback.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The id of the model to give feedback to. |
| feedback | query | MlFeedback | yes | The feedback. |

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
curl -X POST "https://api.zoo.dev/user/text-to-cad/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
