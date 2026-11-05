# TaoDock Media for Dify

TaoDock Media adds image and video generation tools to Dify workflows and agents.

## Setup

1. Register at [TaoDock](https://taodock.com/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations).
2. Review the [wallet](https://taodock.com/wallet) and [model catalog](https://taodock.com/models).
3. Create a key at [API Keys](https://taodock.com/keys) and allow the models required by your workflow.
4. Install the `.difypkg` file in Dify and save the key in the TaoDock Media provider.

Credential validation reads the models authorized for the key. It does not create media.

## Tools

| Tool | Result |
| --- | --- |
| List Models | Returns the image, video, or text models authorized for the key. |
| Generate Image | Generates an image and returns it as a Dify file message. |
| Generate Video | Starts a video task, optionally waits, and returns either the file or task state. |
| Get Video Status | Returns the current state of an existing video task. |
| Download Video | Returns the file for a completed video task. |

Use exact model IDs from **List Models**. Model-specific settings are JSON objects. The selected `model` and the image `prompt` are always set by the dedicated tool fields and cannot be replaced through JSON settings.

See the [TaoDock model guide](https://docs.taodock.com/en/guide/models.html) for supported fields. Requests use TaoDock quota; activity is available in [usage logs](https://taodock.com/usage-logs/common).

## Project

- Repository: https://github.com/taodock-api/taodock-dify-tools
- Support: https://github.com/taodock-api/taodock-dify-tools/issues
- Privacy: [PRIVACY.md](PRIVACY.md)
- License: MIT © TaoDock
