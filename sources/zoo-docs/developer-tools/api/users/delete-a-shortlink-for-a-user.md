Source URL: https://zoo.dev/docs/developer-tools/api/users/delete-a-shortlink-for-a-user
Title: Delete a shortlink for a user.

# Delete a shortlink for a user.

`DELETE /user/shortlinks/{key}`

This endpoint requires authentication by any Zoo user. It deletes a shortlink for the user.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The key of the shortlink. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | resource updated |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/user/shortlinks/{key}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
