Source URL: https://zoo.dev/docs/developer-tools/api/authentication
Title: Authentication

# Authentication

Zoo APIs use API tokens to authenticate requests. Create and manage tokens from your Zoo account, then send the token as a bearer token.

```bash
curl "https://api.zoo.dev/user" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```

All API requests must be made over HTTPS. Requests without authentication will fail.
