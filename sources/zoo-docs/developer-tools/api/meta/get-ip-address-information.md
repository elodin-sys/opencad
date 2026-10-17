Source URL: https://zoo.dev/docs/developer-tools/api/meta/get-ip-address-information
Title: Get ip address information

# Get ip address information

hidden

No path, query string, header, or cookie parameters

#### Response
- ##### 

  200 OK

  - \+

    ### { ... }

    //

    - ### asn:

      numberint64,

      //

    - ### city:

      string,

      //

    - ### continent_code:

      string,

      //

    - ### country:

      string,

      //

    - ### country_code:

      string,

      //

    - ### country_code3:

      string,

      //

    - ### ip:

      stringip,

      //

    - ### is_in_european_union:

      boolean,

      //

    - ### latitude:

      numberdouble,

      //

    - ### longitude:

      numberdouble,

      //

    - ### offset:

      numberint64,

      //

    - ### organization:

      string,

      //

    - ### postal_code:

      string,

      //

    - ### region:

      string,

      //

    - ### region_code:

      string,

      //

    - ### timezone:

      string

      //

    ##### }

#### Examples

get

/\_meta/ipinfocurlgopythonrusttypescript



200 OK

Response
