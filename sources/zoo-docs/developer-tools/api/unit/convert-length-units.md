Source URL: https://zoo.dev/docs/developer-tools/api/unit/convert-length-units
Title: Convert length units.

# Convert length units.

`GET /unit/conversion/length/{input_unit}/{output_unit}`

Convert a length unit value to another length unit value. This is a nice endpoint to use for helper functions.

## Section

[Unit](/docs/developer-tools/api/unit)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| input_unit | path | UnitLength | yes | The source format of the unit. |
| output_unit | path | UnitLength | yes | The output format of the unit. |
| value | query | number | yes | The initial value. |

## Request Body

No request body.

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 200 | successful operation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl "https://api.zoo.dev/unit/conversion/length/{input_unit}/{output_unit}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
