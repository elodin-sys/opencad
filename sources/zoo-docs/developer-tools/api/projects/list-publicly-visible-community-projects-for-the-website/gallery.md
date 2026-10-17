Source URL: https://zoo.dev/docs/developer-tools/api/projects/list-publicly-visible-community-projects-for-the-website/gallery
Title: List publicly visible community projects for the website/gallery.

# List publicly visible community projects for the website/gallery.

`GET /projects/public`

An endpoint within the Zoo API.

## Section

[Projects](/docs/developer-tools/api/projects)

## Parameters

No parameters.

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
curl "https://api.zoo.dev/projects/public" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
