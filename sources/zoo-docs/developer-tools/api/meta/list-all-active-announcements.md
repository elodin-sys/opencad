Source URL: https://zoo.dev/docs/developer-tools/api/meta/list-all-active-announcements
Title: List all active announcements.

# List all active announcements.

`GET /announcements`

No authentication is required.

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
curl "https://api.zoo.dev/announcements" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
