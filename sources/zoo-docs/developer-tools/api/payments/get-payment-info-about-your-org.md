Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-payment-info-about-your-org
Title: Get payment info about your org.

# Get payment info about your org.

`GET /org/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by an org admin. It gets the payment information for the authenticated user's org.

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
curl "https://api.zoo.dev/org/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
