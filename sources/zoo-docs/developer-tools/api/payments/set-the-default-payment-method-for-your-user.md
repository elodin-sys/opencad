Source URL: https://zoo.dev/docs/developer-tools/api/payments/set-the-default-payment-method-for-your-user
Title: Set the default payment method for your user.

# Set the default payment method for your user.

`POST /user/payment/methods/{id}/default`

This endpoint requires authentication by any Zoo user. It sets the default payment method for the authenticated user.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | Stripe payment method identifier. |

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
curl -X POST "https://api.zoo.dev/user/payment/methods/{id}/default" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
