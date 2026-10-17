Source URL: https://zoo.dev/docs/developer-tools/api/orgs/list-members-of-your-org
Title: List members of your org.

# List members of your org.

`GET /org/members`

This endpoint requires authentication by an org admin. It lists the members of the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| sort_by | query | CreatedAtSortMode | no |  |
| role | query | UserOrgRole | no | The organization role to filter by. |

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
curl "https://api.zoo.dev/org/members" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
