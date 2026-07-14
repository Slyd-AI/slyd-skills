# SLYD PPT Skill

[![GitHub stars](https://img.shields.io/github/stars/Slyd-AI/slyd-skills?style=flat-square)](https://github.com/Slyd-AI/slyd-skills/stargazers)
[![License](https://img.shields.io/github/license/Slyd-AI/slyd-skills?style=flat-square)](./LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent-Skill-111111?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex](https://img.shields.io/badge/Codex-Verified-222222?style=flat-square)

[English](./README_EN.md) | 中文

通过 [SLYD](https://slyd.top) Agent API，把 PDF、Word、Markdown、文本、图片和已有 PowerPoint 文件制作成经过校验的 PPTX 演示文稿。

这个仓库提供的是可移植 Agent Skill，不是只能粘贴到某个产品里的单段提示词。只要 Agent 环境能够加载 `SKILL.md` 目录、运行本地 Python、读取环境变量并访问 SLYD API，就可以使用。Codex 安装已经验证；其他平台应使用各自的 Skill 导入方式。

> 源文件会上传到 SLYD 云端处理，生成任务可能消耗 SLYD 账号积分。Skill 会在提交新的付费任务前说明操作内容并请求确认。

## 30 秒开始

### 1. 安装或导入 Skill

Skill 目录：

```text
https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-skill
```

Codex 用户发送：

```text
使用 $skill-installer 从 https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-skill 安装 slyd-ppt-skill。
```

其他支持 Skill 的 Agent，请使用平台自己的 Skill 管理器导入上面的目录地址；也可以克隆仓库，再让 Agent 加载 `skills/slyd-ppt-skill`：

```bash
git clone https://github.com/Slyd-AI/slyd-skills.git
```

### 2. 配置凭据

在 SLYD 个人中心创建 API Key，然后在 Agent 聊天之外设置：

```bash
export SLYD_API_BASE='https://slyd.top'
export SLYD_API_KEY='slyd_sk_xxx'
```

从同一个终端启动 Agent。不要把 API Key 粘贴到聊天中，也不要写入 Skill 目录。

### 3. 制作第一份 PPT

在下一轮对话中附上或引用本地文件，然后输入：

```text
使用 $slyd-ppt-skill 把 /absolute/path/report.pdf 制作成 12 页中文管理层汇报，突出结论、证据和行动项。
```

Agent 会选择工作模式，汇总源文件、页数、积分规则和所需账号能力，并在提交前请求确认。

## 能做什么

| 工作模式 | 适用任务 | 主要输入 | 账号说明 |
|---|---|---|---|
| 智能重构 | 重新组织叙事和页面结构，制作全新 PPT | PDF、Word、Markdown、文本、混合文档 | 模板上传需要 Pro；PPTX 主材料受服务端灰度开关控制 |
| 图文还原 | 把视觉材料还原成可编辑幻灯片 | 视觉型 PDF、截图、图片、文档 | 图片、模板和多文档上传需要 Pro |
| PPTX 美化 | 重新设计已有演示文稿 | 一个 PPTX，可附加文档、图片、模板或风格参考 | 需要有效 Pro 会员 |

所有模式默认使用异步 Agent API。内置客户端支持健康检查、幂等提交、状态轮询、协作取消、PPTX 下载和文件包校验。

## 平台支持

| 环境 | 状态 | 要求 |
|---|---|---|
| Codex | 已验证 | 使用 `$skill-installer` 安装，下一轮对话可用 |
| 其他支持 Skill 的 Agent | 兼容 | 能加载 `SKILL.md` 目录并执行本地 Python 命令 |
| 没有 Skill 管理器的本地 Coding Agent | 手动接入 | 克隆仓库，按平台说明加载 `skills/slyd-ppt-skill` |
| 普通聊天机器人 | 建议改用 API 文档 | 没有文件系统和命令执行能力时，内置客户端无法可靠运行 |

这里的平台兼容性指 Skill 工作流。PPT 生成实际运行在 SLYD 云端，配置域名必须开启对应 API 功能开关。

## 示例请求

```text
使用 $slyd-ppt-skill，把 ./quarterly-report.docx 制作成 10 页英文投资人季度更新。
```

```text
使用 $slyd-ppt-skill，把这些产品截图还原成 8 页中文可编辑 PPT。
```

```text
使用 $slyd-ppt-skill 重新设计 ./sales-review.pptx，并根据 ./notes.pdf 补充 3 页总结。
```

```text
查询 SLYD 任务 agj_xxx 的状态，不要提交替代任务。
```

```text
取消 SLYD 任务 agj_xxx，并说明是立即取消还是正在协作退出。
```

## 用户保护流程

1. 付费请求前检查 `/api/health`。
2. 选择字段或解释错误前读取完整 API reference。
3. 校验文件路径、模式对应字段和页数限制。
4. 说明所选模式、输入材料、页数和积分规则。
5. 除非用户已经批准完全相同的操作，否则新付费任务必须再次确认。
6. 提交结果不明确时，使用同一个 `Idempotency-Key` 重试。
7. 已受理任务只查询和轮询，不重复提交。
8. 及时下载结果，并验证 PPTX ZIP 文件结构。

## 积分和账号能力

当前默认规则记录在 [`references/api.md`](./skills/slyd-ppt-skill/references/api.md)：

- 普通用户生成：每个目标页 5 积分。
- 有效 Pro 用户生成：每个目标页 4 积分。
- Pro PPT 美化：每个原始页和补充页 4 积分。

部署价格可能变化。Skill 会从 `/api/health` 读取当前公开价格配置，并在提交前说明适用规则。Agent API 目前不提供需要鉴权的余额或报价查询接口。

## 安全与数据处理

- `SLYD_API_KEY` 只放在环境变量中，不写入聊天、源文件、日志或 Git。
- 源文档会上传到所配置的 SLYD API 进行处理。
- `download_url` 是临时 bearer link，不要公开传播。
- 付费转换失败时，任务状态可能包含积分退款信息。
- 失败或提交结果不明确的付费任务，应先检查原任务；需要重新执行时再次获得确认。

## 客户端命令

通常由 Agent 代替用户执行；排查问题时也可以手动运行：

```bash
python skills/slyd-ppt-skill/scripts/slyd_client.py health
python skills/slyd-ppt-skill/scripts/slyd_client.py submit --help
python skills/slyd-ppt-skill/scripts/slyd_client.py status agj_xxx
python skills/slyd-ppt-skill/scripts/slyd_client.py cancel agj_xxx
python skills/slyd-ppt-skill/scripts/slyd_client.py wait agj_xxx --output /absolute/path/result.pptx
```

## 常见问题

### Agent 没有识别到 Skill

确认导入目录根部存在 `SKILL.md`。Codex 新安装的 Skill 会在下一轮对话中可用；其他平台可能需要重新加载。

### 健康检查提示 API 未启用

检查 `SLYD_API_BASE`。`feature_flags.user_agent_api` 和 `feature_flags.user_agent_api_queue` 必须同时开启。不要为了绕过关闭的功能开关，直接把付费请求提交到其他环境。

### API 返回 `403`

当前输入或工作模式需要 Pro。常见情况包括 PPTX 美化、模板上传、图片上传和多文档上传。

### API 返回 `409`

幂等键已经用于不同请求内容，或任务状态发生变化。创建替代任务前，先查询已有任务。

### API 返回 `429`

遵循 `Retry-After`。已受理任务继续轮询，不要重新提交。

## 仓库结构

```text
slyd-skills/
├── README.md
├── README_EN.md
└── skills/
    └── slyd-ppt-skill/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   └── api.md
        └── scripts/
            └── slyd_client.py
```

`agents/openai.yaml` 是 OpenAI/Codex 界面的可选 UI 元数据，平台无关的核心工作流仍在 `SKILL.md` 中。

## 文档

- [English README](./README_EN.md)
- [Skill 工作流](./skills/slyd-ppt-skill/SKILL.md)
- [API reference](./skills/slyd-ppt-skill/references/api.md)
- [网页 API 文档](https://slyd.top/agent-api-docs)

## 开发验证

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/slyd-ppt-skill
python -m py_compile skills/slyd-ppt-skill/scripts/slyd_client.py
python skills/slyd-ppt-skill/scripts/slyd_client.py --help
```

## License

[MIT](./LICENSE)
