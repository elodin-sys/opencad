Source URL: https://zoo.dev/docs/developer-tools/api/ml/list-conversations
Title: List conversations

# List conversations

`GET /ml/conversations`

This endpoint requires authentication by any Zoo user. It returns the conversations for the authenticated user.

The conversations are returned in order of creation, with the most recently created conversations first.

## Section

[ML](/docs/developer-tools/api/ml)

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
curl "https://api.zoo.dev/ml/conversations" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
