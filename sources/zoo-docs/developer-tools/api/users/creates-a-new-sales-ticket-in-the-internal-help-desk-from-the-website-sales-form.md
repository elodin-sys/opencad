Source URL: https://zoo.dev/docs/developer-tools/api/users/creates-a-new-sales-ticket-in-the-internal-help-desk-from-the-website-sales-form
Title: Creates a new sales ticket in the internal help desk from the website sales form

# Creates a new sales ticket in the internal help desk from the website sales form

hidden

#### HTTP Request
- \+

  ### { ... }application/json

  //

  - \+

    ### cad_platforms:

    \[\[ ... \],

    //

    - string

    ##### \]

  - ### company:

    string,

    //

  - ### email:

    stringEmail Address,

    //

  - ### first_name:

    string,

    //

  - ### industry:

    string,

    //

  - ### job_title:

    string,

    //

  - ### last_name:

    string,

    //

  - ### message:

    string,

    //

  - ### num_cad_users:

    string,

    //

  - ### phone:

    string,

    //

  - ### inquiry_type:

    `"pilot_inquiry"`+5▾

    - //<span class="small">Inquiries related to pilots (on the enterprise page).</span>
      `"pilot_inquiry"`
    - //<span class="small">General inquiry about the service or product.</span>
      `"general_inquiry"`
    - //<span class="small">Questions related to sales or purchasing.</span>
      `"sales_question"`
    - //<span class="small">Inquiry from a developer, typically technical in nature.</span>
      `"developer_inquiry"`
    - //<span class="small">Opportunity for partnership or collaboration.</span>
      `"partnership_opportunity"`
    - //<span class="small">Other inquiries related to sales that do not fit predefined categories.</span>
      `"other_sales_inquiry"`

    //

  ##### }

#### Response
##### 

204 No Content

#### Examples

put

/website/forms/salescurlgopythonrusttypescript
