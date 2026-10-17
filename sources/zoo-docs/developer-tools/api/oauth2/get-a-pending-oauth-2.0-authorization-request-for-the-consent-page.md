Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/get-a-pending-oauth-2.0-authorization-request-for-the-consent-page
Title: Get a pending OAuth 2.0 authorization request for the consent page

# Get a pending OAuth 2.0 authorization request for the consent page

hidden

#### Path parameters
- ### /{request_id}

  stringUUID

  //

#### Response
- ##### 

  200 OK

  - \+

    ### { ... }

    //

    - ### app_name:

      string,

      //

    - ### expires_at:

      stringISO-8601,

      //

    - ### owner_name:

      string,

      //

    - ### redirect_uri:

      stringURL,

      //

    - ### request_id:

      stringUUID,

      //

    - \+

      ### scopes:

      \[\[ ... \]

      //

      - ### one of

        `"user:read"`+2▾

        - //<span class="small">Grants read access to the authenticated user's profile.</span>
          `"user:read"`
        - //<span class="small">Grants access to modeling APIs.</span>
          `"modeling"`
        - //<span class="small">Grants write access to admin APIs.</span>
          `"admin:write"`

        //

      ##### \]

    ##### }

#### Examples

get

/oauth2/authorization-requests/{request_id}curlgopythonrusttypescript



200 OK

Response
