Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/delete-an-org-oauth-app
Title: Delete an org OAuth app.

# Delete an org OAuth app.

`DELETE /org/oauth2/apps/{client_id}`

This endpoint requires authentication by an org admin. It deactivates the organization's active public OAuth app.

## Section

[Oauth2](/docs/developer-tools/api/oauth2)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| client_id | path | Uuid | yes | The OAuth client identifier. |

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
curl -X DELETE "https://api.zoo.dev/org/oauth2/apps/{client_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
