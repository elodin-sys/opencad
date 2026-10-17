Source URL: https://zoo.dev/docs/developer-tools/api/users/delete-your-user
Title: Delete your user.

# Delete your user.

`DELETE /user`

This endpoint requires authentication by any Zoo user. It deletes the authenticated user from Zoo's database.

This call will only succeed if all invoices associated with the user have been paid in full and there is no outstanding balance. Personal Factory jobs must be completed or canceled before deleting your account. In-progress jobs owned by an organization do not prevent account deletion.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

No parameters.

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | successful deletion |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/user" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
