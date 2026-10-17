Source URL: https://zoo.dev/docs/developer-tools/api/users/update-your-user
Title: Update your user.

# Update your user.

`PUT /user`

This endpoint requires authentication by any Zoo user. It updates information about the authenticated user.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateUser |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
