Source URL: https://zoo.dev/docs/developer-tools/api/payments/delete-payment-info-for-your-user
Title: Delete payment info for your user.

# Delete payment info for your user.

`DELETE /user/payment`

This includes billing address, phone, and name.

This endpoint requires authentication by any Zoo user. It deletes the payment information for the authenticated user.

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
curl -X DELETE "https://api.zoo.dev/user/payment" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
