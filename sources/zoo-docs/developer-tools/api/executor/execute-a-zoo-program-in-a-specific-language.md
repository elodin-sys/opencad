Source URL: https://zoo.dev/docs/developer-tools/api/executor/execute-a-zoo-program-in-a-specific-language
Title: Execute a Zoo program in a specific language

# Execute a Zoo program in a specific language

hidden

#### Path parameters
- ### /{lang}

  `"go"`+2▾

  - //<span class="small">The \`go\` programming language.</span>
    `"go"`
  - //<span class="small">The \`python\` programming language.</span>
    `"python"`
  - //<span class="small">The \`node\` programming language.</span>
    `"node"`

  //

#### Query string parameters
- ### ?output=

  string

  //

#### HTTP Request
- ### HTTP BodyBinary

  ### Content-Type:application/octet

#### Response
- ##### 

  201 Created

  - \+

    ### { ... }

    //

    - ### stderr:

      string,

      //

    - ### stdout:

      string,

      //

    - \+

      ### output_files:

      \[\[ ... \]

      //

      - \+

        ### { ... }

        //

        - ### contents:

          string,

          //

        - ### name:

          string

          //

        ##### }

      ##### \]

    ##### }

#### Examples

post

/file/execute/{lang}curlgopythonrusttypescript



201 Created

Response
