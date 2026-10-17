Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/create-a-personal-oauth-app
Title: Create a personal OAuth app.

# Create a personal OAuth app.

`POST /user/oauth2/apps`

This endpoint requires authentication by any Zoo user. It creates an active public OAuth app owned by the authenticated user.

## Section

[Oauth2](/docs/developer-tools/api/oauth2)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | CreateOAuth2AppRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/oauth2/apps" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
