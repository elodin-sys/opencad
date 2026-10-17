Source URL: https://zoo.dev/docs/developer-tools/api/orgs/delete-an-saml-identity-provider
Title: Delete an SAML identity provider.

# Delete an SAML identity provider.

`DELETE /org/saml/idp`

This endpoint requires authentication by an org admin.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

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
curl -X DELETE "https://api.zoo.dev/org/saml/idp" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
