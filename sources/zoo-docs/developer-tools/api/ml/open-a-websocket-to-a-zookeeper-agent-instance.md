Source URL: https://zoo.dev/docs/developer-tools/api/ml/open-a-websocket-to-a-zookeeper-agent-instance
Title: Open a websocket to a Zookeeper agent instance.

# Open a websocket to a Zookeeper agent instance.

`GET /ws/ml/copilot`

Remember to authenticate before sending messages. [For WebSockets it's a little different.](/docs/developer-tools/api/authentication?lang=curl#websockets)

As with all Zoo WebSockets, you must implement a ping-pong interval / heartbeat to keep the connection open. This involves a simple `{ type: "ping" }` every ~5s and **check that a `{ pong: {} } ` is received**.

For the "standard experience" where the agent continues off conversations, you'll want to set the `replay` query string param to `true` and record "conversation ids", which are then passed as the other query string parameter.

A list of past conversations can be fetch from [/ml/conversations](/docs/developer-tools/api/ml/list-conversations?lang=curl).

The general use-case is to fire off `{ type: "user", content: "my prompt goes here" }` messages and interpret the various message types that return.

Notable behavior: **ONLY KCL IS RETURNED.** It's a common misunderstanding that Zookeeper returns models in formats such as STEP and STL directly. This is incorrect. All outputs are in KCL, which can then be fed into the [Engine API](/docs/developer-tools/engine-api) (specifically the `exec_kcl_project` command) or the [Zoo CLI](/docs/developer-tools/cli/manual) (`zoo kcl snapshot ...`).

In the future we may add a more direct method, but you can always rely on those.

## Section

[ML](/docs/developer-tools/api/ml)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| replay | query | boolean | no | If `true`, emit MsgPack Replay for the specified conversation and continue. |
| conversation_id | query | string | no | Conversation to replay (UUID). Required when `replay` is `true`. |
| replay_attachment_mode | query | MlCopilotReplayAttachmentMode | no | Controls whether replayed attachment payloads are sent in full or replaced with metadata that can be used with `FetchAttachments`. |
| pr | query | integer | no | Optional Pull Request number to route traffic. |

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
