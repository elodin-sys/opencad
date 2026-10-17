Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-your-personal-aggregate-usage-collection-threshold
Title: Get your personal aggregate-usage collection threshold.

# Get your personal aggregate-usage collection threshold.

`GET /user/billing/usage-collection-threshold`

The effective threshold is the amount of accrued, unfunded usage that causes an early invoice before the normal billing-period close.

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
curl "https://api.zoo.dev/user/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
