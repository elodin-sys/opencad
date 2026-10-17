Source URL: https://zoo.dev/docs/developer-tools/api/users/stores-authenticated-cad-user-info-form-data-for-the-current-user
Title: Stores authenticated CAD user info form data for the current user

# Stores authenticated CAD user info form data for the current user

hidden

#### HTTP Request
- \+

  ### { ... }application/json

  //

  - ### has_used_zoo_design_studio_or_api_before:

    boolean,

    //

  - ### how_did_you_find_us_other:

    string,

    //

  - ### location_city:

    string,

    //

  - ### location_country:

    string,

    //

  - ### location_state:

    string,

    //

  - ### number_of_cad_users:

    string,

    //

  - ### what_are_you_building:

    string,

    //

  - ### cad_experience_level:

    `"beginner"`+2▾

    - //<span class="small">Beginner experience level.</span>
      `"beginner"`
    - //<span class="small">Intermediate experience level.</span>
      `"intermediate"`
    - //<span class="small">Advanced experience level.</span>
      `"advanced"`

    ,

    //

  - ### cad_industry:

    `"mechanical_engineering"`+9▾

    - //<span class="small">Mechanical engineering.</span>
      `"mechanical_engineering"`
    - //<span class="small">Manufacturing.</span>
      `"manufacturing"`
    - //<span class="small">Automotive.</span>
      `"automotive"`
    - //<span class="small">Aerospace.</span>
      `"aerospace"`
    - //<span class="small">Civil engineering.</span>
      `"civil_engineering"`
    - //<span class="small">Electrical engineering.</span>
      `"electrical_engineering"`
    - //<span class="small">Construction.</span>
      `"construction"`
    - //<span class="small">Product design.</span>
      `"product_design"`
    - //<span class="small">Architecture.</span>
      `"architecture"`
    - //<span class="small">Other industry.</span>
      `"other"`

    ,

    //

  - ### cad_user_type:

    `"student_or_researcher"`+2▾

    - //<span class="small">Student or researcher persona.</span>
      `"student_or_researcher"`
    - //<span class="small">Hobbyist persona.</span>
      `"hobbyist"`
    - //<span class="small">Professional persona.</span>
      `"professional"`

    ,

    //

  - ### company_size:

    `"one_to_ten"`+6▾

    - //<span class="small">1-10 people.</span>
      `"one_to_ten"`
    - //<span class="small">11-50 people.</span>
      `"eleven_to_fifty"`
    - //<span class="small">51-200 people.</span>
      `"fifty_one_to_two_hundred"`
    - //<span class="small">201-500 people.</span>
      `"two_hundred_one_to_five_hundred"`
    - //<span class="small">501-1000 people.</span>
      `"five_hundred_one_to_one_thousand"`
    - //<span class="small">1000+ people.</span>
      `"one_thousand_plus"`
    - //<span class="small">Other company size.</span>
      `"other"`

    ,

    //

  - ### design_workflow:

    `"sketching"`+3▾

    - //<span class="small">Sketch-first workflow.</span>
      `"sketching"`
    - //<span class="small">Code-first workflow.</span>
      `"coding"`
    - //<span class="small">AI-first workflow.</span>
      `"ai"`
    - //<span class="small">Hybrid workflow spanning multiple approaches.</span>
      `"hybrid_approach"`

    ,

    //

  - ### how_did_you_find_us:

    `"google"`+9▾

    - //<span class="small">Found via Google search.</span>
      `"google"`
    - //<span class="small">Found via X/Twitter.</span>
      `"x"`
    - //<span class="small">Found via TikTok.</span>
      `"tiktok"`
    - //<span class="small">Found via Reddit.</span>
      `"reddit"`
    - //<span class="small">Found via Payload Space.</span>
      `"payload_space"`
    - //<span class="small">Found via YouTube.</span>
      `"youtube"`
    - //<span class="small">Found via Instagram.</span>
      `"instagram"`
    - //<span class="small">Found via Facebook.</span>
      `"facebook"`
    - //<span class="small">Found through friend referral or word of mouth.</span>
      `"word_of_mouth"`
    - //<span class="small">Found through another source described in free text.</span>
      `"other"`

    //

  ##### }

#### Response
##### 

204 No Content

#### Examples

put

/website/forms/cad-user-infocurlgopythonrusttypescript
