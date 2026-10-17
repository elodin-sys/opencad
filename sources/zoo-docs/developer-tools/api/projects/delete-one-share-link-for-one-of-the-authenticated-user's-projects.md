Source URL: https://zoo.dev/docs/developer-tools/api/projects/delete-one-share-link-for-one-of-the-authenticated-user%27s-projects
Title: Delete one share link for one of the authenticated user's projects.

# Delete one share link for one of the authenticated user's projects.

`DELETE /user/projects/{id}/share-links/{key}`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | Project identifier. |
| key | path | string | yes | Share-link key. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | resource updated |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/user/projects/{id}/share-links/{key}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
