Source URL: https://zoo.dev/docs/developer-tools/api/api-tokens/delete-an-api-token-for-your-user
Title: Delete an API token for your user.

# Delete an API token for your user.

`DELETE /user/api-tokens/{token}`

This endpoint requires authentication by any Zoo user. It deletes the requested API token for the user.

This endpoint does not actually delete the API token from the database. It merely marks the token as invalid. We still want to keep the token in the database for historical purposes.

The token path parameter can be either the full API token (prefixed with `api-`) or the token's unique ID (a UUID).

## Section

[API Tokens](/docs/developer-tools/api/api-tokens)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | path | string | yes | The API token (prefixed with `api-`) or the token's unique ID (a UUID). |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | successful deletion |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/user/api-tokens/{token}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
