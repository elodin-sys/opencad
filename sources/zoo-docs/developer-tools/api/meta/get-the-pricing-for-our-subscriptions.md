Source URL: https://zoo.dev/docs/developer-tools/api/meta/get-the-pricing-for-our-subscriptions
Title: Get the pricing for our subscriptions

# Get the pricing for our subscriptions

hidden

No path, query string, header, or cookie parameters

#### Response
- ##### 

  200 OK

  - \+

    ### { ... }

    - \+

      ### \[key\]:

      \[\[ ... \]

      - \+

        ### one of

        //

        - \+

          ### { ... }

          //

          - \+

            ### type:

            ,

            //

            - \+

              ### individual

              //

              ##### {

              - ### type:

                `"individual"`

              ##### }

            - \+

              ### organization

              //

              ##### {

              - ### type:

                `"organization"`,

              - ### saml_sso:

                boolean

                //

              ##### }

          - ### annual_discount:

            numberdouble,

            //

          - ### description:

            string,

            //

          - ### display_name:

            string,

            //

          - ### ml_custom_models:

            boolean,

            //

          - ### monthly_pay_as_you_go_api_credits:

            numberuint64,

            //

          - ### monthly_pay_as_you_go_api_credits_monetary_value:

            numberUSD Price,

            //

          - ### name:

            string,

            //

          - ### pay_as_you_go_api_credit_price:

            numberUSD Price,

            //

          - ### billing_mode:

            `"standard"`+1▾

            - //<span class="small">Standard self-serve billing through the normal subscription flow.</span>
              `"standard"`
            - //<span class="small">Contract-managed billing controlled outside the standard subscription flow.</span>
              `"contract"`

            ,

            //

          - \+

            ### endpoints_included:

            \[\[ ... \],

            //

            - ### one of

              `"modeling"`+2▾

              - //<span class="small">The modeling API.</span>
                `"modeling"`
              - //<span class="small">Machine learning API.</span>
                `"ml"`
              - //<span class="small">File API.</span>
                `"file"`

              //

            ##### \]

          - \+

            ### features:

            \[\[ ... \],

            //

            - \+

              ### info

              //

              ##### {

              - ### info:

                string

                //

              ##### }

            ##### \]

          - \+

            ### price:

            ,

            //

            - \+

              ### contract

              //

              ##### {

              - ### type:

                `"contract"`

              ##### }

            - \+

              ### flat

              //

              ##### {

              - ### type:

                `"flat"`,

              - ### price:

                numberUSD Price,

                //

              - ### interval:

                `"day"`+4▾

                - //<span class="small">Day.</span>
                  `"day"`
                - //<span class="small">Month.</span>
                  `"month"`
                - //<span class="small">Week.</span>
                  `"week"`
                - //<span class="small">Year.</span>
                  `"year"`
                - //<span class="small">Don't use.</span>
                  `"unknown"`

                //

              ##### }

            - \+

              ### per_user

              //

              ##### {

              - ### type:

                `"per_user"`,

              - ### price:

                numberUSD Price,

                //

              - ### interval:

                `"day"`+4▾

                - //<span class="small">Day.</span>
                  `"day"`
                - //<span class="small">Month.</span>
                  `"month"`
                - //<span class="small">Week.</span>
                  `"week"`
                - //<span class="small">Year.</span>
                  `"year"`
                - //<span class="small">Don't use.</span>
                  `"unknown"`

                //

              ##### }

          - \+

            ### share_links:

            \[\[ ... \],

            //

            - ### one of

              `"public"`+2▾

              - //<span class="small">Publicly accessible share links.</span>
                `"public"`
              - //<span class="small">Share links guarded by a password.</span>
                `"password_protected"`
              - //<span class="small">Share links restricted to members of the organization.</span>
                `"organization_only"`

              //

            ##### \]

          - ### support_tier:

            `"community"`+3▾

            - //<span class="small">Community support.</span>
              `"community"`
            - //<span class="small">Standard email support.</span>
              `"standard_email"`
            - //<span class="small">Priority email support.</span>
              `"priority_email"`
            - //<span class="small">Premium support.</span>
              `"premium"`

            ,

            //

          - ### training_data_behavior:

            `"always"`+2▾

            - //<span class="small">The data is always used for training and cannot be turned off.</span>
              `"always"`
            - //<span class="small">The data is used for training by default, but can be turned off.</span>
              `"default_on"`
            - //<span class="small">The data is not used for training by default, but can be turned on.</span>
              `"default_off"`

            ,

            //

          - \+

            ### zoo_tools_included:

            \[\[ ... \]

            //

            - ### one of

              `"modeling_app"`+1▾

              - //<span class="small">The modeling app.</span>
                `"modeling_app"`
              - //<span class="small">The Text-to-CAD UI.</span>
                `"text_to_cad"`

              //

            ##### \]

          ##### }

      ##### \]

    ##### }

#### Examples

get

/pricing/subscriptionscurlgopythonrusttypescript



200 OK

Response
