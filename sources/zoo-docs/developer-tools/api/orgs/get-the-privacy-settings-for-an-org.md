Source URL: https://zoo.dev/docs/developer-tools/api/orgs/get-the-privacy-settings-for-an-org
Title: Get the privacy settings for an org.

# Get the privacy settings for an org.

`GET /org/privacy`

This endpoint requires authentication by an org admin. It gets the privacy settings for the authenticated user's org.

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
curl "https://api.zoo.dev/org/privacy" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
