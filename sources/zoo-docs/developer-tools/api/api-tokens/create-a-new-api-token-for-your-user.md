Source URL: https://zoo.dev/docs/developer-tools/api/api-tokens/create-a-new-api-token-for-your-user
Title: Create a new API token for your user.

# Create a new API token for your user.

`POST /user/api-tokens`

This endpoint requires authentication by any Zoo user. It creates a new API token for the authenticated user.

## Section

[API Tokens](/docs/developer-tools/api/api-tokens)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| label | query | string | no | An optional label for the API token. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/api-tokens" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
