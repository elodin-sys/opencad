Source URL: https://zoo.dev/docs/developer-tools/api/payments/restore-the-default-for-your-personal-aggregate-usage-collection-threshold
Title: Restore the default for your personal aggregate-usage collection threshold.

# Restore the default for your personal aggregate-usage collection threshold.

`DELETE /user/billing/usage-collection-threshold`

An endpoint within the Zoo API.

## Section

[Payments](/docs/developer-tools/api/payments)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| expected_version | query | integer | yes | Version returned by the read that this mutation is based on. |

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
curl -X DELETE "https://api.zoo.dev/user/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
