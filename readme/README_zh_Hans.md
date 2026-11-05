# TaoDock Dify 媒体工具

TaoDock Media 为 Dify 工作流与 Agent 提供图像和视频生成工具。

## 配置

1. [注册 TaoDock](https://taodock.com/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations)；
2. 查看[钱包](https://taodock.com/wallet)与[模型目录](https://taodock.com/models)；
3. 在 [API 密钥](https://taodock.com/keys)页面创建密钥，并开放工作流所需模型；
4. 在 Dify 中安装 `.difypkg` 文件，然后在 TaoDock Media 提供商中保存密钥。

凭据校验只读取密钥已获授权的模型，不会创建媒体内容。

## 工具

| 工具 | 结果 |
| --- | --- |
| 列出模型 | 返回当前密钥可用的图像、视频或文本模型。 |
| 生成图像 | 生成图像并以 Dify 文件消息返回。 |
| 生成视频 | 创建视频任务，可选择等待，并返回视频文件或任务状态。 |
| 查询视频状态 | 返回已有视频任务的当前状态。 |
| 下载视频 | 返回已完成视频任务的文件。 |

请使用“列出模型”返回的准确模型 ID。模型专属设置使用 JSON 对象；专用字段中的 `model` 和图像 `prompt` 不会被 JSON 设置覆盖。

支持字段请参考 [TaoDock 模型指南](https://docs.taodock.com/guide/models.html)。调用会消耗 TaoDock 额度，可在[使用日志](https://taodock.com/usage-logs/common)中查看记录。

## 项目

- 仓库：https://github.com/taodock-api/taodock-dify-tools
- 支持：https://github.com/taodock-api/taodock-dify-tools/issues
- 隐私说明：[PRIVACY.md](../PRIVACY.md)
- 许可证：MIT © TaoDock
