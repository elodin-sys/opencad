Source URL: https://zoo.dev/docs/developer-tools/api/projects/download-one-of-the-authenticated-user%27s-projects-as-a-tar-archive
Title: Download one of the authenticated user's projects as a tar archive.

# Download one of the authenticated user's projects as a tar archive.

`GET /user/projects/{id}/download`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |
| format | query | ProjectArchiveFormat | no | Archive format to return. Defaults to `tar`. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| default |  | */* |

## Example

```bash
curl "https://api.zoo.dev/user/projects/{id}/download" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
