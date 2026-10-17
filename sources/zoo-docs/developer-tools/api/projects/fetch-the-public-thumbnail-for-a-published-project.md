Source URL: https://zoo.dev/docs/developer-tools/api/projects/fetch-the-public-thumbnail-for-a-published-project
Title: Fetch the public thumbnail for a published project.

# Fetch the public thumbnail for a published project.

`GET /projects/public/{id}/thumbnail`

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
curl "https://api.zoo.dev/projects/public/{id}/thumbnail" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
