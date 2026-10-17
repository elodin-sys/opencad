Source URL: https://zoo.dev/docs/developer-tools/api/api-tokens
Title: API Tokens

# API Tokens

API tokens allow users to call the API outside of their session token that is used as a cookie in the user interface. Users can create, delete, and list their API tokens. But, of course, you need an API token to do this, so first be sure to generate one in the account UI.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/user/api-tokens](/docs/developer-tools/api/api-tokens/list-api-tokens-for-your-user) | List API tokens for your user. |
| POST | [/user/api-tokens](/docs/developer-tools/api/api-tokens/create-a-new-api-token-for-your-user) | Create a new API token for your user. |
| GET | [/user/api-tokens/{token}](/docs/developer-tools/api/api-tokens/get-an-api-token-for-your-user) | Get an API token for your user. |
| DELETE | [/user/api-tokens/{token}](/docs/developer-tools/api/api-tokens/delete-an-api-token-for-your-user) | Delete an API token for your user. |
