Source URL: https://zoo.dev/docs/developer-tools/api/orgs/add-a-member-to-your-org
Title: Add a member to your org.

# Add a member to your org.

`POST /org/members`

If the user exists, this will add them to your org. If they do not exist, this will create a new user and add them to your org.

In both cases the user gets an email that they have been added to the org.

If the user is already in your org, this will return a 400 and a message.

If the user is already in a different org, this will return a 400 and a message.

This endpoint requires authentication by an org admin. It adds the specified member to the authenticated user's org.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | AddOrgMember |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/members" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
