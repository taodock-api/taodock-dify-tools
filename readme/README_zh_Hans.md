# TaoDock AI 图片与视频工具（Dify）

TaoDock Media 为 Dify 工作流与 Agent 提供模型发现、图片生成、视频生成、任务查询和视频下载工具。只需配置一个 TaoDock API 密钥。

[English README](../README.md)

## 核心能力

- 根据 API 密钥权限动态返回可用模型，不把模型列表写死在插件中；
- 生成图片并直接返回 Dify 文件消息；
- 创建异步视频任务，可等待最多 540 秒，也可保存任务 ID 后在其他工作流中继续查询；
- 视频完成后直接返回 Dify 视频文件；
- 仅访问固定域名 `https://taodock.com`，不接受任意请求 URL；
- 不添加插件分析或遥测。

## 安装

### Dify Marketplace

插件通过审核后，可在 Dify Marketplace 搜索 **TaoDock AI Image & Video** 安装。

### 本地安装包

1. 下载或构建 `taodock-dify-tools.difypkg`；
2. 在 Dify 中打开 **插件 → 安装插件 → 本地安装包**；
3. 上传安装包并确认网络权限；
4. 添加 **TaoDock Media** Provider，保存 TaoDock API 密钥。

插件要求 Dify 1.5.1 或更高版本。

## 快速开始

1. [注册 TaoDock](https://taodock.com/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations)；
2. 查看[模型目录](https://taodock.com/models)与[钱包](https://taodock.com/wallet)；
3. 在 [API 密钥](https://taodock.com/keys)页面创建密钥，并授权工作流需要的模型；
4. 在 Dify 的 TaoDock Media Provider 中保存密钥；
5. 先运行 **列出模型**，再把返回的准确模型 ID 填入生成工具。

凭据校验只读取当前密钥已获授权的模型，不会生成内容，也不会消耗生成额度。

## 工具列表

| 工具 | 主要输入 | 输出 |
| --- | --- | --- |
| **列出模型** | 可选类型：媒体、图片、视频或文本 | 当前密钥可用的模型列表 |
| **生成图片** | 模型 ID、提示词、可选 JSON 设置和编辑模式 | 一个或多个 Dify 图片文件 |
| **生成视频** | 模型 ID、JSON 请求、0–540 秒等待时间 | 完成时返回视频文件，否则返回任务状态 |
| **查询视频状态** | 视频任务 ID | 状态、进度、模型和错误详情 |
| **下载视频** | 已完成的视频任务 ID | 视频文件；未完成时返回当前任务状态 |

模型专属字段请参考 [TaoDock 模型指南](https://docs.taodock.com/guide/models.html)。

## 工作流示例

### 生成图片

```text
用户输入
  → TaoDock / 列出模型（类型=图片）
  → TaoDock / 生成图片
      model: <准确模型 ID>
      prompt: "日出时的剪纸风景"
      settings: {"size":"1024x1024"}
  → 保存、展示或传递 Dify 文件
```

专用的 `model` 和 `prompt` 字段优先；`settings` 中同名字段不会覆盖它们。

### 异步生成视频

```text
工作流 A
  → 生成视频
      model: <准确模型 ID>
      request: {"prompt":"山间湖泊上方流动的云层"}
      wait_seconds: 0
  → 保存 task_id

工作流 B
  → 查询视频状态（task_id）
  → 已完成时：下载视频（task_id）
```

长任务建议使用较短或为 0 的等待时间，避免 Dify 工作流一直占用执行状态。

## 隐私与安全

插件只向 `https://taodock.com` 发送 API 密钥和所选工具必需的字段，例如模型 ID、提示词、生成设置和视频任务 ID。插件不会执行用户代码、Shell 命令、SQL、浏览器自动化或任意 URL 请求。

完整说明见 [PRIVACY.md](../PRIVACY.md)。Dify 是否保留工作流输入、输出、文件和日志，取决于部署管理员的配置。TaoDock 按[隐私政策](https://taodock.com/privacy-policy)处理 API 流量。

## 故障排查

| 现象 | 检查项 |
| --- | --- |
| 凭据校验失败 | 确认密钥有效，并有权读取已授权模型。 |
| 模型不存在 | 使用“列出模型”返回的准确 ID，并检查密钥授权范围。 |
| 额度不足 | 检查钱包余额和密钥级限额。 |
| 视频返回任务 JSON | 视频仍在生成；保存 `task_id`，随后查询状态并下载。 |
| JSON 设置解析失败 | 必须传 JSON 对象，不能传自然语言或数组。 |

使用记录可在[使用日志](https://taodock.com/usage-logs/common)中查看。

## 项目链接

- 仓库：https://github.com/taodock-api/taodock-dify-tools
- 支持：https://github.com/taodock-api/taodock-dify-tools/issues
- 文档：https://docs.taodock.com/
- 许可证：[MIT](../LICENSE)
