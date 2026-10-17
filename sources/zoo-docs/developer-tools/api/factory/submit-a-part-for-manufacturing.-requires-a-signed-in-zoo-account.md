Source URL: https://zoo.dev/docs/developer-tools/api/factory/submit-a-part-for-manufacturing.-requires-a-signed-in-zoo-account
Title: Submit a part for manufacturing. Requires a signed-in Zoo account

# Submit a part for manufacturing. Requires a signed-in Zoo account

hidden

#### HTTP Request
- ### HTTP BodyBinary

  ### Content-Type:multipart/form-data

#### Response
- ##### 

  201 Created

  - \+

    ### { ... }

    //

    - ### current_version_id:

      stringUUID,

      //

    - ### id:

      stringUUID,

      //

    - ### status:

      string

      //

    ##### }

#### Examples

post

/user/factory/jobscurlgopythonrusttypescript



201 Created

Response
