Source URL: https://zoo.dev/docs/developer-tools/api/service-accounts
Title: Service Accounts

# Service Accounts

Service accounts allow organizations to call the API. Organization admins can create, delete, and list the service accounts for their org. Service accounts are scoped to an organization not individual users, these are better to use for automations than individual API tokens, since they won't stop working when an individual leaves the company.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/org/service-accounts](/docs/developer-tools/api/service-accounts/list-service-accounts-for-your-org) | List service accounts for your org. |
| POST | [/org/service-accounts](/docs/developer-tools/api/service-accounts/create-a-new-service-account-for-your-org) | Create a new service account for your org. |
| GET | [/org/service-accounts/{token}](/docs/developer-tools/api/service-accounts/get-an-service-account-for-your-org) | Get an service account for your org. |
| DELETE | [/org/service-accounts/{token}](/docs/developer-tools/api/service-accounts/delete-an-service-account-for-your-org) | Delete an service account for your org. |
