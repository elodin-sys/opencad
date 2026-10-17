Source URL: https://zoo.dev/docs/developer-tools/api/users/create-a-shortlink-for-a-user
Title: Create a shortlink for a user.

# Create a shortlink for a user.

`POST /user/shortlinks`

This endpoint requires authentication by any Zoo user. It creates a shortlink for the user.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | CreateShortlinkRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/shortlinks" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
