Source URL: https://zoo.dev/docs/developer-tools/api/orgs/create-a-saml-identity-provider
Title: Create a SAML identity provider.

# Create a SAML identity provider.

`POST /org/saml/idp`

This endpoint requires authentication by an org admin.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | SamlIdentityProviderCreate |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/saml/idp" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
