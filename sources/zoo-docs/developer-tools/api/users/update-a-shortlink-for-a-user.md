Source URL: https://zoo.dev/docs/developer-tools/api/users/update-a-shortlink-for-a-user
Title: Update a shortlink for a user.

# Update a shortlink for a user.

`PUT /user/shortlinks/{key}`

This endpoint requires authentication by any Zoo user. It updates a shortlink for the user.

This endpoint really only allows you to change the `restrict_to_org` setting of a shortlink. Thus it is only useful for folks who are part of an org. If you are not part of an org, you will not be able to change the `restrict_to_org` status.

## Section

[Users](/docs/developer-tools/api/users)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The key of the shortlink. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/json | UpdateShortlinkRequest |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 204 | resource updated |  |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X PUT "https://api.zoo.dev/user/shortlinks/{key}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
  --header "Content-Type: application/json" \
  --data '{}'
```
