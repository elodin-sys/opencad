Source URL: https://zoo.dev/docs/developer-tools/api/payments/get-balance-for-your-user
Title: Get balance for your user.

# Get balance for your user.

`GET /user/payment/balance`

This endpoint requires authentication by any Zoo user. It gets the balance information for the authenticated user.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| include_total_due | query | boolean | no | If you would like to return the total due for a user. This makes the API call take longer so it is off by default. |

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
curl "https://api.zoo.dev/user/payment/balance" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
