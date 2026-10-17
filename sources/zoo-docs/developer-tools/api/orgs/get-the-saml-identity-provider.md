Source URL: https://zoo.dev/docs/developer-tools/api/orgs/get-the-saml-identity-provider
Title: Get the SAML identity provider.

# Get the SAML identity provider.

`GET /org/saml/idp`

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
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/org/saml/idp" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
