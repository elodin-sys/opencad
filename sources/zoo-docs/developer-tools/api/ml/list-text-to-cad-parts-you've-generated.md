Source URL: https://zoo.dev/docs/developer-tools/api/ml/list-text-to-cad-parts-you%27ve-generated
Title: List text-to-CAD parts you've generated.

# List text-to-CAD parts you've generated.

`GET /user/text-to-cad`

This will always return the STEP file contents as well as the format the user originally requested.

This endpoint requires authentication by any Zoo user. It returns the text-to-CAD parts for the authenticated user.

The text-to-CAD parts are returned in order of creation, with the most recently created text-to-CAD parts first.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| sort_by | query | CreatedAtSortMode | no |  |
| no_models | query | boolean | no | DEPRECATED: This is the same as `no_parts`, and will be dropped in a future release. Please do not use this. |
| no_parts | query | boolean | no | If we should return the part contents or just the metadata. |
| conversation_id | query | Uuid | no | If specified, only return the prompts for the conversation id given. |

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
curl "https://api.zoo.dev/user/text-to-cad" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
