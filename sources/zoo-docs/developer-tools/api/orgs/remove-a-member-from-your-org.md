Source URL: https://zoo.dev/docs/developer-tools/api/orgs/remove-a-member-from-your-org
Title: Remove a member from your org.

# Remove a member from your org.

`DELETE /org/members/{user_id}`

This endpoint requires authentication by an org admin. It removes the specified member from the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| user_id | path | Uuid | yes | The user id of the org member. |

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
curl -X DELETE "https://api.zoo.dev/org/members/{user_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
