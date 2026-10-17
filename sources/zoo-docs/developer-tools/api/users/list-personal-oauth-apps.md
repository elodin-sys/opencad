Source URL: https://zoo.dev/docs/developer-tools/api/users/list-personal-oauth-apps
Title: List personal OAuth apps.

# List personal OAuth apps.

`GET /user/oauth2/apps`

This endpoint requires authentication by any Zoo user. It lists the authenticated user's active public OAuth apps.

## Section

[Users](/docs/developer-tools/api/users)

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
curl "https://api.zoo.dev/user/oauth2/apps" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
