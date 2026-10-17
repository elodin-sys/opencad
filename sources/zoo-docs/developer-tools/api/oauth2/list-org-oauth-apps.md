Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/list-org-oauth-apps
Title: List org OAuth apps.

# List org OAuth apps.

`GET /org/oauth2/apps`

This endpoint requires authentication by an org member. It lists the organization's active public OAuth apps.

## Section

[Oauth2](/docs/developer-tools/api/oauth2)

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
curl "https://api.zoo.dev/org/oauth2/apps" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
