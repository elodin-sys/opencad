Source URL: https://zoo.dev/docs/developer-tools/api/users/get-extended-information-about-a-user
Title: Get extended information about a user

# Get extended information about a user

hidden

#### Path parameters
- ### /{id}

  string

  //

#### Response
- ##### 

  200 OK

  - \+

    ### { ... }

    //

    - ### allow_pay_as_you_go:

      boolean,

      //

    - ### can_train_on_data:

      boolean,

      //

    - ### company:

      string,

      //

    - ### created_at:

      stringISO-8601,

      //

    - ### deletion_scheduled:

      boolean,

      //

    - ### discord:

      string,

      //

    - ### email:

      stringEmail Address,

      //

    - ### email_verified:

      stringISO-8601,

      //

    - ### first_name:

      string,

      //

    - ### github:

      string,

      //

    - ### id:

      stringUUID,

      //

    - ### image:

      stringURL,

      //

    - ### is_onboarded:

      boolean,

      //

    - ### is_service_account:

      boolean,

      //

    - ### last_name:

      string,

      //

    - ### name:

      string,

      //

    - ### phone:

      stringPhone Number,

      //

    - ### stripe_id:

      string,

      //

    - ### updated_at:

      stringISO-8601,

      //

    - ### username:

      string,

      //

    - ### block:

      `"missing_payment_method"`+5▾

      - //<span class="small">The user is missing a payment method and has exceeded their free API call credits for the month.</span>
        `"missing_payment_method"`
      - //<span class="small">The users payment method has failed.</span>
        `"payment_method_failed"`
      - //<span class="small">The account reached its configured pay-as-you-go collection threshold.</span>
        `"billing_threshold_reached"`
      - //<span class="small">The user exhausted their included credits without opting into pay-as-you-go charges.</span>
        `"pay_as_you_go_disabled"`
      - //<span class="small">The user repeatedly upgraded and downgraded to recycle free-plan credits.</span>
        `"upgrade_downgrade_abuse"`
      - //<span class="small">An explicit admin block that can only be removed by admin intervention.</span>
        `"admin"`

      //

    ##### }

#### Examples

get

/users-extended/{id}curlgopythonrusttypescript



200 OK

Response
