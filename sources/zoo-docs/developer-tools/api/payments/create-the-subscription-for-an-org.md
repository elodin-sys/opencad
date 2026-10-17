Source URL: https://zoo.dev/docs/developer-tools/api/payments/create-the-subscription-for-an-org
Title: Create the subscription for an org.

# Create the subscription for an org.

`POST /org/payment/subscriptions`

This endpoint requires authentication by an org admin. It creates the subscription for the authenticated user's org.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | ZooProductSubscriptionsOrgRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
