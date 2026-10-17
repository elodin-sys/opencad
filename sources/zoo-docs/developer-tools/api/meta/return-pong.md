Source URL: https://zoo.dev/docs/developer-tools/api/meta/return-pong
Title: Return pong.

# Return pong.

`GET /ping`

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
curl "https://api.zoo.dev/ping" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
