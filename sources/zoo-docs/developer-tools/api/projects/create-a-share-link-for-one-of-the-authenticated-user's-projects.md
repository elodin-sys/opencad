Source URL: https://zoo.dev/docs/developer-tools/api/projects/create-a-share-link-for-one-of-the-authenticated-user%27s-projects
Title: Create a share link for one of the authenticated user's projects.

# Create a share link for one of the authenticated user's projects.

`POST /user/projects/{id}/share-links`

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
| application/json | CreateProjectShareLinkRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/projects/{id}/share-links" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
