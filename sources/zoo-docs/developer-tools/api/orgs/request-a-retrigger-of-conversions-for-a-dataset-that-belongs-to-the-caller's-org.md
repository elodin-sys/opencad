Source URL: https://zoo.dev/docs/developer-tools/api/orgs/request-a-retrigger-of-conversions-for-a-dataset-that-belongs-to-the-caller%27s-org
Title: Request a retrigger of conversions for a dataset that belongs to the caller's org.

# Request a retrigger of conversions for a dataset that belongs to the caller's org.

`POST /org/datasets/{id}/retrigger`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |
| statuses | query | string | no | Optional comma-separated set of conversion statuses to retrigger.<br><br>Example: `statuses=success,in_progress` If omitted, we retrigger all non-success conversions, but only retrigger `in_progress` conversions that have been running for more than 5 minutes. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | resource updated |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/datasets/{id}/retrigger" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
