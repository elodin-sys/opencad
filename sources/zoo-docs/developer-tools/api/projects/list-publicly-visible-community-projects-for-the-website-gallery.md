Source URL: https://zoo.dev/docs/developer-tools/api/projects/list-publicly-visible-community-projects-for-the-website-gallery
Title: List publicly visible community projects for the website/gallery

# List publicly visible community projects for the website/gallery

No path, query string, header, or cookie parameters

#### Response
- ##### 

  200 OK

  - \+

    ### \[ ... \]

    - \+

      ### { ... }

      //

      - ### description:

        string,

        //

      - ### id:

        stringUUID,

        //

      - ### like_count:

        numberint64,

        //

      - ### liked:

        boolean,

        //

      - ### preview_url:

        string,

        //

      - ### published_at:

        stringISO-8601,

        //

      - ### title:

        string,

        //

      - \+

        ### categories:

        \[\[ ... \],

        //

        - \+

          ### { ... }

          //

          - ### description:

            string,

            //

          - ### display_name:

            string,

            //

          - ### id:

            stringUUID,

            //

          - ### slug:

            string,

            //

          - ### sort_order:

            numberint64

            //

          ##### }

        ##### \]

      - \+

        ### owner:

        {{ ... }

        //

        - ### username:

          string

          //

        ##### }

      ##### }

    ##### \]

#### Examples

get

/projects/publiccurlgopythonrusttypescript



200 OK

Response
