Source URL: https://zoo.dev/docs/developer-tools/api
Title: Zoo API Overview

# Zoo API Overview

Zoo provides APIs for building hardware design tools and automations. You can use them to create or edit geometry, convert CAD files, run AI-assisted workflows, and manage the account objects around those systems.

Base URL: `https://api.zoo.dev`

## Getting Started

1. Create an API token from your Zoo account.
2. Send it as a bearer token in the `Authorization` header.
3. Start with a simple authenticated request:

```bash
curl "https://api.zoo.dev/user" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```

## Available APIs

| Section | Description |
| --- | --- |
| [ML](/docs/developer-tools/api/ml) | Machine learning to generate CAD models and other things. |
| [Modeling](/docs/developer-tools/api/modeling) | Modeling API for updating your 3D files using the Zoo engine. |
| [API Calls](/docs/developer-tools/api/api-calls) | API calls that have been performed by users can be queried by the API. This is helpful for debugging as well as billing. |
| [API Tokens](/docs/developer-tools/api/api-tokens) | API tokens allow users to call the API outside of their session token that is used as a cookie in the user interface. Users can create, delete, and list their API tokens. But, of course, you need an API token to do this, so first be sure to generate one in the account UI. |
| [Factory](/docs/developer-tools/api/factory) | Operations for submitting and managing Factory manufacturing jobs. |
| [File](/docs/developer-tools/api/file) | CAD file operations. Create, get, and list CAD file conversions. More endpoints will be added here in the future as we build out transforms, etc on CAD models. |
| [Meta](/docs/developer-tools/api/meta) | Meta information about the API. |
| [Oauth2](/docs/developer-tools/api/oauth2) | Endpoints that implement OAuth 2.0 grant flows. |
| [Orgs](/docs/developer-tools/api/orgs) | An organization is a group of users of the Zoo API. Here, we can add users to an org and perform operations on orgs. |
| [Payments](/docs/developer-tools/api/payments) | Operations around payments and billing. |
| [Projects](/docs/developer-tools/api/projects) | Operations for user-owned projects, public project discovery, publishing, voting, and share links. |
| [Service Accounts](/docs/developer-tools/api/service-accounts) | Service accounts allow organizations to call the API. Organization admins can create, delete, and list the service accounts for their org. Service accounts are scoped to an organization not individual users, these are better to use for automations than individual API tokens, since they won't stop working when an individual leaves the company. |
| [Shortlinks](/docs/developer-tools/api/shortlinks) | Shortlinks are a way to create a short URL that redirects to a longer URL. This is useful for sharing links that are long and unwieldy. |
| [Unit](/docs/developer-tools/api/unit) | Unit conversion operations. |
| [Users](/docs/developer-tools/api/users) | A user is someone who uses the Zoo API. Here, we can create, delete, and list users. We can also get information about a user. Operations will only be authorized if the user is requesting information about themselves. |

The OpenAPI schema is available from `https://api.zoo.dev`.
