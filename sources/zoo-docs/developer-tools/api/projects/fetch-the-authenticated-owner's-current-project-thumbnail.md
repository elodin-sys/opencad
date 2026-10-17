Source URL: https://zoo.dev/docs/developer-tools/api/projects/fetch-the-authenticated-owner%27s-current-project-thumbnail
Title: Fetch the authenticated owner's current project thumbnail.

# Fetch the authenticated owner's current project thumbnail.

`GET /user/projects/{id}/thumbnail`

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
| default |  | */* |

## Example

```bash
curl "https://api.zoo.dev/user/projects/{id}/thumbnail" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
