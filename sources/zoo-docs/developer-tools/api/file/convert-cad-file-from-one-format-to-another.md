Source URL: https://zoo.dev/docs/developer-tools/api/file/convert-cad-file-from-one-format-to-another
Title: Convert CAD file from one format to another.

# Convert CAD file from one format to another.

`POST /file/conversion`

This takes a HTTP multipart body with these fields in any order:

 - The input and output format options (as JSON), name is 'body'.  - The files to convert, in raw binary. Must supply filenames.

This starts a conversion job and returns the `id` of the operation. You can use the `id` returned from the request to get status information about the async operation from the `/async/operations/{id}` endpoint.

## Section

[File](/docs/developer-tools/api/file)

## Parameters

No parameters.

## Request Body

Convert files to other formats

| Content-Type | Schema |
| --- | --- |
| multipart/form-data | ConversionParams |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 201 | successful creation | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
curl -X POST "https://api.zoo.dev/file/conversion" \
  --header "Authorization: Bearer $ZOO_API_TOKEN"
```
