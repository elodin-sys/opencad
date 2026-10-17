Source URL: https://zoo.dev/docs/developer-tools/api/payments/create-the-subscription-for-a-user
Title: Create the subscription for a user.

# Create the subscription for a user.

`POST /user/payment/subscriptions`

This endpoint requires authentication by any Zoo user. It creates the subscription for the user.

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
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
