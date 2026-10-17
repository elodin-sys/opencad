Source URL: https://zoo.dev/docs/developer-tools/api/meta/get-openapi-schema
Title: Get OpenAPI schema.

# Get OpenAPI schema.

`GET /`

An endpoint within the Zoo API.

## Section

[Meta](/docs/developer-tools/api/meta)

## Parameters

No parameters.

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
curl "https://api.zoo.dev/" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
