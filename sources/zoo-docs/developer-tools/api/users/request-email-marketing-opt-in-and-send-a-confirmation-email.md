Source URL: https://zoo.dev/docs/developer-tools/api/users/request-email-marketing-opt-in-and-send-a-confirmation-email
Title: Request email marketing opt-in and send a confirmation email.

# Request email marketing opt-in and send a confirmation email.

`POST /user/email-marketing-consent/request`

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
curl -X POST "https://api.zoo.dev/user/email-marketing-consent/request" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
