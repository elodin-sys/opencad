Source URL: https://zoo.dev/docs/developer-tools/api/projects/submit-one-of-the-authenticated-user%27s-projects-for-public-review
Title: Submit one of the authenticated user's projects for public review.

# Submit one of the authenticated user's projects for public review.

`POST /user/projects/{id}/publish`

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
curl -X POST "https://api.zoo.dev/user/projects/{id}/publish" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
