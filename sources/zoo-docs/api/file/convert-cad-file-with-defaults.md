Source URL: https://zoo.dev/docs/api/file/convert-cad-file-with-defaults
Title: Convert CAD file with defaults.

# Convert CAD file with defaults.

`POST /file/conversion/{src_format}/{output_format}`

If you wish to specify the conversion options, use the `/file/conversion` endpoint instead.

Convert a CAD file from one format to another. If the file being converted is larger than 25MB, it will be performed asynchronously.

If the conversion is performed synchronously, the contents of the converted file (`output`) will be returned as a base64 encoded string.

If the operation is performed asynchronously, the `id` of the operation will be returned. You can use the `id` returned from the request to get status information about the async operation from the `/async/operations/{id}` endpoint.

## Section

[File](/docs/developer-tools/api/file)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| src_format | path | FileImportFormat | yes | The format of the file to convert. |
| output_format | path | FileExportFormat | yes | The format the file should be converted to. |

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
curl -X POST "https://api.zoo.dev/file/conversion/{src_format}/{output_format}" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
