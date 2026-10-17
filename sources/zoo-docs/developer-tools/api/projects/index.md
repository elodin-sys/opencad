Source URL: https://zoo.dev/docs/developer-tools/api/projects
Title: Projects

# Projects

Operations for user-owned projects, public project discovery, publishing, voting, and share links.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/projects/categories](/docs/developer-tools/api/projects/list-the-active-categories-available-for-project-submissions) | List the active categories available for project submissions. |
| GET | [/projects/public](/docs/developer-tools/api/projects/list-publicly-visible-community-projects-for-the-website/gallery) | List publicly visible community projects for the website/gallery. |
| GET | [/projects/public/{id}](/docs/developer-tools/api/projects/get-one-publicly-visible-community-project) | Get one publicly visible community project. |
| GET | [/projects/public/{id}/download](/docs/developer-tools/api/projects/download-a-published-public-project-as-a-tar-archive) | Download a published public project as a tar archive. |
| GET | [/projects/public/{id}/thumbnail](/docs/developer-tools/api/projects/fetch-the-public-thumbnail-for-a-published-project) | Fetch the public thumbnail for a published project. |
| POST | [/projects/public/{id}/vote](/docs/developer-tools/api/projects/add-the-authenticated-user's-upvote-to-a-published-community-project) | Add the authenticated user's upvote to a published community project. |
| DELETE | [/projects/public/{id}/vote](/docs/developer-tools/api/projects/remove-the-authenticated-user's-upvote-from-a-published-community-project) | Remove the authenticated user's upvote from a published community project. |
| GET | [/user/projects](/docs/developer-tools/api/projects/list-the-authenticated-user's-projects) | List the authenticated user's projects. |
| POST | [/user/projects](/docs/developer-tools/api/projects/create-a-draft-project-for-the-authenticated-user) | Create a draft project for the authenticated user. |
| GET | [/user/projects/{id}](/docs/developer-tools/api/projects/get-one-of-the-authenticated-user's-projects) | Get one of the authenticated user's projects. |
| PUT | [/user/projects/{id}](/docs/developer-tools/api/projects/replace-one-of-the-authenticated-user's-projects) | Replace one of the authenticated user's projects. |
| DELETE | [/user/projects/{id}](/docs/developer-tools/api/projects/delete-one-of-the-authenticated-user's-projects) | Delete one of the authenticated user's projects. |
| GET | [/user/projects/{id}/download](/docs/developer-tools/api/projects/download-one-of-the-authenticated-user's-projects-as-a-tar-archive) | Download one of the authenticated user's projects as a tar archive. |
| PUT | [/user/projects/{id}/organization](/docs/developer-tools/api/projects/move-one-of-the-authenticated-user's-projects-into-their-active-organization-library) | Move one of the authenticated user's projects into their active organization library. |
| DELETE | [/user/projects/{id}/organization](/docs/developer-tools/api/projects/move-an-organization-project-back-to-its-creator's-personal-library) | Move an organization project back to its creator's personal library. |
| POST | [/user/projects/{id}/publish](/docs/developer-tools/api/projects/submit-one-of-the-authenticated-user's-projects-for-public-review) | Submit one of the authenticated user's projects for public review. |
| GET | [/user/projects/{id}/share-links](/docs/developer-tools/api/projects/list-share-links-for-one-of-the-authenticated-user's-projects) | List share links for one of the authenticated user's projects. |
| POST | [/user/projects/{id}/share-links](/docs/developer-tools/api/projects/create-a-share-link-for-one-of-the-authenticated-user's-projects) | Create a share link for one of the authenticated user's projects. |
| DELETE | [/user/projects/{id}/share-links/{key}](/docs/developer-tools/api/projects/delete-one-share-link-for-one-of-the-authenticated-user's-projects) | Delete one share link for one of the authenticated user's projects. |
| GET | [/user/projects/{id}/thumbnail](/docs/developer-tools/api/projects/fetch-the-authenticated-owner's-current-project-thumbnail) | Fetch the authenticated owner's current project thumbnail. |
