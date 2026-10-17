Source URL: https://zoo.dev/docs/developer-tools/api/users/get-the-oauth2-providers-for-your-user
Title: Get the OAuth2 providers for your user.

# Get the OAuth2 providers for your user.

`GET /user/oauth2/providers`

If this returns an empty array, then the user has not connected any OAuth2 providers and uses raw email authentication.

This endpoint requires authentication by any Zoo user. It gets the providers for the authenticated user.

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
curl "https://api.zoo.dev/user/oauth2/providers" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
