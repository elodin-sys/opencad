Source URL: https://zoo.dev/docs/developer-tools/api/users/update-a-personal-oauth-app
Title: Update a personal OAuth app.

# Update a personal OAuth app.

`PUT /user/oauth2/apps/{client_id}`

This endpoint requires authentication by any Zoo user. It updates the configuration of the authenticated user's active public OAuth app.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| client_id | path | Uuid | yes | The OAuth client identifier. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateOAuth2AppRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user/oauth2/apps/{client_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
