Source URL: https://zoo.dev/docs/developer-tools/api/users/get-a-personal-oauth-app
Title: Get a personal OAuth app.

# Get a personal OAuth app.

`GET /user/oauth2/apps/{client_id}`

This endpoint requires authentication by any Zoo user. It returns the authenticated user's active public OAuth app by client ID.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| client_id | path | Uuid | yes | The OAuth client identifier. |

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
curl "https://api.zoo.dev/user/oauth2/apps/{client_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
