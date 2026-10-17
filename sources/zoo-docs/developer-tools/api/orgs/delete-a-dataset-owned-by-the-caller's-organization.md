Source URL: https://zoo.dev/docs/developer-tools/api/orgs/delete-a-dataset-owned-by-the-caller%27s-organization
Title: Delete a dataset owned by the caller's organization.

# Delete a dataset owned by the caller's organization.

`DELETE /org/datasets/{id}`

This is a destructive operation that: - requires org admin authentication and the dataset must belong to the caller's org. - fails with a 409 Conflict if the dataset is still attached to any custom model. - deletes Zoo-managed artifacts for this dataset (converted outputs and embeddings). - does **not** delete or modify the customer's source bucket/prefix.

All internal artifact deletions are strict; if any cleanup fails, the request fails.

## Section

[Orgs](/docs/developer-tools/api/orgs)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | Uuid | yes | The identifier. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | successful deletion |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X DELETE "https://api.zoo.dev/org/datasets/{id}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
