Source URL: https://zoo.dev/docs/developer-tools/api/ml
Title: ML

# ML

Machine learning to generate CAD models and other things.

## Endpoints

| Method | Path | Summary |
| --- | --- | --- |
| GET | [/ml/conversations](/docs/developer-tools/api/ml/list-conversations) | List conversations |
| POST | [/ml/custom/models](/docs/developer-tools/api/ml/create-a-custom-ml-model-that-is-backed-by-one-or-more-org-datasets) | Create a custom ML model that is backed by one or more org datasets. |
| GET | [/ml/custom/models/{id}](/docs/developer-tools/api/ml/retrieve-the-details-of-a-single-custom-ml-model-so-long-as-it-belongs-to-the-caller’s-organization) | Retrieve the details of a single custom ML model so long as it belongs to the caller’s organization. |
| PUT | [/ml/custom/models/{id}](/docs/developer-tools/api/ml/update-mutable-metadata-(name,-system-prompt)-for-a-custom-ml-model-owned-by-the-caller's-organization) | Update mutable metadata (name, system prompt) for a custom ML model owned by the caller's organization. |
| GET | [/ml/custom/models/{id}/datasets](/docs/developer-tools/api/ml/list-the-org-datasets-that-are-currently-attached-to-a-custom-ml-model-owned-by-the-caller’s-organization) | List the org datasets that are currently attached to a custom ML model owned by the caller’s organization. |
| GET | [/user/text-to-cad](/docs/developer-tools/api/ml/list-text-to-cad-parts-you've-generated) | List text-to-CAD parts you've generated. |
| GET | [/user/text-to-cad/{id}](/docs/developer-tools/api/ml/get-a-text-to-cad-response) | Get a text-to-CAD response. |
| POST | [/user/text-to-cad/{id}](/docs/developer-tools/api/ml/give-feedback-to-a-specific-ml-response) | Give feedback to a specific ML response. |
| GET | [/ws/ml/copilot](/docs/developer-tools/api/ml/open-a-websocket-to-a-zookeeper-agent-instance) | Open a websocket to a Zookeeper agent instance. |
| GET | [/ws/ml/reasoning/{id}](/docs/developer-tools/api/ml/open-a-websocket-to-prompt-the-ml-copilot) | Open a websocket to prompt the ML copilot. |
