Source URL: https://zoo.dev/docs/developer-tools/api/ml/generate-code-completions-for-kcl
Title: Generate code completions for KCL

# Generate code completions for KCL

beta

#### HTTP Request
- \+

  ### { ... }application/json

  //

  - ### max_tokens:

    numberuint16,

    //

  - ### model_version:

    string,

    //

  - ### n:

    numberuint8,

    //

  - ### nwo:

    string,

    //

  - ### prompt:

    string,

    //

  - \+

    ### stop:

    \[\[ ... \],

    //

    - string

    ##### \]

  - ### stream:

    boolean,

    //

  - ### suffix:

    string,

    //

  - ### temperature:

    numberfloat,

    //

  - ### top_p:

    numberfloat,

    //

  - \+

    ### extra:

    {{ ... }

    //

    - ### language:

      string,

      //

    - ### next_indent:

      numberuint8,

      //

    - ### prompt_tokens:

      numberuint32,

      //

    - ### suffix_tokens:

      numberuint32,

      //

    - ### trim_by_indentation:

      boolean

      //

    ##### }

  ##### }

#### Response
- ##### 

  201 Created

  - \+

    ### completions

    //

    ##### {

    - \+

      ### completions:

      \[\[ ... \]

      //

      - string

      ##### \]

    ##### }

#### Examples

post

/ml/kcl/completionscurlgopythonrusttypescript



201 Created

Response
