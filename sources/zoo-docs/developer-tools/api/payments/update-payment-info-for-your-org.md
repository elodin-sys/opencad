Source URL: https://zoo.dev/docs/developer-tools/api/payments/update-payment-info-for-your-org
Title: Update payment info for your org.

# Update payment info for your org.

`PUT /org/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by an org admin. It updates the payment information for the authenticated user's org.

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
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
