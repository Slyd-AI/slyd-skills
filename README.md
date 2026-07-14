# SLYD Skills

Official Codex skills for creating PowerPoint presentations with [SLYD](https://slyd.top).

## 安装到 Codex

在 Codex 中输入：

```text
使用 $skill-installer 从 https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-maker 安装 SLYD PPT Maker Skill。
```

安装完成后，在下一轮对话中调用：

```text
$slyd-ppt-maker 请把 report.pdf 制作成 12 页中文汇报 PPT。
```

Codex 支持显式使用 `$slyd-ppt-maker`，也可以在请求符合 Skill 描述时自动调用。

## 配置

登录 SLYD，在个人中心创建 API Key。启动 Codex 前设置：

```bash
export SLYD_API_BASE='https://slyd.top'
export SLYD_API_KEY='slyd_sk_xxx'
codex
```

不要把 API Key 写进聊天、仓库或 Skill 文件。生成和美化任务会消耗 SLYD 账号积分，Skill 会在提交前说明任务参数并确认。

## 功能

- 从 PDF、Word、Markdown、文本和混合资料智能重构 PPT。
- 从图片、截图和视觉型文档还原可编辑 PPT。
- 美化和重新设计已有 PPTX。
- 使用异步队列安全提交、轮询和取消任务。
- 下载并验证生成的 PPTX 文件。

详细能力和限制见 [Skill API reference](skills/slyd-ppt-maker/references/api.md)。网页 API 文档位于 [slyd.top/agent-api-docs](https://slyd.top/agent-api-docs)。

## Repository Layout

```text
skills/slyd-ppt-maker/
├── SKILL.md
├── agents/openai.yaml
├── references/api.md
└── scripts/slyd_client.py
```

## Development

Validate the skill metadata and client before publishing:

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/slyd-ppt-maker
python -m py_compile skills/slyd-ppt-maker/scripts/slyd_client.py
python skills/slyd-ppt-maker/scripts/slyd_client.py --help
```

## License

MIT
