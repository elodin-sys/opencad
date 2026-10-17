Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/request-a-device-access-token
Title: Request a device access token

# Request a device access token

hidden

#### HTTP Request
- \+

  ### { ... }application/x-www-form-urlencoded

  //

  - ### client_id:

    stringUUID,

    //

  - ### device_code:

    stringUUID,

    //

  - ### grant_type:

    `"urn:ietf:params:oauth:grant-type:device_code"`

    //

  ##### }

#### Response
##### 

NaN Unknown

#### Examples

post

/oauth2/device/tokencurlgopythonrusttypescript
