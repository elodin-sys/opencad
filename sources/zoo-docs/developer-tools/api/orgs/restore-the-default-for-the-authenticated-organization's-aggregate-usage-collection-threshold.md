Source URL: https://zoo.dev/docs/developer-tools/api/orgs/restore-the-default-for-the-authenticated-organization%27s-aggregate-usage-collection-threshold
Title: Restore the default for the authenticated organization's aggregate-usage collection threshold.

# Restore the default for the authenticated organization's aggregate-usage collection threshold.

`DELETE /org/billing/usage-collection-threshold`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

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
curl -X DELETE "https://api.zoo.dev/org/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
