Source URL: https://zoo.dev/docs/developer-tools/api/api-calls/list-api-calls-for-your-user
Title: List API calls for your user.

# List API calls for your user.

`GET /user/api-calls`

This endpoint requires authentication by any Zoo user. It returns the API calls for the authenticated user.

The API calls are returned in order of creation, with the most recently created API calls first.

## Section

[API Calls](/docs/developer-tools/api/api-calls)

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
curl "https://api.zoo.dev/user/api-calls" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
