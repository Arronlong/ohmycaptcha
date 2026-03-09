<div class="landing landing--dark" markdown>

<div class="landing__hero" markdown>

<div class="landing__eyebrow">OHMYCAPTCHA</div>

# Self-hostable captcha solving, with a YesCaptcha-style API

OhMyCaptcha is a polished self-hosted service for **flow2api** and similar integrations, combining **FastAPI**, **Playwright**, and **OpenAI-compatible multimodal models** behind a clean async task API.

<div class="landing__actions" markdown>

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api-reference.md){ .md-button }
[GitHub](https://github.com/shenhao-stu/ohmycaptcha){ .md-button }

</div>

<div class="landing__badges" markdown>

- `RecaptchaV3TaskProxyless`
- `RecaptchaV3TaskProxylessM1`
- `RecaptchaV3TaskProxylessM1S7`
- `RecaptchaV3TaskProxylessM1S9`
- `ImageToTextTask`

</div>

</div>

<div class="landing__panel" markdown>

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

</div>

</div>

## Why teams use OhMyCaptcha

<div class="grid cards landing-cards" markdown>

-   :material-api: **YesCaptcha-style API**

    ---

    Keep familiar async `createTask` / `getTaskResult` semantics for the task types implemented in this repository.

-   :material-google-chrome: **Browser-based reCAPTCHA v3 solving**

    ---

    Use Playwright + Chromium to generate reCAPTCHA v3 tokens through a transparent browser execution path.

-   :material-image-search: **Multimodal image reasoning**

    ---

    Route image captcha analysis through hosted or self-hosted OpenAI-compatible multimodal providers.

-   :material-cloud-outline: **Self-hosted deployment options**

    ---

    Run locally or deploy with the included Render and Hugging Face Spaces guidance.

</div>

## Quick paths

<div class="grid cards landing-cards" markdown>

-   :material-rocket-launch-outline: **Get started**

    ---

    Install dependencies, configure environment variables, and bring the service up locally.

    [Open quick start](getting-started.md)

-   :material-file-document-outline: **Read the API**

    ---

    See supported endpoints, task shapes, and compatibility notes.

    [Open API reference](api-reference.md)

-   :material-play-box-outline: **Run acceptance**

    ---

    Validate the public detector target flow and confirm token generation behavior.

    [Open acceptance guide](acceptance.md)

-   :material-palette-outline: **Deploy it**

    ---

    Choose a path for Render or Hugging Face Spaces and ship a public instance safely.

    [Open deployment docs](deployment/render.md)

</div>

## Scope note

OhMyCaptcha implements a **YesCaptcha-style API surface for the task types available in this repository**. It does **not** claim full feature parity with commercial captcha-solving vendors, and it does **not** guarantee score targeting for `minScore`.
