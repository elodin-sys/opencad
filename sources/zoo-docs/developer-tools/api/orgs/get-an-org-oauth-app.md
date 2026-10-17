Source URL: https://zoo.dev/docs/developer-tools/api/orgs/get-an-org-oauth-app
Title: Get an org OAuth app.

# Get an org OAuth app.

`GET /org/oauth2/apps/{client_id}`

This endpoint requires authentication by an org member. It returns the organization's active public OAuth app by client ID.

## Section

[Orgs](/docs/developer-tools/api/orgs)

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
curl "https://api.zoo.dev/org/oauth2/apps/{client_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
