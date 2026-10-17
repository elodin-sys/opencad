Source URL: https://zoo.dev/docs/developer-tools/api/payments/redirect-to-a-fresh-stripe-hosted-payment-method-update-link-for-your-user
Title: Redirect to a fresh Stripe-hosted payment-method update link for your user.

# Redirect to a fresh Stripe-hosted payment-method update link for your user.

`GET /user/payment/method-portal-link`

If the request is not authenticated, this redirects to website login with a callback back to this endpoint. If authenticated, it creates a fresh hosted Stripe portal session and redirects the browser to it.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| return_url | query | string | no | The URL Stripe should offer after the hosted flow completes.<br><br>If omitted, this defaults to the account page. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 302 | Temporary Redirect |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/user/payment/method-portal-link" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
