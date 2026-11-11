# Privacy Disclosure

## Data sent to TaoDock

The TaoDock AI Image & Video plugin sends the configured API key and the fields required by the selected tool to `https://taodock.com/v1`. Depending on the tool, these fields can include model IDs, prompts, model-specific generation settings, video task IDs, and requested wait times. The plugin also reads the models authorized for the key and the public TaoDock model catalog.

The data is used only to authenticate the request, discover models, generate media, inspect video tasks, and download completed results. TaoDock processes this traffic under the [TaoDock Privacy Policy](https://taodock.com/privacy-policy).

## Data stored by the plugin

The plugin does not add analytics or telemetry and does not intentionally persist API keys, prompts, generated media, task IDs, or API responses. It does not send data to advertising or analytics services.

Dify manages provider credentials and may retain workflow inputs, outputs, files, execution history, and logs according to the Dify deployment administrator's configuration. Review the privacy and retention settings of your Dify deployment separately.

## Network and security boundary

The plugin permits outbound HTTPS access only to `taodock.com`. It does not accept arbitrary request URLs and does not execute user-controlled code, shell commands, SQL, browser automation, or filesystem operations.

Only submit content that you are authorized to process. Do not include sensitive personal data unless your use case, Dify deployment, and TaoDock account are configured to handle it lawfully.
