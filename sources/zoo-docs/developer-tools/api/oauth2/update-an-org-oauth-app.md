Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/update-an-org-oauth-app
Title: Update an org OAuth app.

# Update an org OAuth app.

`PUT /org/oauth2/apps/{client_id}`

This endpoint requires authentication by an org admin. It updates the configuration of the organization's active public OAuth app.

## Section

[Oauth2](/docs/developer-tools/api/oauth2)

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
curl -X PUT "https://api.zoo.dev/org/oauth2/apps/{client_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
