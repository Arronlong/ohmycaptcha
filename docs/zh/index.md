<div class="landing landing--dark" markdown>

<div class="landing__hero" markdown>

<div class="landing__eyebrow">OHMYCAPTCHA</div>

# 面向自托管场景的 YesCaptcha 风格验证码服务

OhMyCaptcha 是一个为 **flow2api** 与类似集成场景设计的高质量自托管服务，使用 **FastAPI**、**Playwright** 与 **OpenAI-compatible 多模态模型**，对外提供统一的异步任务 API。

<div class="landing__actions" markdown>

[快速开始](getting-started.md){ .md-button .md-button--primary }
[API 参考](api-reference.md){ .md-button }
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

## 为什么选择 OhMyCaptcha

<div class="grid cards landing-cards" markdown>

-   :material-api: **YesCaptcha 风格 API**

    ---

    为当前仓库已实现的任务类型保留熟悉的异步 `createTask` / `getTaskResult` 语义。

-   :material-google-chrome: **基于浏览器的 reCAPTCHA v3 求解**

    ---

    通过 Playwright + Chromium 执行透明的浏览器链路来生成 reCAPTCHA v3 token。

-   :material-image-search: **多模态图片推理**

    ---

    将图片验证码分析路由到托管或自托管的 OpenAI-compatible 多模态提供方。

-   :material-cloud-outline: **适合自托管的部署路径**

    ---

    可本地运行，也可配合 Render 与 Hugging Face Spaces 文档完成部署。

</div>

## 快速入口

<div class="grid cards landing-cards" markdown>

-   :material-rocket-launch-outline: **快速开始**

    ---

    安装依赖、配置环境变量，并在本地启动服务。

    [打开快速开始](getting-started.md)

-   :material-file-document-outline: **查看 API**

    ---

    查看支持的接口、任务结构与兼容性说明。

    [打开 API 参考](api-reference.md)

-   :material-play-box-outline: **执行验收**

    ---

    验证公开 detector 目标的完整流程，并确认 token 返回行为。

    [打开验收指南](acceptance.md)

-   :material-palette-outline: **开始部署**

    ---

    选择 Render 或 Hugging Face Spaces 路径，安全地发布服务实例。

    [打开部署文档](deployment/render.md)

</div>

## 范围说明

OhMyCaptcha 提供的是**针对本仓库已实现任务类型的 YesCaptcha 风格 API**。它**不宣称**与商业打码平台具备完全等价的全部功能，也**不保证**基于 `minScore` 的分数控制能力。
