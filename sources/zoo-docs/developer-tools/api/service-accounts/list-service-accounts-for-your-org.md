Source URL: https://zoo.dev/docs/developer-tools/api/service-accounts/list-service-accounts-for-your-org
Title: List service accounts for your org.

# List service accounts for your org.

`GET /org/service-accounts`

This endpoint requires authentication by an org member. It returns the service accounts for the organization.

The service accounts are returned in order of creation, with the most recently created service accounts first.

## Section

[Service Accounts](/docs/developer-tools/api/service-accounts)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| sort_by | query | CreatedAtSortMode | no |  |

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
curl "https://api.zoo.dev/org/service-accounts" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
