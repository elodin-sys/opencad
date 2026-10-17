Source URL: https://zoo.dev/docs/developer-tools/api/orgs/list-every-dataset-that-belongs-to-the-caller%27s-organization
Title: List every dataset that belongs to the caller's organization.

# List every dataset that belongs to the caller's organization.

`GET /org/datasets`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| lookup_enabled | query | boolean | no | When set, only return datasets with the matching lookup setting. |
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
curl "https://api.zoo.dev/org/datasets" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
