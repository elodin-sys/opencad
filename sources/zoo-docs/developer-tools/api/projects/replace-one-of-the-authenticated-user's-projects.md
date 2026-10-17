Source URL: https://zoo.dev/docs/developer-tools/api/projects/replace-one-of-the-authenticated-user%27s-projects
Title: Replace one of the authenticated user's projects.

# Replace one of the authenticated user's projects.

`PUT /user/projects/{id}`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| multipart/form-data | string |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user/projects/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
