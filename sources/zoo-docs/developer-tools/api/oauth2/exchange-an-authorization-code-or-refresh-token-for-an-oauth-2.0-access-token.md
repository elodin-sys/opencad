Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/exchange-an-authorization-code-or-refresh-token-for-an-oauth-2.0-access-token
Title: Exchange an authorization code or refresh token for an OAuth 2.0 access token

# Exchange an authorization code or refresh token for an OAuth 2.0 access token

hidden

#### HTTP Request
- \+

  ### { ... }application/x-www-form-urlencoded

  //

  - ### client_id:

    stringUUID,

    //

  - ### code:

    string,

    //

  - ### code_verifier:

    string,

    //

  - ### redirect_uri:

    stringURL,

    //

  - ### refresh_token:

    string,

    //

  - ### grant_type:

    `"authorization_code"`+1▾

    - //<span class="small">The authorization code grant.</span>
      `"authorization_code"`
    - //<span class="small">The refresh token grant.</span>
      `"refresh_token"`

    //

  ##### }

#### Response
##### 

NaN Unknown

#### Examples

post

/oauth2/tokencurlgopythonrusttypescript
