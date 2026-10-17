Source URL: https://zoo.dev/docs/developer-tools/api/modeling/opens-a-websocket-to-a-zoo-kittycad-engine-instance
Title: Opens a WebSocket to a Zoo KittyCAD engine instance.

# Opens a WebSocket to a Zoo KittyCAD engine instance.

`GET /ws/modeling/commands`

**Note**: Currently it's recommended to set `webrtc=true` in the WebSocket query string, otherwise some features, such as opacity setting, will cause the engine to fail.

Due to the long-lived nature of the instances, it's possible the resources on have been used and not freed entirely, or the instance is in a bad state. Thus it's good practice to expect to have to potentially reconnect at any moment -even almost immediately after the first connection!

Authorization happens via a pseudo HTTP header over the WebSocket: `{ type: "headers", headers: { "Authorization": "Bearer xxxxxxxxx" }}`

The very next thing recommended is to setup a ping-pong interval. The current timeout is 10s and has no documented guarantee, so use a conservative number below that. 5s should be sufficient. A ping-pong interval is sending `{ type: 'ping" }` when `{ request_id, success, resp: { type: "pong", data: {} } }` message is received.

You're ready to start sending modeling commands!

If you want to understand how to connect to the WebRTC video stream, https://github.com/KittyCAD/kittycad.ts/blob/main/src/webrtc.ts is a nice example to learn from.

## Section

[Modeling](/docs/developer-tools/api/modeling)

## Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| video_res_width | query | integer | no | Width of the video feed. Must be a multiple of 4. |
| video_res_height | query | integer | no | Height of the video feed. Must be a multiple of 4. |
| fps | query | integer | no | Frames per second of the video feed. |
| unlocked_framerate | query | boolean | no | If true, engine will render video frames as fast as it can. |
| post_effect | query | PostEffectType | no | Engine Post effects (such as SSAO) |
| webrtc | query | boolean | no | If true, will start a webrtc connection. |
| geometry_only | query | boolean | no | If true, the engine will be ran without any graphical rendering capability. This may reduce the ability of some endpoints such as snapshot. |
| pool | query | string | no | An optional identifier for a pool of engine instances. The 'default' pool is used when none is specified. |
| show_grid | query | boolean | no | If true, will show the grid at the start of the session. |
| replay | query | string | no | If given, when the session ends, the modeling commands sent during the session will be written out to this filename. For debugging. |
| api_call_id | query | string | no | API Call ID for distributed tracing |
| order_independent_transparency | query | boolean | no | Enables nicer visuals for transparent surfaces. This slows down rendering, so it's off by default. |
| kcl_version | query | KclVersion | no | Which KCL+Engine version should the engine use? Clients use this to opt into updated algorithms and behaviours. |
| pr | query | integer | no | Optional Pull Request number to route traffic. |

## Request Body

Websocket requests

| Content-Type | Schema |
| --- | --- |
| application/json | WebSocketRequest |

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
