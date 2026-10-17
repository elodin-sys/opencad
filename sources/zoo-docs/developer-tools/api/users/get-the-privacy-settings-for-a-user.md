Source URL: https://zoo.dev/docs/developer-tools/api/users/get-the-privacy-settings-for-a-user
Title: Get the privacy settings for a user.

# Get the privacy settings for a user.

`GET /user/privacy`

This endpoint requires authentication by any Zoo user. It gets the privacy settings for the user.

## Section

[Users](/docs/developer-tools/api/users)

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
curl "https://api.zoo.dev/user/privacy" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
