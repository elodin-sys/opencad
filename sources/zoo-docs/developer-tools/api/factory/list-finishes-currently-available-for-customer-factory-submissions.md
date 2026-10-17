Source URL: https://zoo.dev/docs/developer-tools/api/factory/list-finishes-currently-available-for-customer-factory-submissions
Title: List finishes currently available for customer Factory submissions.

# List finishes currently available for customer Factory submissions.

`GET /user/factory/finishes`

Internal-only entries are omitted. Clients should refetch this endpoint after a catalog validation error before asking the customer to choose again.

## Section

[Factory](/docs/developer-tools/api/factory)

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
curl "https://api.zoo.dev/user/factory/finishes" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
