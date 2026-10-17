Source URL: https://zoo.dev/docs/developer-tools/api/projects/list-share-links-for-one-of-the-authenticated-user%27s-projects
Title: List share links for one of the authenticated user's projects.

# List share links for one of the authenticated user's projects.

`GET /user/projects/{id}/share-links`

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
curl "https://api.zoo.dev/user/projects/{id}/share-links" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
