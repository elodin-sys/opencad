Source URL: https://zoo.dev/docs/developer-tools/api/orgs/update-the-saml-identity-provider
Title: Update the SAML identity provider.

# Update the SAML identity provider.

`PUT /org/saml/idp`

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
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/saml/idp" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
