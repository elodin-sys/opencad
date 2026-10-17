Source URL: https://zoo.dev/docs/developer-tools/api/users/publicly-remove-an-email-address-from-a-mailing-list-by-slug
Title: Publicly remove an email address from a mailing list by slug

# Publicly remove an email address from a mailing list by slug

hidden

#### Path parameters
- ### /{slug}

  string

  //

#### HTTP Request
- \+

  ### emailapplication/json

  //

  ##### {

  - ### email:

    stringEmail Address

    //

  ##### }

#### Response
##### 

204 No Content

#### Examples

put

/website/email-marketing-lists/{slug}/unsubscribecurlgopythonrusttypescript
