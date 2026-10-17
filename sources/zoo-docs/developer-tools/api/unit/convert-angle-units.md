Source URL: https://zoo.dev/docs/developer-tools/api/unit/convert-angle-units
Title: Convert angle units.

# Convert angle units.

`GET /unit/conversion/angle/{input_unit}/{output_unit}`

Convert an angle unit value to another angle unit value. This is a nice endpoint to use for helper functions.

## Section

[Unit](/docs/developer-tools/api/unit)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| input_unit | path | UnitAngle | yes | The source format of the unit. |
| output_unit | path | UnitAngle | yes | The output format of the unit. |
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
curl "https://api.zoo.dev/unit/conversion/angle/{input_unit}/{output_unit}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
