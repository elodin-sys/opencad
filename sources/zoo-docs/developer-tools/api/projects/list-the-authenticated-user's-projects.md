Source URL: https://zoo.dev/docs/developer-tools/api/projects/list-the-authenticated-user%27s-projects
Title: List the authenticated user's projects.

# List the authenticated user's projects.

`GET /user/projects`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

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
curl "https://api.zoo.dev/user/projects" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
