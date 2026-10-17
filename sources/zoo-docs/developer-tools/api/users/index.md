Source URL: https://zoo.dev/docs/developer-tools/api/users
Title: Users

# Users

A user is someone who uses the Zoo API. Here, we can create, delete, and list users. We can also get information about a user. Operations will only be authorized if the user is requesting information about themselves.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/user](/docs/developer-tools/api/users/get-your-user) | Get your user. |
| PUT | [/user](/docs/developer-tools/api/users/update-your-user) | Update your user. |
| DELETE | [/user](/docs/developer-tools/api/users/delete-your-user) | Delete your user. |
| GET | [/user/cad-user-info](/docs/developer-tools/api/users/gets-authenticated-cad-user-info-form-data-for-the-current-user) | Gets authenticated CAD user info form data for the current user. |
| POST | [/user/client-errors](/docs/developer-tools/api/users/report-a-client-originated-error) | Report a CLIent-originated error. |
| GET | [/user/email-marketing-consent](/docs/developer-tools/api/users/get-email-marketing-consent-state-for-the-authenticated-user) | Get email marketing consent state for the authenticated user. |
| POST | [/user/email-marketing-consent/decline](/docs/developer-tools/api/users/record-explicit-decline-for-email-marketing-consent) | Record explicit decline for email marketing consent. |
| POST | [/user/email-marketing-consent/request](/docs/developer-tools/api/users/request-email-marketing-opt-in-and-send-a-confirmation-email) | Request email marketing opt-in and send a confirmation email. |
| POST | [/user/email-marketing-consent/seen](/docs/developer-tools/api/users/mark-the-email-marketing-modal-as-seen/dismissed-for-the-authenticated-user) | Mark the email-marketing modal as seen/dismissed for the authenticated user. |
| GET | [/user/extended](/docs/developer-tools/api/users/get-extended-information-about-your-user) | Get extended information about your user. |
| GET | [/user/features](/docs/developer-tools/api/users/list-user-visible-feature-flags-enabled-for-the-authenticated-user) | List user-visible feature flags enabled for the authenticated user. |
| GET | [/user/oauth2/apps](/docs/developer-tools/api/users/list-personal-oauth-apps) | List personal OAuth apps. |
| POST | [/user/oauth2/apps](/docs/developer-tools/api/users/create-a-personal-oauth-app) | Create a personal OAuth app. |
| GET | [/user/oauth2/apps/{client_id}](/docs/developer-tools/api/users/get-a-personal-oauth-app) | Get a personal OAuth app. |
| PUT | [/user/oauth2/apps/{client_id}](/docs/developer-tools/api/users/update-a-personal-oauth-app) | Update a personal OAuth app. |
| DELETE | [/user/oauth2/apps/{client_id}](/docs/developer-tools/api/users/delete-a-personal-oauth-app) | Delete a personal OAuth app. |
| GET | [/user/oauth2/providers](/docs/developer-tools/api/users/get-the-oauth2-providers-for-your-user) | Get the OAuth2 providers for your user. |
| GET | [/user/org](/docs/developer-tools/api/users/get-a-user's-org) | Get a user's org. |
| GET | [/user/privacy](/docs/developer-tools/api/users/get-the-privacy-settings-for-a-user) | Get the privacy settings for a user. |
| PUT | [/user/privacy](/docs/developer-tools/api/users/update-the-user's-privacy-settings) | Update the user's privacy settings. |
| GET | [/user/session/{token}](/docs/developer-tools/api/users/get-a-session-for-your-user) | Get a session for your user. |
| GET | [/user/shortlinks](/docs/developer-tools/api/users/get-the-shortlinks-for-a-user) | Get the shortlinks for a user. |
| POST | [/user/shortlinks](/docs/developer-tools/api/users/create-a-shortlink-for-a-user) | Create a shortlink for a user. |
| PUT | [/user/shortlinks/{key}](/docs/developer-tools/api/users/update-a-shortlink-for-a-user) | Update a shortlink for a user. |
| DELETE | [/user/shortlinks/{key}](/docs/developer-tools/api/users/delete-a-shortlink-for-a-user) | Delete a shortlink for a user. |
