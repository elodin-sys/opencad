Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/listen-for-callbacks-for-the-oauth-2.0-provider
Title: Listen for callbacks for the OAuth 2.0 provider

# Listen for callbacks for the OAuth 2.0 provider

hidden

#### Path parameters
- ### /{provider}

  `"apple"`+7▾

  - //<span class="small">The Apple account provider.</span>
    `"apple"`
  - //<span class="small">The Discord account provider.</span>
    `"discord"`
  - //<span class="small">The Google account provider.</span>
    `"google"`
  - //<span class="small">The ZooCorp account provider (aka https://auth.corp.zoo.dev).</span>
    `"zoo_corp"`
  - //<span class="small">The GitHub account provider.</span>
    `"github"`
  - //<span class="small">The Microsoft account provider.</span>
    `"microsoft"`
  - //<span class="small">The SAML account provider.</span>
    `"saml"`
  - //<span class="small">Test provider for integration tests (only available during testing).</span>
    `"test_provider"`

  //

#### Query string parameters
- ### ?code=

  string

  //

- ### &state=

  string

  //

- ### &id_token=

  string

  //

- ### &user=

  string

  //

#### Response
#### Examples

get

/oauth2/provider/{provider}/callbackcurlgopythonrusttypescript
