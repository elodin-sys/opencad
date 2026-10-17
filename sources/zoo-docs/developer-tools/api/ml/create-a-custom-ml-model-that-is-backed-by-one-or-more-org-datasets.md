Source URL: https://zoo.dev/docs/developer-tools/api/ml/create-a-custom-ml-model-that-is-backed-by-one-or-more-org-datasets
Title: Create a custom ML model that is backed by one or more org datasets.

# Create a custom ML model that is backed by one or more org datasets.

`POST /ml/custom/models`

Dataset readiness is enforced via `OrgDatasetFileConversion::status_counts_for_datasets`: - At least one conversion must have status `success`. - No conversions may remain in `queued`. If even a single file is still queued the dataset is treated as “not ready for training.” - A dataset consisting only of `canceled` or `error_*` entries is rejected because there’s nothing usable.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

No parameters.

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | CreateCustomModel |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/ml/custom/models" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
