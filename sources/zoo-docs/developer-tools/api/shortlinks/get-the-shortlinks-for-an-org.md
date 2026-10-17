Source URL: https://zoo.dev/docs/developer-tools/api/shortlinks/get-the-shortlinks-for-an-org
Title: Get the shortlinks for an org.

# Get the shortlinks for an org.

`GET /org/shortlinks`

This endpoint requires authentication by an org admin. It gets the shortlinks for the authenticated user's org.

## Section

[Shortlinks](/docs/developer-tools/api/shortlinks)

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
curl "https://api.zoo.dev/org/shortlinks" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
