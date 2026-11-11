<p align="center">
  <img src="_assets/icon.png" width="128" alt="TaoDock Media for Dify">
</p>

<h1 align="center">TaoDock AI Image & Video Tools for Dify</h1>

<p align="center">
  Generate images and videos in Dify workflows and agents through one TaoDock API key.
</p>

<p align="center">
  <a href="https://github.com/taodock-api/taodock-dify-tools/actions/workflows/validate.yml"><img src="https://github.com/taodock-api/taodock-dify-tools/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <img src="https://img.shields.io/badge/Dify-%3E%3D%201.5.1-1C64F2" alt="Dify 1.5.1+">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB" alt="Python 3.12">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
</p>

[Chinese README](readme/README_zh_Hans.md)

## Why use this plugin?

- **Five workflow and agent tools** for model discovery, image generation, video generation, task polling, and result download.
- **Key-aware model discovery** returns only models authorized for the configured TaoDock API key.
- **Native Dify outputs**: generated images and completed videos are returned as file messages; unfinished video jobs return structured task state.
- **Asynchronous video support** lets a workflow wait for up to 540 seconds or resume a task later by ID.
- **Bounded network access**: the plugin calls only `https://taodock.com`; it does not accept arbitrary request URLs.
- **No plugin analytics or telemetry**.

## Install

### Dify Marketplace

After the plugin is approved, install **TaoDock AI Image & Video** from the Dify Marketplace.

### Install a local package

1. Download or build `taodock-dify-tools.difypkg`.
2. In Dify, open **Plugins → Install Plugin → Local Package**.
3. Upload the package and confirm the requested network permission.
4. Add the **TaoDock Media** provider and save a TaoDock API key.

The plugin requires Dify 1.5.1 or later.

## Quick start

1. [Create a TaoDock account](https://taodock.com/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations).
2. Review the [model catalog](https://taodock.com/models) and [wallet](https://taodock.com/wallet).
3. Create a key at [API Keys](https://taodock.com/keys) and authorize the models needed by your workflow.
4. Save that key in the TaoDock Media provider in Dify.
5. Run **List Models** with `kind=image` or `kind=video` and copy an exact model ID into a generation tool.

Credential validation reads the models authorized for the key. It does not create media or consume generation quota.

## Tools

| Tool | Main input | Output |
| --- | --- | --- |
| **List Models** | Optional `kind`: media, image, video, or text | JSON list of models authorized for the key |
| **Generate Image** | Model ID, prompt, optional JSON settings and edit mode | One or more Dify image file messages |
| **Generate Video** | Model ID, JSON request, wait time from 0 to 540 seconds | Video file when complete, otherwise structured task state |
| **Get Video Status** | Existing video task ID | Status, progress, model, and failure details when available |
| **Download Video** | Completed video task ID | Dify video file, or current task state if unfinished |

Use exact model IDs returned by **List Models**. Supported model-specific fields are documented in the [TaoDock model guide](https://docs.taodock.com/en/guide/models.html).

## Workflow examples

### Generate an image

```text
User input
  → TaoDock / List Models (kind=image)
  → TaoDock / Generate Image
      model: <exact model ID>
      prompt: "A paper-cut landscape at sunrise"
      settings: {"size":"1024x1024"}
  → Store, display, or pass the Dify file to another node
```

The dedicated `model` and `prompt` fields take precedence. Values with those names inside `settings` are ignored.

### Generate and resume a video

```text
Workflow A
  → Generate Video
      model: <exact model ID>
      request: {"prompt":"Clouds moving above a mountain lake"}
      wait_seconds: 0
  → Save task_id

Workflow B
  → Get Video Status (task_id)
  → If completed: Download Video (task_id)
```

Use a short or zero wait time for long-running jobs. This avoids holding a Dify workflow execution open while the upstream model renders the video.

## Data flow and permissions

```text
Dify workflow or agent
        │ API key + tool fields
        ▼
TaoDock Media plugin
        │ HTTPS only; fixed host
        ▼
https://taodock.com/v1
        │
        ├── authorized model metadata
        ├── generated image bytes
        ├── video task state
        └── completed video bytes
```

The manifest requests only Dify tool permission and declares `taodock.com` as the outbound domain. The plugin does not execute user code, shell commands, SQL, browser automation, or arbitrary URL requests.

See [PRIVACY.md](PRIVACY.md) for the complete disclosure. Dify may retain workflow inputs, outputs, files, and logs according to the deployment administrator's configuration. TaoDock processes API traffic under the [TaoDock Privacy Policy](https://taodock.com/privacy-policy).

## Compatibility

| Component | Requirement |
| --- | --- |
| Dify | 1.5.1 or later |
| Plugin runtime | Python 3.12 |
| Architectures | amd64, arm64 |
| Dify Plugin SDK | 0.10.2 |

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Credential validation fails | Confirm the key is active at [API Keys](https://taodock.com/keys) and has permission to read authorized models. |
| Model not found | Use the exact ID from **List Models** and confirm that the key is authorized for it. |
| Insufficient quota | Check the [wallet](https://taodock.com/wallet) and key-level limits. |
| Video returns task JSON | The task is still running. Save `task_id`, then use **Get Video Status** and **Download Video**. |
| Settings parsing fails | Pass a JSON object, not prose or an array. |

Requests use TaoDock quota. Review activity in [usage logs](https://taodock.com/usage-logs/common).

## Development

```bash
uv sync --frozen
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q main.py provider taodock_plugin tools
```

To build a Marketplace package with the official Dify Plugin CLI:

```bash
dify-plugin plugin package .
```

Before submitting, validate the resulting `.difypkg`, confirm it contains no credentials or development caches, and submit only that one package in the Marketplace pull request.

## Links

- [TaoDock](https://taodock.com/)
- [Documentation](https://docs.taodock.com/)
- [Model catalog](https://taodock.com/models)
- [Issues and support](https://github.com/taodock-api/taodock-dify-tools/issues)
- [Privacy disclosure](PRIVACY.md)

## Other TaoDock integrations

| Ecosystem | Repository |
| --- | --- |
| WordPress AI Client | [taodock-wordpress](https://github.com/taodock-api/taodock-wordpress) |
| n8n | [taodock-n8n-nodes](https://github.com/taodock-api/taodock-n8n-nodes) |
| Vercel AI SDK | [taodock-ai-sdk](https://github.com/taodock-api/taodock-ai-sdk) |
| AstrBot | [taodock-astrbot-plugin](https://github.com/taodock-api/taodock-astrbot-plugin) |
| Model Context Protocol | [taodock-mcp](https://github.com/taodock-api/taodock-mcp) |

## License

[MIT](LICENSE) © TaoDock
