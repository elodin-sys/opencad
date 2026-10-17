Source URL: https://zoo.dev/docs/developer-tools/api/payments/update-the-subscription-for-an-org
Title: Update the subscription for an org.

# Update the subscription for an org.

`PUT /org/payment/subscriptions`

This endpoint requires authentication by an org admin. It updates the subscription for the authenticated user's org.

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
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/payment/subscriptions" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
