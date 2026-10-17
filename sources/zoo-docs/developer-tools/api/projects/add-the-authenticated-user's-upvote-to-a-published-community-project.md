Source URL: https://zoo.dev/docs/developer-tools/api/projects/add-the-authenticated-user%27s-upvote-to-a-published-community-project
Title: Add the authenticated user's upvote to a published community project.

# Add the authenticated user's upvote to a published community project.

`POST /projects/public/{id}/vote`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

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
curl -X POST "https://api.zoo.dev/projects/public/{id}/vote" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
