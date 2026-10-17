Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/start-an-oauth-2.0-authorization-code-flow-with-pkce
Title: Start an OAuth 2.0 authorization code flow with PKCE

# Start an OAuth 2.0 authorization code flow with PKCE

hidden

#### Query string parameters
- ### ?response_type=

  `"code"`

  //

- ### &client_id=

  UUID

  //

- ### &redirect_uri=

  URL

  //

- ### &state=

  string

  //

- ### &scope=

  string

  //

- ### &code_challenge=

  string

  //

- ### &code_challenge_method=

  `"PLAIN"`+1▾

  - //<span class="small">Plain code challenge comparison.</span>
    `"PLAIN"`
  - //<span class="small">SHA-256 based PKCE challenge.</span>
    `"S256"`

  //

#### Response
#### Examples

get

/oauth2/authorizecurlgopythonrusttypescript
