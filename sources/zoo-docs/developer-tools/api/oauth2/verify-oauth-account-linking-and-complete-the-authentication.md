Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/verify-oauth-account-linking-and-complete-the-authentication
Title: Verify OAuth account linking and complete the authentication.

# Verify OAuth account linking and complete the authentication.

`GET /oauth2/verify-account-linking`

This endpoint is called when a user clicks the verification link sent to their email after attempting to log in with OAuth when an existing account with the same email was found. This endpoint validates the token, links the OAuth account to the user, and creates a session.

## Section

[Oauth2](/docs/developer-tools/api/oauth2)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | query | string | yes | The verification token from the email |
| callback_url | query | string | no | Optional callback URL to redirect to after verification |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 302 | Temporary Redirect |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/oauth2/verify-account-linking" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
