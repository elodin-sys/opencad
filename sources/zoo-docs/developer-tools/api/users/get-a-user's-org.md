Source URL: https://zoo.dev/docs/developer-tools/api/users/get-a-user%27s-org
Title: Get a user's org.

# Get a user's org.

`GET /user/org`

This endpoint requires authentication by any Zoo user. It gets the authenticated user's org.

If the user is not a member of an org, this endpoint will return a 404.

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
curl "https://api.zoo.dev/user/org" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
