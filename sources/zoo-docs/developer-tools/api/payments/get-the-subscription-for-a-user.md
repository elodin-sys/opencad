Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-the-subscription-for-a-user
Title: Get the subscription for a user.

# Get the subscription for a user.

`GET /user/payment/subscriptions`

This endpoint requires authentication by any Zoo user. It gets the subscription for the user.

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
curl "https://api.zoo.dev/user/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
