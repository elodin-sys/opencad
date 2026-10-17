Source URL: https://zoo.dev/docs/developer-tools/api/payments/delete-payment-info-for-your-org
Title: Delete payment info for your org.

# Delete payment info for your org.

`DELETE /org/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by an org admin. It deletes the payment information for the authenticated user's org.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

No parameters.

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | successful deletion |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/org/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
