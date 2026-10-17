Source URL: https://zoo.dev/docs/developer-tools/api/api-calls/get-an-async-operation
Title: Get an async operation.

# Get an async operation.

`GET /async/operations/{id}`

Get the status and output of an async operation.

This endpoint requires authentication by any Zoo user. It returns details of the requested async operation for the user.

If the user is not authenticated to view the specified async operation, then it is not returned.

Only Zoo employees with the proper access can view async operations for other users.

## Section

[API Calls](/docs/developer-tools/api/api-calls)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The ID of the async operation. |

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
curl "https://api.zoo.dev/async/operations/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
