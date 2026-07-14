# SLYD Skills

Official Agent Skills for creating PowerPoint presentations with [SLYD](https://slyd.top).

## 安装或导入

Skill 目录：

```text
https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-maker
```

任何支持 `SKILL.md` 目录结构的 Agent 都可以从该地址安装或导入。不同平台的 Skill 入口和命令可能不同；运行环境需要能够执行本地 Python 脚本、读取环境变量并访问 SLYD API。

### Codex

在 Codex 中输入：

```text
使用 $skill-installer 从 https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-maker 安装 SLYD PPT Maker Skill。
```

安装完成后，在下一轮对话中调用：

```text
$slyd-ppt-maker 请把 report.pdf 制作成 12 页中文汇报 PPT。
```

Codex 支持显式使用 `$slyd-ppt-maker`，也可以在请求符合 Skill 描述时自动调用。其他 Agent 请使用其平台提供的 GitHub Skill 导入方式，或克隆本仓库后加载 `skills/slyd-ppt-maker` 目录。

## 配置

登录 SLYD，在个人中心创建 API Key。启动 Agent 前设置：

```bash
export SLYD_API_BASE='https://slyd.top'
export SLYD_API_KEY='slyd_sk_xxx'
```

在同一终端启动所用 Agent；Codex CLI 用户随后运行 `codex`。不要把 API Key 写进聊天、仓库或 Skill 文件。生成和美化任务会消耗 SLYD 账号积分，Skill 会在提交前说明任务参数并确认。

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
├── agents/openai.yaml        # 可选 OpenAI/Codex UI 元数据
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
