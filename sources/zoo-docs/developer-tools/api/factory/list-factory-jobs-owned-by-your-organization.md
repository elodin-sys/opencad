Source URL: https://zoo.dev/docs/developer-tools/api/factory/list-factory-jobs-owned-by-your-organization
Title: List Factory jobs owned by your organization.

# List Factory jobs owned by your organization.

`GET /org/factory/jobs`

Any current organization member can list its jobs, including archived jobs. Ownership uses the job's stored organization, so a submitter leaving or deleting their account does not move the job. Former members lose access. Results are paginated, newest first by default, with the job id breaking ties. Internal communication, financial details, and file storage locations are omitted.

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
curl "https://api.zoo.dev/org/factory/jobs" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
