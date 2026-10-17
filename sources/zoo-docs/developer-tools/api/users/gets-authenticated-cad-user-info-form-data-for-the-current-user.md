Source URL: https://zoo.dev/docs/developer-tools/api/users/gets-authenticated-cad-user-info-form-data-for-the-current-user
Title: Gets authenticated CAD user info form data for the current user.

# Gets authenticated CAD user info form data for the current user.

`GET /user/cad-user-info`

An endpoint within the Zoo API.

## Section

[Users](/docs/developer-tools/api/users)

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
curl "https://api.zoo.dev/user/cad-user-info" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
