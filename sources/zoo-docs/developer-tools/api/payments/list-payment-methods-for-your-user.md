Source URL: https://zoo.dev/docs/developer-tools/api/payments/list-payment-methods-for-your-user
Title: List payment methods for your user.

# List payment methods for your user.

`GET /user/payment/methods`

This endpoint requires authentication by any Zoo user. It lists payment methods for the authenticated user.

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
curl "https://api.zoo.dev/user/payment/methods" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
