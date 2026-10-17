Source URL: https://zoo.dev/docs/developer-tools/api/users/creates-a-new-support-ticket-in-the-internal-help-desk-from-the-website-support-form
Title: Creates a new support ticket in the internal help desk from the website support form

# Creates a new support ticket in the internal help desk from the website support form

hidden

#### HTTP Request
- \+

  ### { ... }application/json

  //

  - ### company:

    string,

    //

  - ### email:

    stringEmail Address,

    //

  - ### first_name:

    string,

    //

  - ### last_name:

    string,

    //

  - ### message:

    string,

    //

  - ### phone:

    string,

    //

  - ### inquiry_type:

    `"technical_support"`+2▾

    - //<span class="small">Request for technical support or troubleshooting.</span>
      `"technical_support"`
    - //<span class="small">Questions or requests related to account management.</span>
      `"account_management"`
    - //<span class="small">Other support-related inquiries that do not fit predefined categories.</span>
      `"other_support_inquiry"`

    //

  ##### }

#### Response
##### 

204 No Content

#### Examples

put

/website/forms/supportcurlgopythonrusttypescript
