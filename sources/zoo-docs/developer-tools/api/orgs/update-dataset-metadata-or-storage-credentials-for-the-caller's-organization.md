Source URL: https://zoo.dev/docs/developer-tools/api/orgs/update-dataset-metadata-or-storage-credentials-for-the-caller%27s-organization
Title: Update dataset metadata or storage credentials for the caller's organization.

# Update dataset metadata or storage credentials for the caller's organization.

`PUT /org/datasets/{id}`

IMPORTANT: Use this endpoint to fix connectivity to the same underlying storage location (e.g. rotating credentials or correcting a typo). Do not repoint an existing dataset at a completely different bucket or provider—create a new dataset instead so conversions in flight keep their original source. This warning applies to every storage backend, not just S3.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateOrgDataset |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/org/datasets/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
