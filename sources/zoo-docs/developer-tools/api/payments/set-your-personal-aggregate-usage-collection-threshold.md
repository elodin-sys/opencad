Source URL: https://zoo.dev/docs/developer-tools/api/payments/set-your-personal-aggregate-usage-collection-threshold
Title: Set your personal aggregate-usage collection threshold.

# Set your personal aggregate-usage collection threshold.

`PUT /user/billing/usage-collection-threshold`

An endpoint within the Zoo API.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | AggregateUsageCollectionThresholdSet |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
