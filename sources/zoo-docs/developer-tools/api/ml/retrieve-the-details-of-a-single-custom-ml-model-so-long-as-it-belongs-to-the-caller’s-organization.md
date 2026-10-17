Source URL: https://zoo.dev/docs/developer-tools/api/ml/retrieve-the-details-of-a-single-custom-ml-model-so-long-as-it-belongs-to-the-caller%E2%80%99s-organization
Title: Retrieve the details of a single custom ML model so long as it belongs to the caller’s organization.

# Retrieve the details of a single custom ML model so long as it belongs to the caller’s organization.

`GET /ml/custom/models/{id}`

An endpoint within the Zoo API.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

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
curl "https://api.zoo.dev/ml/custom/models/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
