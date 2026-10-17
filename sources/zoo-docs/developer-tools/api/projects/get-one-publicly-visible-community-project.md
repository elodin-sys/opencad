Source URL: https://zoo.dev/docs/developer-tools/api/projects/get-one-publicly-visible-community-project
Title: Get one publicly visible community project.

# Get one publicly visible community project.

`GET /projects/public/{id}`

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
curl "https://api.zoo.dev/projects/public/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
