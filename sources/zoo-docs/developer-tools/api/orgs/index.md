Source URL: https://zoo.dev/docs/developer-tools/api/orgs
Title: Orgs

# Orgs

An organization is a group of users of the Zoo API. Here, we can add users to an org and perform operations on orgs.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/org](/docs/developer-tools/api/orgs/get-an-org) | Get an org. |
| PUT | [/org](/docs/developer-tools/api/orgs/update-an-org) | Update an org. |
| POST | [/org](/docs/developer-tools/api/orgs/create-an-org) | Create an org. |
| GET | [/org/billing/usage-collection-threshold](/docs/developer-tools/api/orgs/get-the-authenticated-organization's-aggregate-usage-collection-threshold) | Get the authenticated organization's aggregate-usage collection threshold. |
| PUT | [/org/billing/usage-collection-threshold](/docs/developer-tools/api/orgs/set-the-authenticated-organization's-aggregate-usage-collection-threshold) | Set the authenticated organization's aggregate-usage collection threshold. |
| DELETE | [/org/billing/usage-collection-threshold](/docs/developer-tools/api/orgs/restore-the-default-for-the-authenticated-organization's-aggregate-usage-collection-threshold) | Restore the default for the authenticated organization's aggregate-usage collection threshold. |
| GET | [/org/dataset/s3/policies](/docs/developer-tools/api/orgs/return-the-iam-policies-customers-should-apply-when-onboarding-an-s3-dataset) | Return the IAM policies customers should apply when onboarding an S3 dataset. |
| GET | [/org/datasets](/docs/developer-tools/api/orgs/list-every-dataset-that-belongs-to-the-caller's-organization) | List every dataset that belongs to the caller's organization. |
| POST | [/org/datasets](/docs/developer-tools/api/orgs/register-a-new-org-dataset) | Register a new org dataset. |
| GET | [/org/datasets/{id}](/docs/developer-tools/api/orgs/fetch-a-single-dataset-by-id-so-long-as-it-belongs-to-the-authenticated-org) | Fetch a single dataset by ID so long as it belongs to the authenticated org. |
| PUT | [/org/datasets/{id}](/docs/developer-tools/api/orgs/update-dataset-metadata-or-storage-credentials-for-the-caller's-organization) | Update dataset metadata or storage credentials for the caller's organization. |
| DELETE | [/org/datasets/{id}](/docs/developer-tools/api/orgs/delete-a-dataset-owned-by-the-caller's-organization) | Delete a dataset owned by the caller's organization. |
| GET | [/org/datasets/{id}/bulk-download/kcl](/docs/developer-tools/api/orgs/bulk-download-kcl-outputs-for-successful-dataset-conversions) | Bulk-download KCL outputs for successful dataset conversions. |
| GET | [/org/datasets/{id}/conversions](/docs/developer-tools/api/orgs/list-the-file-conversions-that-have-been-processed-for-a-given-dataset-owned-by-the-caller's-org) | List the file conversions that have been processed for a given dataset owned by the caller's org. |
| GET | [/org/datasets/{id}/conversions/{conversion_id}](/docs/developer-tools/api/orgs/fetch-the-metadata-and-converted-output-for-a-single-dataset-conversion) | Fetch the metadata and converted output for a single dataset conversion. |
| GET | [/org/datasets/{id}/conversions/{conversion_id}/original](/docs/developer-tools/api/orgs/download-the-original-source-file-for-a-specific-dataset-conversion) | Download the original source file for a specific dataset conversion. |
| POST | [/org/datasets/{id}/conversions/{conversion_id}/retrigger](/docs/developer-tools/api/orgs/retrigger-a-specific-dataset-conversion-for-the-caller's-org) | Retrigger a specific dataset conversion for the caller's org. |
| POST | [/org/datasets/{id}/retrigger](/docs/developer-tools/api/orgs/request-a-retrigger-of-conversions-for-a-dataset-that-belongs-to-the-caller's-org) | Request a retrigger of conversions for a dataset that belongs to the caller's org. |
| GET | [/org/datasets/{id}/search/conversions](/docs/developer-tools/api/orgs/search-dataset-conversions-by-conversion-id-or-file-path) | Search dataset conversions by conversion ID or file path. |
| GET | [/org/datasets/{id}/search/semantic](/docs/developer-tools/api/orgs/run-semantic-search-across-chunked-conversion-outputs-for-a-dataset) | Run semantic search across chunked conversion outputs for a dataset. |
| GET | [/org/datasets/{id}/stats](/docs/developer-tools/api/orgs/return-aggregate-conversion-stats-for-a-dataset-owned-by-the-caller's-org) | Return aggregate conversion stats for a dataset owned by the caller's org. |
| POST | [/org/datasets/{id}/uploads](/docs/developer-tools/api/orgs/upload-source-files-into-a-zoo-managed-dataset) | Upload source files into a Zoo-managed dataset. |
| GET | [/org/members](/docs/developer-tools/api/orgs/list-members-of-your-org) | List members of your org. |
| POST | [/org/members](/docs/developer-tools/api/orgs/add-a-member-to-your-org) | Add a member to your org. |
| GET | [/org/members/{user_id}](/docs/developer-tools/api/orgs/get-a-member-of-your-org) | Get a member of your org. |
| PUT | [/org/members/{user_id}](/docs/developer-tools/api/orgs/update-a-member-of-your-org) | Update a member of your org. |
| DELETE | [/org/members/{user_id}](/docs/developer-tools/api/orgs/remove-a-member-from-your-org) | Remove a member from your org. |
| GET | [/org/oauth2/apps](/docs/developer-tools/api/orgs/list-org-oauth-apps) | List org OAuth apps. |
| POST | [/org/oauth2/apps](/docs/developer-tools/api/orgs/create-an-org-oauth-app) | Create an org OAuth app. |
| GET | [/org/oauth2/apps/{client_id}](/docs/developer-tools/api/orgs/get-an-org-oauth-app) | Get an org OAuth app. |
| PUT | [/org/oauth2/apps/{client_id}](/docs/developer-tools/api/orgs/update-an-org-oauth-app) | Update an org OAuth app. |
| DELETE | [/org/oauth2/apps/{client_id}](/docs/developer-tools/api/orgs/delete-an-org-oauth-app) | Delete an org OAuth app. |
| GET | [/org/privacy](/docs/developer-tools/api/orgs/get-the-privacy-settings-for-an-org) | Get the privacy settings for an org. |
| PUT | [/org/privacy](/docs/developer-tools/api/orgs/update-the-privacy-settings-for-an-org) | Update the privacy settings for an org. |
| GET | [/org/saml/idp](/docs/developer-tools/api/orgs/get-the-saml-identity-provider) | Get the SAML identity provider. |
| PUT | [/org/saml/idp](/docs/developer-tools/api/orgs/update-the-saml-identity-provider) | Update the SAML identity provider. |
| POST | [/org/saml/idp](/docs/developer-tools/api/orgs/create-a-saml-identity-provider) | Create a SAML identity provider. |
| DELETE | [/org/saml/idp](/docs/developer-tools/api/orgs/delete-an-saml-identity-provider) | Delete an SAML identity provider. |
| GET | [/org/shortlinks](/docs/developer-tools/api/orgs/get-the-shortlinks-for-an-org) | Get the shortlinks for an org. |
| GET | [/org/skills](/docs/developer-tools/api/orgs/list-every-skill-that-belongs-to-the-caller's-organization) | List every skill that belongs to the caller's organization. |
| GET | [/user/org](/docs/developer-tools/api/orgs/get-a-user's-org) | Get a user's org. |
