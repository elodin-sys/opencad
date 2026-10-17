Source URL: https://zoo.dev/docs/developer-tools/api/unit/convert-torque-units
Title: Convert torque units.

# Convert torque units.

`GET /unit/conversion/torque/{input_unit}/{output_unit}`

Convert a torque unit value to another torque unit value. This is a nice endpoint to use for helper functions.

## Section

[Unit](/docs/developer-tools/api/unit)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| input_unit | path | UnitTorque | yes | The source format of the unit. |
| output_unit | path | UnitTorque | yes | The output format of the unit. |
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
curl "https://api.zoo.dev/unit/conversion/torque/{input_unit}/{output_unit}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
