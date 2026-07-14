---
name: slyd-ppt-maker
description: Create, reconstruct, or beautify PowerPoint presentations through the SLYD Agent API from PDF, Word, Markdown, text, images, or existing PPTX files. Use when a user asks Codex to make a PPT with SLYD, visually restore source material into editable slides, redesign an existing deck, submit or monitor a SLYD job, or download a generated PPTX.
---

# SLYD PPT Maker

Use the bundled client to run the SLYD workflow reliably. Prefer asynchronous jobs so retries do not create duplicate charged conversions. Resolve `<skill-dir>` to the absolute directory containing this `SKILL.md` before running any command below; do not assume the user's project is the Skill directory.

## Prerequisites

1. Read `SLYD_API_KEY` from the environment. Never ask the user to paste it into chat or write it to a file.
2. Read `SLYD_API_BASE` from the environment, defaulting to `https://slyd.top` only when it is unset.
3. Run `python <skill-dir>/scripts/slyd_client.py health` before a paid request. Stop if `user_agent_api` or `user_agent_api_queue` is disabled.
4. Read [references/api.md](references/api.md) before selecting fields, formats, limits, or interpreting an error.

## Choose One Mode

- `smart_refactor`: Create a new presentation from reports, text, Markdown, Word, PDF, or mixed document sources.
- `deep_restore`: Reconstruct screenshots, images, visually structured PDFs, and chart-heavy material as editable slides.
- `pptx_beautify`: Redesign an existing PPTX. This endpoint requires an active Pro membership.

Do not send the same source to multiple modes unless the user explicitly requests separate alternatives.

## Confirm the Charged Action

Before submitting:

1. Validate that every path exists and its field is supported by the chosen mode.
2. Determine `target_pages` for `smart_refactor` and `deep_restore` in the allowed 4-30 range.
3. Summarize the selected mode, source files, target or source slide count, supplemental pages, and the expected points rule.
4. Ask for confirmation unless the user already explicitly approved that exact charged operation in the current request.

Never create a second job after an ambiguous timeout without checking the first job or reusing its idempotency key.

## Submit

Generate one UUID per logical request and keep it for every retry:

```bash
IDEMPOTENCY_KEY="$(python -c 'import uuid; print(uuid.uuid4())')"
python <skill-dir>/scripts/slyd_client.py submit \
  --mode smart_refactor \
  --idempotency-key "$IDEMPOTENCY_KEY" \
  --file file=/absolute/path/report.pdf \
  --field target_pages=12 \
  --field output_language=zh-CN \
  --field content_density=medium \
  --field 'user_requirements=面向管理层，突出结论、数据和行动建议'
```

Capture the returned `job_id`. If submission returns a network error, retry with the same `IDEMPOTENCY_KEY`. A `409 idempotency_key_conflict` means the key was reused with different content; stop and report it.

## Wait and Deliver

Use the returned job instead of submitting again:

```bash
python <skill-dir>/scripts/slyd_client.py wait agj_xxx --output /absolute/path/slyd-output.pptx
```

The client honors `Retry-After`, waits at least 30 seconds between status checks, downloads the completed file, and validates the PPTX package. On success, return the saved PPTX to the user when the surface supports file attachments, plus `download_url` and `download_expires_at` when useful.

Treat `failed`, `expired`, and `canceled` as terminal. Report `last_error_message` without exposing credentials or internal diagnostics. Do not retry a failed charged conversion without fresh user confirmation.

## Cancel

When the user asks to stop a queued or running job, request cooperative cancellation:

```bash
python <skill-dir>/scripts/slyd_client.py cancel agj_xxx
```

If the response remains nonterminal, explain that cancellation was requested and the current processing stage is exiting safely.

## Safety Rules

- Never print, log, commit, or return `SLYD_API_KEY`.
- Treat download URLs as temporary bearer links. Avoid placing them in public logs or repositories.
- Do not claim success until the downloaded file passes PPTX validation.
- Respect `429` and `Retry-After`; do not increase polling frequency.
- Use absolute input and output paths so Codex does not write to an unexpected directory.
- If network access needs approval, request it for the configured SLYD host only.
