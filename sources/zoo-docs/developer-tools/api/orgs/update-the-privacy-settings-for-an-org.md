Source URL: https://zoo.dev/docs/developer-tools/api/orgs/update-the-privacy-settings-for-an-org
Title: Update the privacy settings for an org.

# Update the privacy settings for an org.

`PUT /org/privacy`

This endpoint requires authentication by an org admin. It updates the privacy settings for the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | PrivacySettings |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/privacy" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
