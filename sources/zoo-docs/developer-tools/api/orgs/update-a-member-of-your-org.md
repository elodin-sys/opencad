Source URL: https://zoo.dev/docs/developer-tools/api/orgs/update-a-member-of-your-org
Title: Update a member of your org.

# Update a member of your org.

`PUT /org/members/{user_id}`

This endpoint requires authentication by an org admin. It updates the specified member of the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| user_id | path | Uuid | yes | The user id of the org member. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateMemberToOrgBody |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/members/{user_id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
