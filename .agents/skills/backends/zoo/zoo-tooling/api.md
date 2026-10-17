# Zoo REST API

Base `https://api.zoo.dev`, header `Authorization: Bearer $ZOO_API_TOKEN`. OpenAPI: `GET /`.
Large or slow jobs return an async operation `id`; poll `GET /async/operations/{id}`. Errors are JSON with `error_code` and `message` (see `/docs/developer-tools/api/errors`).
`†` = hidden endpoint (absent from public nav; unstable; listed by path only). Page: `zoo.dev/docs/developer-tools/api/<section>/<slug-of-title>`.
Gists are omitted where the path already says it.

## api-calls: API calls that have been performed by users can be queried by…
- `GET /api-calls/{id}` †
- `GET /async/operations/{id}`
- `GET /org/api-calls`
- `GET /org/api-calls/{id}`
- `GET /user/api-calls`
- `GET /user/api-calls/{id}`
- `GET /users/{id}/api-calls` †

## api-tokens: API tokens allow users to call the API outside of their session…
- `GET /user/api-tokens`
- `POST /user/api-tokens`
- `DELETE /user/api-tokens/{token}`
- `GET /user/api-tokens/{token}`

## executor
- `POST /file/execute/{lang}` †

## factory: Operations for submitting and managing Factory manufacturing jobs
- `GET /org/factory/jobs`
- `GET /user/factory/finishes` List finishes currently available for customer Factory submissions
- `GET /user/factory/jobs`
- `POST /user/factory/jobs` †
- `GET /user/factory/materials` List materials currently available for customer Factory submissions

## file: CAD file operations
- `POST /file/center-of-mass`
- `POST /file/conversion` Convert CAD file from one format to another
- `POST /file/conversion/{src_format}/{output_format}` Convert CAD file with defaults
- `POST /file/density`
- `POST /file/mass`
- `POST /file/surface-area`
- `POST /file/volume`

## meta: Meta information about the API
- `GET /` Get OpenAPI schema
- `GET /_meta/ipinfo` †
- `GET /announcements` List all active announcements
- `GET /community/sso` †
- `GET /ping` Return pong
- `GET /pricing/subscriptions` †

## ml: Machine learning to generate CAD models and other things
- `GET /ml/conversations`
- `POST /ml/convert/proprietary-to-kcl` †
- `POST /ml/custom/models` Create a custom ML model that is backed…
- `GET /ml/custom/models/{id}` Retrieve the details of a single custom ML…
- `PUT /ml/custom/models/{id}` Update mutable metadata (name…
- `GET /ml/custom/models/{id}/datasets` List the org datasets that are currently attached…
- `POST /ml/kcl/completions` †
- `GET /user/text-to-cad` List text-to-CAD parts you've generated
- `GET /user/text-to-cad/{id}`
- `POST /user/text-to-cad/{id}` Give feedback to a specific ML response
- `GET /ws/ml/copilot` Open a websocket to a Zookeeper agent instance
- `GET /ws/ml/reasoning/{id}` Open a websocket to prompt the ML copilot

## modeling
- `GET /ws/modeling/commands` Opens a WebSocket to a Zoo KittyCAD engine…

## oauth2: Endpoints that implement OAuth 2.0 grant flows
- `GET /oauth2/authorization-requests/{request_id}` †
- `POST /oauth2/authorization-requests/{request_id}/approve` †
- `POST /oauth2/authorization-requests/{request_id}/deny` †
- `GET /oauth2/authorize` †
- `POST /oauth2/device/auth` †
- `POST /oauth2/device/confirm` †
- `POST /oauth2/device/token` †
- `GET /oauth2/device/verify` †
- `GET /oauth2/provider/{provider}/callback` †
- `GET /oauth2/provider/{provider}/consent` †
- `POST /oauth2/token` †
- `POST /oauth2/token/revoke` †
- `GET /oauth2/verify-account-linking`
- `GET /org/oauth2/apps`
- `POST /org/oauth2/apps`
- `DELETE /org/oauth2/apps/{client_id}`
- `GET /org/oauth2/apps/{client_id}`
- `PUT /org/oauth2/apps/{client_id}`
- `GET /user/oauth2/apps`
- `POST /user/oauth2/apps` Create a personal OAuth app
- `DELETE /user/oauth2/apps/{client_id}` Delete a personal OAuth app
- `GET /user/oauth2/apps/{client_id}`
- `PUT /user/oauth2/apps/{client_id}` Update a personal OAuth app

## orgs: An organization is a group of users of the Zoo API
- `DELETE /org` †
- `GET /org`
- `POST /org` Create an org
- `PUT /org` Update an org
- `DELETE /org/billing/usage-collection-threshold` Restore the default for the authenticated organization's aggregate-usage…
- `GET /org/billing/usage-collection-threshold` Get the authenticated organization's aggregate-usage collection threshold
- `PUT /org/billing/usage-collection-threshold` Set the authenticated organization's aggregate-usage collection threshold
- `GET /org/dataset/s3/policies` Return the IAM policies customers should apply when…
- `GET /org/datasets` List every dataset that belongs to the caller's…
- `POST /org/datasets`
- `DELETE /org/datasets/{id}` Delete a dataset owned by the caller's organization
- `GET /org/datasets/{id}` Fetch a single dataset by ID so long…
- `PUT /org/datasets/{id}` Update dataset metadata or storage credentials for the…
- `GET /org/datasets/{id}/bulk-download/kcl` Bulk-download KCL outputs for successful dataset conversions
- `GET /org/datasets/{id}/conversions` List the file conversions that have been processed…
- `GET /org/datasets/{id}/conversions/{conversion_id}` Fetch the metadata and converted output for a…
- `GET /org/datasets/{id}/conversions/{conversion_id}/original` Download the original source file for a specific…
- `POST /org/datasets/{id}/conversions/{conversion_id}/retrigger`
- `POST /org/datasets/{id}/retrigger` Request a retrigger of conversions for a dataset…
- `GET /org/datasets/{id}/search/conversions`
- `GET /org/datasets/{id}/search/semantic` Run semantic search across chunked conversion outputs for…
- `GET /org/datasets/{id}/stats` Return aggregate conversion stats for a dataset owned…
- `POST /org/datasets/{id}/uploads` Upload source files into a Zoo-managed dataset
- `GET /org/members`
- `POST /org/members`
- `DELETE /org/members/{user_id}`
- `GET /org/members/{user_id}`
- `PUT /org/members/{user_id}`
- `GET /org/privacy`
- `PUT /org/privacy` Update the privacy settings for an org
- `DELETE /org/saml/idp` Delete an SAML identity provider
- `GET /org/saml/idp` Get the SAML identity provider
- `POST /org/saml/idp` Create a SAML identity provider
- `PUT /org/saml/idp` Update the SAML identity provider
- `GET /org/shortlinks`
- `GET /org/skills` List every skill that belongs to the caller's…
- `GET /user/org`

## payments: Operations around payments and billing
- `DELETE /org/payment` Delete payment info for your org
- `GET /org/payment` Get payment info about your org
- `POST /org/payment` Create payment info for your org
- `PUT /org/payment` Update payment info for your org
- `GET /org/payment/balance`
- `POST /org/payment/intent` †
- `GET /org/payment/invoices`
- `GET /org/payment/method-portal-link` Redirect to a fresh Stripe-hosted payment-method update link…
- `GET /org/payment/methods`
- `DELETE /org/payment/methods/{id}` †
- `GET /org/payment/subscriptions`
- `POST /org/payment/subscriptions`
- `PUT /org/payment/subscriptions`
- `GET /org/payment/tax` †
- `DELETE /user/billing/usage-collection-threshold` Restore the default for your personal aggregate-usage collection…
- `GET /user/billing/usage-collection-threshold`
- `PUT /user/billing/usage-collection-threshold` Set your personal aggregate-usage collection threshold
- `DELETE /user/payment` Delete payment info for your user
- `GET /user/payment` Get payment info about your user
- `POST /user/payment` Create payment info for your user
- `PUT /user/payment` Update payment info for your user
- `GET /user/payment/balance`
- `POST /user/payment/intent` †
- `GET /user/payment/invoices`
- `GET /user/payment/method-portal-link` Redirect to a fresh Stripe-hosted payment-method update link…
- `GET /user/payment/methods`
- `DELETE /user/payment/methods/{id}` †
- `POST /user/payment/methods/{id}/default`
- `GET /user/payment/subscriptions`
- `POST /user/payment/subscriptions`
- `PUT /user/payment/subscriptions` Update the user's subscription
- `GET /user/payment/tax` †

## projects: Operations for user-owned projects, public project discovery, publishing, voting, and share links
- `GET /projects/categories` List the active categories available for project submissions
- `GET /projects/public` List publicly visible community projects for the website/gallery
- `GET /projects/public/{id}` Get one publicly visible community project
- `GET /projects/public/{id}/download` Download a published public project as a tar…
- `GET /projects/public/{id}/thumbnail`
- `DELETE /projects/public/{id}/vote` Remove the authenticated user's upvote from a published…
- `POST /projects/public/{id}/vote` Add the authenticated user's upvote to a published…
- `GET /projects/shared/{key}/download` †
- `GET /user/projects` List the authenticated user's projects
- `POST /user/projects` Create a draft project for the authenticated user
- `DELETE /user/projects/{id}` Delete one of the authenticated user's projects
- `GET /user/projects/{id}` Get one of the authenticated user's projects
- `PUT /user/projects/{id}` Replace one of the authenticated user's projects
- `GET /user/projects/{id}/download` Download one of the authenticated user's projects as…
- `DELETE /user/projects/{id}/organization` Move an organization project back to its creator's…
- `PUT /user/projects/{id}/organization` Move one of the authenticated user's projects into…
- `POST /user/projects/{id}/publish` Submit one of the authenticated user's projects for…
- `GET /user/projects/{id}/share-links`
- `POST /user/projects/{id}/share-links` Create a share link for one of the…
- `DELETE /user/projects/{id}/share-links/{key}` Delete one share link for one of the…
- `GET /user/projects/{id}/thumbnail` Fetch the authenticated owner's current project thumbnail

## service-accounts: Service accounts allow organizations to call the API
- `GET /org/service-accounts`
- `POST /org/service-accounts`
- `DELETE /org/service-accounts/{token}`
- `GET /org/service-accounts/{token}`

## shortlinks: Shortlinks are a way to create a short URL that redirects to…
- `GET /user/shortlinks`
- `POST /user/shortlinks`
- `DELETE /user/shortlinks/{key}`
- `GET /user/shortlinks/{key}` †
- `PUT /user/shortlinks/{key}`

## unit: Unit conversion operations
- `GET /unit/conversion/angle/{input_unit}/{output_unit}`
- `GET /unit/conversion/area/{input_unit}/{output_unit}`
- `GET /unit/conversion/current/{input_unit}/{output_unit}`
- `GET /unit/conversion/energy/{input_unit}/{output_unit}`
- `GET /unit/conversion/force/{input_unit}/{output_unit}`
- `GET /unit/conversion/frequency/{input_unit}/{output_unit}`
- `GET /unit/conversion/length/{input_unit}/{output_unit}`
- `GET /unit/conversion/mass/{input_unit}/{output_unit}`
- `GET /unit/conversion/power/{input_unit}/{output_unit}`
- `GET /unit/conversion/pressure/{input_unit}/{output_unit}`
- `GET /unit/conversion/temperature/{input_unit}/{output_unit}`
- `GET /unit/conversion/torque/{input_unit}/{output_unit}`
- `GET /unit/conversion/volume/{input_unit}/{output_unit}`

## users: A user is someone who uses the Zoo API
- `DELETE /user` Delete your user
- `GET /user`
- `PUT /user` Update your user
- `GET /user/cad-user-info` Gets authenticated CAD user info form data for…
- `POST /user/client-errors` Report a CLIent-originated error
- `GET /user/email-marketing-consent`
- `POST /user/email-marketing-consent/decline`
- `POST /user/email-marketing-consent/request` Request email marketing opt-in…
- `POST /user/email-marketing-consent/seen` Mark the email-marketing modal as seen/dismissed for the…
- `GET /user/extended` Get extended information about your user
- `GET /user/features` List user-visible feature flags enabled for the authenticated…
- `GET /user/oauth2/providers`
- `GET /user/privacy`
- `PUT /user/privacy` Update the user's privacy settings
- `GET /user/session/{token}`
- `GET /users-extended/{id}` †
- `GET /users/{id}` †
- `PUT /website/email-marketing-consent/request` †
- `PUT /website/email-marketing-lists/{slug}/subscribe` †
- `PUT /website/email-marketing-lists/{slug}/unsubscribe` †
- `PUT /website/forms/cad-user-info` †
- `PUT /website/forms/sales` †
- `PUT /website/forms/support` †
