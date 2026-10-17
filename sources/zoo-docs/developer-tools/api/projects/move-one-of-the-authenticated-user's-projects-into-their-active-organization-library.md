Source URL: https://zoo.dev/docs/developer-tools/api/projects/move-one-of-the-authenticated-user%27s-projects-into-their-active-organization-library
Title: Move one of the authenticated user's projects into their active organization library.

# Move one of the authenticated user's projects into their active organization library.

`PUT /user/projects/{id}/organization`

This changes only the project's ownership scope. The project ID, current revision, files, and version history remain unchanged so cloud bindings stay valid across the move.

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
curl -X PUT "https://api.zoo.dev/user/projects/{id}/organization" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
