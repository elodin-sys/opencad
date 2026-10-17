Source URL: https://zoo.dev/docs/developer-tools/api/payments/update-the-user%27s-subscription
Title: Update the user's subscription.

# Update the user's subscription.

`PUT /user/payment/subscriptions`

This endpoint requires authentication by any Zoo user. It updates the subscription for the user.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | ZooProductSubscriptionsUserRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
