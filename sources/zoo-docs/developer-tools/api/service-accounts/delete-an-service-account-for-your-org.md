Source URL: https://zoo.dev/docs/developer-tools/api/service-accounts/delete-an-service-account-for-your-org
Title: Delete an service account for your org.

# Delete an service account for your org.

`DELETE /org/service-accounts/{token}`

This endpoint requires authentication by an org member. It deletes the requested service account for the organization.

This endpoint does not actually delete the service account from the database. It merely marks the token as invalid. We still want to keep the service account in the database for historical purposes.

The token path parameter can be either the full service account token (prefixed with `svc-`) or the token's unique ID (a UUID).

## Section

[Service Accounts](/docs/developer-tools/api/service-accounts)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | path | string | yes | The service account token (prefixed with `svc-`) or the token's unique ID (a UUID). |

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
curl -X DELETE "https://api.zoo.dev/org/service-accounts/{token}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
