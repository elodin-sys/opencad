Source URL: https://zoo.dev/docs/developer-tools/api/api-tokens/get-an-api-token-for-your-user
Title: Get an API token for your user.

# Get an API token for your user.

`GET /user/api-tokens/{token}`

This endpoint requires authentication by any Zoo user. It returns details of the requested API token for the user.

## Section

[API Tokens](/docs/developer-tools/api/api-tokens)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | path | ApiTokenUuid | yes | The API token. |

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
curl "https://api.zoo.dev/user/api-tokens/{token}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
