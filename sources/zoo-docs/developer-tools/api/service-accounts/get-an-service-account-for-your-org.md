Source URL: https://zoo.dev/docs/developer-tools/api/service-accounts/get-an-service-account-for-your-org
Title: Get an service account for your org.

# Get an service account for your org.

`GET /org/service-accounts/{token}`

This endpoint requires authentication by an org member. It returns details of the requested service account for the organization.

## Section

[Service Accounts](/docs/developer-tools/api/service-accounts)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| token | path | ServiceAccountUuid | yes | The service account. |

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
curl "https://api.zoo.dev/org/service-accounts/{token}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
