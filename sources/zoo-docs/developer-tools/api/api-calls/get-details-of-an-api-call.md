Source URL: https://zoo.dev/docs/developer-tools/api/api-calls/get-details-of-an-api-call
Title: Get details of an API call

# Get details of an API call

hidden

#### Path parameters
- ### /{id}

  stringUUID

  //

#### Response
- ##### 

  200 OK

  - \+

    ### { ... }

    //

    - ### completed_at:

      stringISO-8601,

      //

    - ### created_at:

      stringISO-8601,

      //

    - ### duration:

      numberDuration,

      //

    - ### email:

      stringEmail Address,

      //

    - ### endpoint:

      string,

      //

    - ### id:

      stringUUID,

      //

    - ### ip_address:

      stringip,

      //

    - ### minutes:

      numberint32,

      //

    - ### org_id:

      stringUUID,

      //

    - ### origin:

      string,

      //

    - ### price:

      numberUSD Price,

      //

    - ### request_query_params:

      string,

      //

    - ### seconds:

      numberint32,

      //

    - ### started_at:

      stringISO-8601,

      //

    - ### status_code:

      numberint32,

      //

    - ### stripe_invoice_item_id:

      string,

      //

    - ### token:

      stringUUID,

      //

    - ### updated_at:

      stringISO-8601,

      //

    - ### user_agent:

      string,

      //

    - ### user_id:

      stringUUID,

      //

    - ### method:

      `"OPTIONS"`+9▾

      - //<span class="small">The \`OPTIONS\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.2.1).</span>
        `"OPTIONS"`
      - //<span class="small">The \`GET\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.1).</span>
        `"GET"`
      - //<span class="small">The \`POST\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.1).</span>
        `"POST"`
      - //<span class="small">The \`PUT\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.1).</span>
        `"PUT"`
      - //<span class="small">The \`DELETE\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.5).</span>
        `"DELETE"`
      - //<span class="small">The \`HEAD\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.2).</span>
        `"HEAD"`
      - //<span class="small">The \`TRACE\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3).</span>
        `"TRACE"`
      - //<span class="small">The \`CONNECT\` method as defined in \[RFC 7231\](https://tools.ietf.org/html/rfc7231#section-4.3.6).</span>
        `"CONNECT"`
      - //<span class="small">The \`PATCH\` method as defined in \[RFC 5789\](https://tools.ietf.org/html/rfc5789).</span>
        `"PATCH"`
      - //<span class="small">A catch all.</span>
        `"EXTENSION"`

      //

    ##### }

#### Examples

get

/api-calls/{id}curlgopythonrusttypescript



200 OK

Response
