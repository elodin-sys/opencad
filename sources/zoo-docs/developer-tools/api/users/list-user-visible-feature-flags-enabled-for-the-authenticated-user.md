Source URL: https://zoo.dev/docs/developer-tools/api/users/list-user-visible-feature-flags-enabled-for-the-authenticated-user
Title: List user-visible feature flags enabled for the authenticated user.

# List user-visible feature flags enabled for the authenticated user.

`GET /user/features`

Returns only features that are marked as safe for exposure to clients and currently resolved to `true` for the requesting user (including org overrides).

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
curl "https://api.zoo.dev/user/features" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
