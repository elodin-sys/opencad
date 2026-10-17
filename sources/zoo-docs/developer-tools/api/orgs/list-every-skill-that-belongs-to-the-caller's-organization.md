Source URL: https://zoo.dev/docs/developer-tools/api/orgs/list-every-skill-that-belongs-to-the-caller%27s-organization
Title: List every skill that belongs to the caller's organization.

# List every skill that belongs to the caller's organization.

`GET /org/skills`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

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
curl "https://api.zoo.dev/org/skills" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
