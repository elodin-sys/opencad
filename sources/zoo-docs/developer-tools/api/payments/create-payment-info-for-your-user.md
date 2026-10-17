Source URL: https://zoo.dev/docs/developer-tools/api/payments/create-payment-info-for-your-user
Title: Create payment info for your user.

# Create payment info for your user.

`POST /user/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by any Zoo user. It creates the payment information for the authenticated user.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | BillingInfo |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
