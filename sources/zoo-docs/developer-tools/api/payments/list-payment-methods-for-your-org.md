Source URL: https://zoo.dev/docs/developer-tools/api/payments/list-payment-methods-for-your-org
Title: List payment methods for your org.

# List payment methods for your org.

`GET /org/payment/methods`

This endpoint requires authentication by an org admin. It lists payment methods for the authenticated user's org.

## Section

[Payments](/docs/developer-tools/api/payments)

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
curl "https://api.zoo.dev/org/payment/methods" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
