Source URL: https://zoo.dev/docs/developer-tools/api/oauth2/approve-a-pending-oauth-2.0-authorization-request
Title: Approve a pending OAuth 2.0 authorization request

# Approve a pending OAuth 2.0 authorization request

hidden

#### Path parameters
- ### /{request_id}

  stringUUID

  //

#### Response
- ##### 

  200 OK

  - \+

    ### redirect_url

    //

    ##### {

    - ### redirect_url:

      string

      //

    ##### }

#### Examples

post

/oauth2/authorization-requests/{request_id}/approvecurlgopythonrusttypescript



200 OK

Response
