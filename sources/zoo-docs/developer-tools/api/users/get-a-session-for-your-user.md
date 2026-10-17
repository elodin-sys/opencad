Source URL: https://zoo.dev/docs/developer-tools/api/users/get-a-session-for-your-user
Title: Get a session for your user.

# Get a session for your user.

`GET /user/session/{token}`

This endpoint requires authentication by any Zoo user. It returns details of the requested API token for the user.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | path | SessionUuid | yes | The API token. |

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
curl "https://api.zoo.dev/user/session/{token}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
