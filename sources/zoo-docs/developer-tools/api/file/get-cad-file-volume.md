Source URL: https://zoo.dev/docs/developer-tools/api/file/get-cad-file-volume
Title: Get CAD file volume.

# Get CAD file volume.

`POST /file/volume`

We assume any file given to us has one consistent unit throughout. We also assume the file is at the proper scale.

This endpoint returns the cubic measure units.

In the future, we will use the units inside the file if they are given and do any conversions if necessary for the calculation. But currently, that is not supported.

Get the volume of an object in a CAD file. If the file is larger than 25MB, it will be performed asynchronously.

If the operation is performed asynchronously, the `id` of the operation will be returned. You can use the `id` returned from the request to get status information about the async operation from the `/async/operations/{id}` endpoint.

## Section

[File](/docs/developer-tools/api/file)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| src_format | query | FileImportFormat | yes | The format of the file. |
| output_unit | query | UnitVolume | no | The output unit for the volume. |

## Request Body

| Content-Type | Schema |
| --- | --- |
| application/octet-stream | string |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/file/volume" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
