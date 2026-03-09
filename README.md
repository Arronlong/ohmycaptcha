<div align="center">

# OhMyCaptcha

**Self-hostable YesCaptcha-style captcha solver for flow2api and similar integrations**

<p>
  <a href="https://github.com/shenhao-stu/ohmycaptcha"><img alt="GitHub Repo" src="https://img.shields.io/badge/GitHub-ohmycaptcha-181717?logo=github"></a>
  <a href="https://shenhao-stu.github.io/ohmycaptcha/"><img alt="Docs" src="https://img.shields.io/badge/docs-MkDocs%20Material-526CFE?logo=materialformkdocs&logoColor=white"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.119-009688?logo=fastapi&logoColor=white">
  <img alt="Playwright" src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white">
  <img alt="OpenAI Compatible" src="https://img.shields.io/badge/OpenAI--compatible-Multimodal-6E56CF">
  <img alt="Render" src="https://img.shields.io/badge/Deploy-Render-000000?logo=render&logoColor=white">
  <img alt="Hugging Face Spaces" src="https://img.shields.io/badge/Deploy-Hugging%20Face%20Spaces-FFB000?logo=huggingface&logoColor=black">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111">
</p>

[中文说明](README.zh-CN.md) · [Documentation](https://shenhao-stu.github.io/ohmycaptcha/) · [Render Guide](https://shenhao-stu.github.io/ohmycaptcha/deployment/render/) · [Hugging Face Guide](https://shenhao-stu.github.io/ohmycaptcha/deployment/huggingface/) · [Skills](skills/README.md)

![OhMyCaptcha hero](docs/assets/ohmycaptcha-hero.png)

</div>

OhMyCaptcha is a polished, self-hostable captcha-solving service that exposes a **YesCaptcha-style async API** for the task types implemented in this repository. It is built for **flow2api**, internal routing layers, and other systems that expect `createTask` / `getTaskResult` semantics.

---

## Highlights

- **YesCaptcha-style async API** for supported task types
- **Playwright + Chromium** solving path for reCAPTCHA v3 token generation
- **OpenAI-compatible multimodal backends** for image captcha analysis
- **Self-hosted friendly deployment** for local environments, Render, and Hugging Face Spaces
- **Bilingual docs** with GitHub Pages publishing
- **Reusable agent skills** for Claude Code, OpenCode, and similar workflows

---

## Why OhMyCaptcha

Managed captcha-solving platforms are convenient, but self-hosted workflows often need more control:

- **Deployment ownership** — run the service in your own environment
- **Model routing flexibility** — connect hosted or self-hosted OpenAI-compatible multimodal backends
- **Transparent solving flow** — understand the browser path instead of hiding it behind a black box
- **Integration compatibility** — keep a familiar YesCaptcha-style API surface for existing clients

> OhMyCaptcha is best described as a **self-hostable YesCaptcha-compatible service for the task types implemented here**. It does **not** claim full parity with every commercial captcha-solving platform.

---

## Supported task types

### reCAPTCHA v3

- `RecaptchaV3TaskProxyless`
- `RecaptchaV3TaskProxylessM1`
- `RecaptchaV3TaskProxylessM1S7`
- `RecaptchaV3TaskProxylessM1S9`

All four task types currently use the same browser-based solving path in this codebase.

### Image captcha recognition

- `ImageToTextTask`

`ImageToTextTask` uses an Argus-inspired multimodal recognition prompt, normalizes images into a 1440×900 coordinate space, and returns structured recognition output serialized into `solution.text`.

---

## Architecture

```text
Client / flow2api
        │
        ▼
  POST /createTask
        │
        ▼
 In-memory TaskManager
        │
   ┌────┴────┐
   ▼         ▼
Playwright   OpenAI-compatible
reCAPTCHA    multimodal model
solver       backend
   │         │
   └────┬────┘
        ▼
 POST /getTaskResult
```

### Core building blocks

- **FastAPI** powers the HTTP API
- **Playwright + Chromium** generate reCAPTCHA v3 tokens
- **OpenAI-compatible multimodal APIs** analyze image captchas
- **An in-memory async task manager** handles background execution

---

## Quick start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

### 2. Configure environment variables

```bash
export CLIENT_KEY="your-client-key"
export CAPTCHA_BASE_URL="https://your-openai-compatible-endpoint/v1"
export CAPTCHA_API_KEY="your-api-key"
export CAPTCHA_MODEL="gpt-5.4"
export CAPTCHA_MULTIMODAL_MODEL="qwen3.5-2b"
export BROWSER_HEADLESS="true"
export BROWSER_TIMEOUT="30"
```

### 3. Start the service

```bash
python main.py
```

### 4. Verify health

```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
```

---

## API surface

- `POST /createTask`
- `POST /getTaskResult`
- `POST /getBalance`
- `GET /api/v1/health`

### Create a reCAPTCHA v3 task

```bash
curl -X POST http://localhost:8000/createTask \
  -H "Content-Type: application/json" \
  -d '{
    "clientKey": "your-client-key",
    "task": {
      "type": "RecaptchaV3TaskProxyless",
      "websiteURL": "https://antcpt.com/score_detector/",
      "websiteKey": "6LcR_okUAAAAAPYrPe-HK_0RULO1aZM15ENyM-Mf",
      "pageAction": "homepage"
    }
  }'
```

### Poll task result

```bash
curl -X POST http://localhost:8000/getTaskResult \
  -H "Content-Type: application/json" \
  -d '{
    "clientKey": "your-client-key",
    "taskId": "uuid-from-createTask"
  }'
```

### Create an image task

```bash
curl -X POST http://localhost:8000/createTask \
  -H "Content-Type: application/json" \
  -d '{
    "clientKey": "your-client-key",
    "task": {
      "type": "ImageToTextTask",
      "body": "<base64-encoded-image>"
    }
  }'
```

---

## Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `CLIENT_KEY` | Client authentication key used as `clientKey` | unset |
| `CAPTCHA_BASE_URL` | OpenAI-compatible API base URL | `https://your-openai-compatible-endpoint/v1` |
| `CAPTCHA_API_KEY` | API key for the configured model backend | unset |
| `CAPTCHA_MODEL` | Strong text model name | `gpt-5.4` |
| `CAPTCHA_MULTIMODAL_MODEL` | Multimodal model name | `qwen3.5-2b` |
| `CAPTCHA_RETRIES` | Retry count for model or browser operations | `3` |
| `CAPTCHA_TIMEOUT` | Model request timeout in seconds | `30` |
| `BROWSER_HEADLESS` | Whether Chromium runs headless | `true` |
| `BROWSER_TIMEOUT` | Page load timeout in seconds | `30` |
| `SERVER_HOST` | Bind host | `0.0.0.0` |
| `SERVER_PORT` | Bind port | `8000` |

---

## Deployment

- [Render deployment](https://shenhao-stu.github.io/ohmycaptcha/deployment/render/)
- [Hugging Face Spaces deployment](https://shenhao-stu.github.io/ohmycaptcha/deployment/huggingface/)
- [Full documentation](https://shenhao-stu.github.io/ohmycaptcha/)

---

## Skills

This repository includes reusable local skills under `skills/`:

- `skills/ohmycaptcha/` — operate, deploy, validate, and integrate OhMyCaptcha
- `skills/ohmycaptcha-image/` — generate public-safe README and docs visuals

They are designed for Claude Code, OpenCode, OpenClaw-style workflows, and similar agent environments.

---

## Acceptance status

This repository has been validated locally against the public reCAPTCHA v3 detector target at:

- `https://antcpt.com/score_detector/`
- site key: `6LcR_okUAAAAAPYrPe-HK_0RULO1aZM15ENyM-Mf`

The verified result for this codebase is that the service can successfully:

- start the API service
- create a detector task
- poll until `ready`
- return a non-empty `solution.gRecaptchaResponse`

The implementation does **not** claim guaranteed score targeting or full compatibility with all commercial captcha service features.

---

## Limitations

- Tasks are stored **in memory** and expire after the configured TTL
- `minScore` exists in the schema for compatibility, but the current solver does **not** enforce score targeting
- `ImageToTextTask` currently returns structured output serialized into `solution.text`
- Reliability depends on browser environment, target-site behavior, IP reputation, and model or provider quality

---

## Development

```bash
pytest tests/
npx pyright
python -m mkdocs build --strict
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=shenhao-stu/ohmycaptcha&type=Date)](https://www.star-history.com/#shenhao-stu/ohmycaptcha&Date)

## License

This repository is released under the [MIT License](LICENSE).
