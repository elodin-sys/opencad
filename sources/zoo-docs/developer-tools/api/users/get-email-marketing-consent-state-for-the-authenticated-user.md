Source URL: https://zoo.dev/docs/developer-tools/api/users/get-email-marketing-consent-state-for-the-authenticated-user
Title: Get email marketing consent state for the authenticated user.

# Get email marketing consent state for the authenticated user.

`GET /user/email-marketing-consent`

An endpoint within the Zoo API.

## Section

[Users](/docs/developer-tools/api/users)

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
curl "https://api.zoo.dev/user/email-marketing-consent" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
