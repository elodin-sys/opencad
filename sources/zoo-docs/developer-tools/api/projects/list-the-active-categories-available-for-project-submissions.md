Source URL: https://zoo.dev/docs/developer-tools/api/projects/list-the-active-categories-available-for-project-submissions
Title: List the active categories available for project submissions.

# List the active categories available for project submissions.

`GET /projects/categories`

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
curl "https://api.zoo.dev/projects/categories" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
