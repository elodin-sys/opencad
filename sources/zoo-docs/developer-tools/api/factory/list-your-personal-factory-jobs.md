Source URL: https://zoo.dev/docs/developer-tools/api/factory/list-your-personal-factory-jobs
Title: List your personal Factory jobs.

# List your personal Factory jobs.

`GET /user/factory/jobs`

Returns jobs owned by your account, including archived jobs. Jobs with an organization owner belong to that organization, even when your account is also associated with them; use `GET /org/factory/jobs` to list those jobs. Results are paginated, newest first by default, with the job id breaking ties. Internal communication, financial details, and file storage locations are omitted.

## Section

[Factory](/docs/developer-tools/api/factory)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer | no | Maximum number of items returned by a single call |
| page_token | query | string | no | Token returned by previous call to retrieve the subsequent page |
| sort_by | query | CreatedAtSortMode | no |  |

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
curl "https://api.zoo.dev/user/factory/jobs" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
