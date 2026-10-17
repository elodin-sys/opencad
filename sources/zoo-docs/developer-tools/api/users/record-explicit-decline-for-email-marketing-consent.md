Source URL: https://zoo.dev/docs/developer-tools/api/users/record-explicit-decline-for-email-marketing-consent
Title: Record explicit decline for email marketing consent.

# Record explicit decline for email marketing consent.

`POST /user/email-marketing-consent/decline`

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
curl -X POST "https://api.zoo.dev/user/email-marketing-consent/decline" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
