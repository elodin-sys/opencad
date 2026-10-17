Source URL: https://zoo.dev/docs/api/users/get-your-user
Title: Get your user.

# Get your user.

`GET /user`

Get the user information for the authenticated user.

Alternatively, you can also use the `/users/me` endpoint.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

No parameters.

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
curl "https://api.zoo.dev/user" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
