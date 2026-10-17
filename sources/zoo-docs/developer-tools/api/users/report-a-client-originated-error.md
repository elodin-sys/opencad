Source URL: https://zoo.dev/docs/developer-tools/api/users/report-a-client-originated-error
Title: Report a CLIent-originated error.

# Report a CLIent-originated error.

`POST /user/client-errors`

This endpoint requires authentication by any Zoo user. It accepts a structured client error payload and writes it to the server logs for triage.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | ClientErrorReport |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 202 | successfully enqueued operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/user/client-errors" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
