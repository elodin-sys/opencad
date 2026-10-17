Source URL: https://zoo.dev/docs/developer-tools/api/orgs/run-semantic-search-across-chunked-conversion-outputs-for-a-dataset
Title: Run semantic search across chunked conversion outputs for a dataset.

# Run semantic search across chunked conversion outputs for a dataset.

`GET /org/datasets/{id}/search/semantic`

This embeds the query text with the org-dataset embedding model and returns top chunk matches ranked by cosine similarity.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |
| q | query | string | yes | Natural-language query text to embed and search. |
| limit | query | integer | no | Max number of matching chunks to return.<br><br>Defaults to 10 and is capped at 100. |

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
curl "https://api.zoo.dev/org/datasets/{id}/search/semantic" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
