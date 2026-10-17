Source URL: https://zoo.dev/docs/developer-tools/api/service-accounts/create-a-new-service-account-for-your-org
Title: Create a new service account for your org.

# Create a new service account for your org.

`POST /org/service-accounts`

This endpoint requires authentication by an org member. It creates a new service account for the organization.

## Section

[Service Accounts](/docs/developer-tools/api/service-accounts)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| label | query | string | no | An optional label for the service account. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/org/service-accounts" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
