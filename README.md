# SLYD PPT Maker Skill

[![GitHub stars](https://img.shields.io/github/stars/Slyd-AI/slyd-skills?style=flat-square)](https://github.com/Slyd-AI/slyd-skills/stargazers)
[![License](https://img.shields.io/github/license/Slyd-AI/slyd-skills?style=flat-square)](./LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent-Skill-111111?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex](https://img.shields.io/badge/Codex-Verified-222222?style=flat-square)

English | [中文](./README_CN.md)

Turn PDF, Word, Markdown, text, images, and existing PowerPoint files into polished PPTX presentations through the [SLYD](https://slyd.top) Agent API.

This repository contains a portable Agent Skill, not a model prompt pasted into one specific product. Any Agent environment that can load a `SKILL.md` directory, run local Python, read environment variables, and access the SLYD API can use it. Codex installation is verified; other platforms should use their own Skill import mechanism.

> Source files are uploaded to SLYD for cloud processing. Jobs may consume SLYD account points. The Skill explains the operation and asks for confirmation before submitting a new paid task.

## 30-second start

### 1. Install or import the Skill

Skill directory:

```text
https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-maker
```

For Codex, send:

```text
Use $skill-installer to install SLYD PPT Maker from https://github.com/Slyd-AI/slyd-skills/tree/main/skills/slyd-ppt-maker.
```

For another Skill-capable Agent, import the directory URL above with its Skill manager. You can also clone this repository and point the Agent at `skills/slyd-ppt-maker`:

```bash
git clone https://github.com/Slyd-AI/slyd-skills.git
```

### 2. Configure credentials

Create an API Key in your SLYD profile, then set it outside the Agent chat:

```bash
export SLYD_API_BASE='https://slyd.top'
export SLYD_API_KEY='slyd_sk_xxx'
```

Start the Agent from the same terminal. Never paste the API Key into chat or store it in the Skill directory.

### 3. Make your first presentation

On the next Agent turn, attach or reference a local source file and ask:

```text
Use $slyd-ppt-maker to turn /absolute/path/report.pdf into a 12-slide Chinese management presentation. Focus on conclusions, evidence, and action items.
```

The Agent will select a workflow, summarize the source files, page count, account rule, and required capability, then ask for confirmation before submission.

## What it does

| Workflow | Use it for | Main inputs | Account notes |
|---|---|---|---|
| Smart refactor | Build a new narrative and slide structure | PDF, Word, Markdown, text, mixed documents | Template upload requires Pro; PPTX as a primary source is deployment-gated |
| Deep restore | Reconstruct visual material into editable slides | Visual PDFs, screenshots, images, documents | Images, templates, and multiple documents require Pro |
| PPTX beautify | Redesign an existing deck | One PPTX, plus optional documents, images, template, or style references | Requires active Pro membership |

All workflows use the asynchronous Agent API by default. The bundled client supports health checks, idempotent submission, status polling, cooperative cancellation, PPTX download, and package validation.

## Platform support

| Environment | Status | Requirements |
|---|---|---|
| Codex | Verified | Install with `$skill-installer`; available on the next turn |
| Other Skill-capable Agents | Compatible | Must load a `SKILL.md` directory and run local Python commands |
| Local coding Agents without a Skill manager | Manual | Clone the repository and load `skills/slyd-ppt-maker` according to the platform documentation |
| Plain chatbots | Use the API guide instead | Without filesystem and command execution, the bundled client cannot run reliably |

Platform support refers to the Skill workflow. Presentation generation itself runs on SLYD's cloud service and requires the API feature flags to be enabled for the configured base URL.

## Example requests

```text
Use $slyd-ppt-maker to create a 10-slide investor update from ./quarterly-report.docx in English.
```

```text
Use $slyd-ppt-maker to visually restore these product screenshots as an editable 8-slide Chinese deck.
```

```text
Use $slyd-ppt-maker to redesign ./sales-review.pptx and add 3 summary slides from ./notes.pdf.
```

```text
Check the status of SLYD job agj_xxx. Do not submit a replacement job.
```

```text
Cancel SLYD job agj_xxx and report whether it was canceled immediately or is exiting cooperatively.
```

## How the workflow protects users

1. Checks `/api/health` before a paid request.
2. Reads the complete API reference before choosing fields or interpreting errors.
3. Validates file paths, mode-specific fields, and page limits.
4. Explains the selected mode, inputs, page count, and points rule.
5. Requires confirmation for a new paid operation unless the exact action was already approved.
6. Reuses one `Idempotency-Key` across ambiguous submission retries.
7. Polls the accepted job instead of submitting duplicates.
8. Downloads the result promptly and validates the PPTX ZIP structure.

## Points and account capabilities

Current default rules are documented in [`references/api.md`](./skills/slyd-ppt-maker/references/api.md):

- Standard generation: 5 points per target page.
- Active Pro generation: 4 points per target page.
- Pro beautify: 4 points per source slide and supplemental page.

Deployment pricing can change. The Skill reads the current public pricing configuration from `/api/health` and explains the applicable rule before submission. The Agent API does not currently expose an authenticated balance or quote endpoint.

## Security and data handling

- Keep `SLYD_API_KEY` in environment variables, never in chat, source files, logs, or Git.
- Source documents are uploaded to the configured SLYD API for processing.
- Treat `download_url` as a temporary bearer link and avoid publishing it.
- A failed charged conversion may report refunded points in the job status.
- Do not resubmit a failed or ambiguous charged task without checking the original job and getting fresh confirmation when needed.

## Commands

The Agent normally runs these commands for the user. They are also available for diagnostics:

```bash
python skills/slyd-ppt-maker/scripts/slyd_client.py health
python skills/slyd-ppt-maker/scripts/slyd_client.py submit --help
python skills/slyd-ppt-maker/scripts/slyd_client.py status agj_xxx
python skills/slyd-ppt-maker/scripts/slyd_client.py cancel agj_xxx
python skills/slyd-ppt-maker/scripts/slyd_client.py wait agj_xxx --output /absolute/path/result.pptx
```

## Troubleshooting

### The Skill is not detected

Confirm that the imported directory contains `SKILL.md` at its root. Codex makes a newly installed Skill available on the next turn; other platforms may require a reload.

### The health check says the API is disabled

Verify `SLYD_API_BASE`. Both `feature_flags.user_agent_api` and `feature_flags.user_agent_api_queue` must be enabled. Do not submit a paid request to another environment just to bypass a disabled feature flag.

### The API returns `403`

The selected input or workflow requires Pro membership. Common cases are PPTX beautify, template uploads, images, or multiple source documents.

### The API returns `409`

The idempotency key was reused with different request content, or the job state changed. Query the existing job before creating any replacement.

### The API returns `429`

Honor `Retry-After`. Continue polling an accepted job; do not resubmit it.

## Repository layout

```text
slyd-skills/
├── README.md
├── README_CN.md
└── skills/
    └── slyd-ppt-maker/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   └── api.md
        └── scripts/
            └── slyd_client.py
```

`agents/openai.yaml` is optional UI metadata for OpenAI/Codex surfaces. The core workflow remains in the platform-neutral `SKILL.md`.

## Documentation

- [Chinese README](./README_CN.md)
- [Skill workflow](./skills/slyd-ppt-maker/SKILL.md)
- [API reference](./skills/slyd-ppt-maker/references/api.md)
- [Web API documentation](https://slyd.top/agent-api-docs)

## Development

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/slyd-ppt-maker
python -m py_compile skills/slyd-ppt-maker/scripts/slyd_client.py
python skills/slyd-ppt-maker/scripts/slyd_client.py --help
```

## License

[MIT](./LICENSE)
