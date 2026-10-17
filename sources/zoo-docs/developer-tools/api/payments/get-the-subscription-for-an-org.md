Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-the-subscription-for-an-org
Title: Get the subscription for an org.

# Get the subscription for an org.

`GET /org/payment/subscriptions`

This endpoint requires authentication by any member of an org. It gets the subscription for the authenticated user's org.

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
curl "https://api.zoo.dev/org/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
