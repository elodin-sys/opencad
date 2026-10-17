Source URL: https://zoo.dev/docs/developer-tools/api/api-calls/get-an-api-call-for-an-org
Title: Get an API call for an org.

# Get an API call for an org.

`GET /org/api-calls/{id}`

This endpoint requires authentication by an org admin. It returns details of the requested API call for the user's org.

## Section

[API Calls](/docs/developer-tools/api/api-calls)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The ID of the API call. |

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
curl "https://api.zoo.dev/org/api-calls/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
