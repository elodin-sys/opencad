Source URL: https://zoo.dev/docs/developer-tools/api/users/update-the-user%27s-privacy-settings
Title: Update the user's privacy settings.

# Update the user's privacy settings.

`PUT /user/privacy`

This endpoint requires authentication by any Zoo user. It updates the privacy settings for the user.

## Section

[Users](/docs/developer-tools/api/users)

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
curl -X PUT "https://api.zoo.dev/user/privacy" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
