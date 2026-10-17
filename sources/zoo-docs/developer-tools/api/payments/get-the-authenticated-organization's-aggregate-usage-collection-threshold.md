Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-the-authenticated-organization%27s-aggregate-usage-collection-threshold
Title: Get the authenticated organization's aggregate-usage collection threshold.

# Get the authenticated organization's aggregate-usage collection threshold.

`GET /org/billing/usage-collection-threshold`

An endpoint within the Zoo API.

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
curl "https://api.zoo.dev/org/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
