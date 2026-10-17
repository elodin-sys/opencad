Source URL: https://zoo.dev/docs/developer-tools/api/payments/list-invoices-for-your-org
Title: List invoices for your org.

# List invoices for your org.

`GET /org/payment/invoices`

This endpoint requires authentication by an org admin. It lists invoices for the authenticated user's org.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |

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
curl "https://api.zoo.dev/org/payment/invoices" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
