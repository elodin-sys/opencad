Source URL: https://zoo.dev/docs/developer-tools/api/orgs/create-an-org
Title: Create an org.

# Create an org.

`POST /org`

This endpoint requires authentication by a Zoo user that is not already in an org. It creates a new org for the authenticated user and makes them an admin.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | OrgDetails |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
