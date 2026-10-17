Source URL: https://zoo.dev/docs/developer-tools/api/orgs/get-an-org
Title: Get an org.

# Get an org.

`GET /org`

This endpoint requires authentication by an org admin. It gets the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

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
curl "https://api.zoo.dev/org" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
