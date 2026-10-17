Source URL: https://zoo.dev/docs/developer-tools/api/projects/move-an-organization-project-back-to-its-creator%27s-personal-library
Title: Move an organization project back to its creator's personal library.

# Move an organization project back to its creator's personal library.

`DELETE /user/projects/{id}/organization`

Organization administrators may perform this move to revoke organization access. The project ID, current revision, files, and version history remain unchanged.

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
| 204 | successful deletion |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/user/projects/{id}/organization" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
