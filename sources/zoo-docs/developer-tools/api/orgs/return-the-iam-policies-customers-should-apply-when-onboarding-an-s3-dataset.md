Source URL: https://zoo.dev/docs/developer-tools/api/orgs/return-the-iam-policies-customers-should-apply-when-onboarding-an-s3-dataset
Title: Return the IAM policies customers should apply when onboarding an S3 dataset.

# Return the IAM policies customers should apply when onboarding an S3 dataset.

`GET /org/dataset/s3/policies`

An endpoint within the Zoo API.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| uri | query | string | yes | Dataset URI used to scope generated IAM policies. |
| role_arn | query | string | yes | IAM role ARN customers expect Zoo to assume when reading the dataset. |

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
curl "https://api.zoo.dev/org/dataset/s3/policies" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
