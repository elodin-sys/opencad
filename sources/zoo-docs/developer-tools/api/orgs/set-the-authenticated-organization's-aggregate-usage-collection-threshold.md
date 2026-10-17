Source URL: https://zoo.dev/docs/developer-tools/api/orgs/set-the-authenticated-organization%27s-aggregate-usage-collection-threshold
Title: Set the authenticated organization's aggregate-usage collection threshold.

# Set the authenticated organization's aggregate-usage collection threshold.

`PUT /org/billing/usage-collection-threshold`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | AggregateUsageCollectionThresholdSet |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/billing/usage-collection-threshold" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
