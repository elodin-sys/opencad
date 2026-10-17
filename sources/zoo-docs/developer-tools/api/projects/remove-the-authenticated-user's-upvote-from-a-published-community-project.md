Source URL: https://zoo.dev/docs/developer-tools/api/projects/remove-the-authenticated-user%27s-upvote-from-a-published-community-project
Title: Remove the authenticated user's upvote from a published community project.

# Remove the authenticated user's upvote from a published community project.

`DELETE /projects/public/{id}/vote`

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
curl -X DELETE "https://api.zoo.dev/projects/public/{id}/vote" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
