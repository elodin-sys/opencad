Source URL: https://zoo.dev/docs/developer-tools/api/projects/create-a-draft-project-for-the-authenticated-user
Title: Create a draft project for the authenticated user.

# Create a draft project for the authenticated user.

`POST /user/projects`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| multipart/form-data | string |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/projects" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
