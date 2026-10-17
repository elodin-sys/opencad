Source URL: https://zoo.dev/docs/developer-tools/api/ml/open-a-websocket-to-prompt-the-ml-copilot
Title: Open a websocket to prompt the ML copilot.

# Open a websocket to prompt the ML copilot.

`GET /ws/ml/reasoning/{id}`

An endpoint within the Zoo API.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The ID of the async operation. |

## Request Body

Websocket requests

| Content-Type | Schema |
| --- | --- |
| application/json | MlCopilotClientMessage |

## Responses

| Status | Description | Content-Type |
| --- | --- | --- |
| 101 | Negotiating protocol upgrade from HTTP/1.1 to WebSocket |  |
| default | Websocket responses | application/json |
| 4XX | Error | application/json |
| 5XX | Error | application/json |

## Example

```bash
# WebSocket endpoint.
# Use an SDK or a WebSocket client.
```
