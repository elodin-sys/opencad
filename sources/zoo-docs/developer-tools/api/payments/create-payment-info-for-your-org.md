Source URL: https://zoo.dev/docs/developer-tools/api/payments/create-payment-info-for-your-org
Title: Create payment info for your org.

# Create payment info for your org.

`POST /org/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by the org admin. It creates the payment information for the authenticated user's org.

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
curl -X POST "https://api.zoo.dev/org/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
