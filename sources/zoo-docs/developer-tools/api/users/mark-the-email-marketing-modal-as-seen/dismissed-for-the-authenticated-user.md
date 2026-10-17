Source URL: https://zoo.dev/docs/developer-tools/api/users/mark-the-email-marketing-modal-as-seen/dismissed-for-the-authenticated-user
Title: Mark the email-marketing modal as seen/dismissed for the authenticated user.

# Mark the email-marketing modal as seen/dismissed for the authenticated user.

`POST /user/email-marketing-consent/seen`

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
| 204 | successful operation, no content |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/email-marketing-consent/seen" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
