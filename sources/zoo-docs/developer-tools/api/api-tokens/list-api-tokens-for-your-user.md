Source URL: https://zoo.dev/docs/developer-tools/api/api-tokens/list-api-tokens-for-your-user
Title: List API tokens for your user.

# List API tokens for your user.

`GET /user/api-tokens`

This endpoint requires authentication by any Zoo user. It returns the API tokens for the authenticated user.

The API tokens are returned in order of creation, with the most recently created API tokens first.

## Section

[API Tokens](/docs/developer-tools/api/api-tokens)

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
curl "https://api.zoo.dev/user/api-tokens" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
