# SLYD Agent API Reference

Use this reference when choosing request fields, validating inputs, estimating points, or handling API responses. Server responses and `/api/health` are authoritative when deployment configuration differs from these defaults. Resolve `<skill-dir>` to the absolute directory containing the parent `SKILL.md`.

## Contents

1. Availability and authentication
2. Modes and permissions
3. File fields and limits
4. Generation fields
5. Asynchronous jobs
6. Points and confirmation
7. Errors and retry policy
8. Download handling

## Availability and Authentication

Base URL:

- Production: `https://slyd.top`
- Development testing: `https://dev.slyd.top`

Never send a development test to production accidentally. Check availability first:

```bash
python <skill-dir>/scripts/slyd_client.py health
```

The health response must report both `feature_flags.user_agent_api=true` and `feature_flags.user_agent_api_queue=true` for the bundled asynchronous client.

Set credentials outside Codex chat:

```bash
export SLYD_API_BASE='https://slyd.top'
export SLYD_API_KEY='slyd_sk_xxx'
```

The client uses `X-SLYD-API-Key`. The API also accepts `Authorization: Bearer <key>`.

## Modes and Permissions

| Mode | Purpose | Required input | Membership notes |
|---|---|---|---|
| `smart_refactor` | Build a new deck from document sources | `target_pages` and `file` or repeated `files` | A custom `template` requires Pro |
| `deep_restore` | Reconstruct visual sources as editable slides | `target_pages` and content in `file`, `files`, or `images` | Images, templates, and multiple documents require Pro |
| `pptx_beautify` | Redesign an existing presentation | PPTX in `file` | The endpoint requires Pro |

All create requests use `POST /api/agent/v1/jobs` with multipart form field `mode`.

## File Fields and Limits

### smart_refactor

| Field | Accepted files | Limit |
|---|---|---|
| `file` / `files` | PDF, TXT, MD, Markdown, DOC, DOCX | Up to 10 primary files |
| `template` | PPTX | One file, Pro, up to 20 slides |
| `style_reference` | PNG, JPG, JPEG, PDF | Up to 4 files |

PPTX as a primary source is deployment-gated by `pptx_as_source`; check `/api/health` before using it. Multiple smart-refactor files have a default combined 90 MB limit.

### deep_restore

| Field | Accepted files | Limit |
|---|---|---|
| `file` | PDF, DOC, DOCX | One legacy primary document |
| `files` | PDF, TXT, MD, Markdown, DOC, DOCX | Up to 5 documents |
| `images` | JPG, JPEG, PNG | Up to 40 images |
| `template` | PPTX | One file, Pro, up to 20 slides |
| `style_reference` | PNG, JPG, JPEG, PDF | Up to 4 files |

PPTX in `files` is deployment-gated by `pptx_as_source`. Non-Pro users may submit only one document and may not use images, templates, or multiple documents.

### pptx_beautify

| Field | Accepted files | Limit |
|---|---|---|
| `file` | PPTX | Exactly one source presentation |
| `documents` | PDF, TXT, MD, Markdown, DOC, DOCX | Up to 5 documents |
| `images` | JPG, JPEG, PNG | Up to 40 images |
| `template` | PPTX | One file, up to 20 slides |
| `style_reference` | PNG, JPG, JPEG, PDF | Up to 4 files |

The default whole-request limit is 150 MB. Deployment configuration may override it.

## Generation Fields

All values are multipart text fields.

| Field | Type | Default or range | Applies to |
|---|---|---|---|
| `target_pages` | integer | Required, 4-30 | smart refactor, deep restore |
| `user_requirements` | string | Optional | all modes |
| `output_language` | string | `zh-CN`; also `en`, `ko`, `ja`, `ru` | all modes |
| `content_density` | string | `low`, `medium`, `high` | all modes |
| `aspect_ratio` | string | `16:9`, `4:3`, `1:1`, `9:16` | generation modes |
| `include_cover` | boolean | `true` | generation modes |
| `include_toc` | boolean | `true` | generation modes |
| `include_background` | boolean | `true` | generation modes |
| `include_transition` | boolean | `false` | generation modes |
| `include_conclusion` | boolean | `true` | generation modes |
| `enable_navigation_bar` | boolean | `false` | generation modes |
| `navigation_position` | string | `top`, `bottom`, `left`, `right` | generation modes |
| `primary_color` | string | HEX color | generation modes |
| `accent_color_1` | string | HEX color | generation modes |
| `accent_color_2` | string | HEX color | generation modes |
| `web_search_enabled` | boolean | Feature-gated | supported generation modes |
| `image_search_enabled` | boolean | Feature-gated | deep restore only |
| `supplement_pages` | integer | 0-20 | PPTX beautify only |

Boolean form values should be lowercase `true` or `false`.

## Asynchronous Jobs

Create:

```http
POST /api/agent/v1/jobs
Idempotency-Key: one-uuid-per-logical-request
```

Status and cancellation:

```http
GET /api/agent/v1/jobs/{job_id}
DELETE /api/agent/v1/jobs/{job_id}
```

Normal status progression:

```text
queued -> running -> exporting -> completed
```

Terminal failure states are `failed`, `canceled`, and `expired`. Status responses can include `queue_position`, `retry_after`, `points_used`, `points_refunded`, `cancel_requested`, `last_error_code`, `last_error_message`, `download_url`, and `download_expires_at`.

Wait at least 30 seconds between status checks even if a smaller fallback interval is available. On `429`, honor HTTP `Retry-After` or JSON `retry_after` and continue querying the same job.

An idempotent replay may return the existing job with `idempotent_replay=true`. Reusing one idempotency key with different request content returns `409 idempotency_key_conflict`.

## Points and Confirmation

Creating a conversion consumes account points. Current server defaults are:

- Standard generation: 5 points per target page.
- Active Pro generation: 4 points per target page.
- Pro beautify: 4 points per original slide plus each supplemental page.

Read `config.points_per_page` and `config.pro_points_per_page` from `/api/health`; deployment pricing may change. The public Agent API does not currently expose an authenticated balance or quote endpoint. Explain the applicable rule and confirm the charged operation before submission. A failed conversion may report refunded points in the job response.

## Errors and Retry Policy

| HTTP or state | Meaning | Action |
|---|---|---|
| `400` | Invalid fields, formats, limits, or sometimes insufficient points | Correct the request; do not blindly retry |
| `401` | Missing, invalid, or deleted API key | Ask the user to configure a valid key outside chat |
| `402` | Insufficient points detected during an atomic charge | Ask the user to add points or reduce page count |
| `403` | Pro membership required | Explain the required account capability |
| `404` | API disabled or job not found for this account/environment | Verify base URL and feature flags |
| `409` | Idempotency conflict or stale execution | Do not create a replacement until the existing job is understood |
| `413` | Request body too large | Reduce or split source files |
| `429` | Rate or queue limit | Honor `Retry-After`; do not resubmit an accepted job |
| `5xx` | Service or conversion failure | Preserve `job_id` and idempotency key; check status before any retry |

Prefer the JSON `message` and `last_error_message` for user-facing explanations. Never expose internal traces or credentials.

## Download Handling

Completed jobs return a temporary `download_url` and `download_expires_at`. Download promptly. The URL is a bearer link and normally does not need the API key.

Validate the saved artifact as an OOXML ZIP containing at least:

- `[Content_Types].xml`
- `ppt/presentation.xml`

The bundled `wait --output` and `download` commands perform this validation.
