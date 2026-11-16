# 快速开始

## 环境要求

- Python 3.10+
- 通过 Playwright 安装 Chromium
- 具备访问以下资源的网络能力：
  - 目标网站
  - 你配置的 OpenAI-compatible 模型接口

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

## 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `CLIENT_KEY` | 客户端鉴权密钥 | 未设置 |
| `CAPTCHA_BASE_URL` | OpenAI-compatible API 地址 | `https://your-openai-compatible-endpoint/v1` |
| `CAPTCHA_API_KEY` | 模型接口密钥 | 未设置 |
| `CAPTCHA_MODEL` | 强文本模型 | `gpt-5.4` |
| `CAPTCHA_MULTIMODAL_MODEL` | 多模态模型 | `qwen3.5-2b` |
| `CAPTCHA_RETRIES` | 重试次数 | `3` |
| `CAPTCHA_TIMEOUT` | 模型超时（秒） | `30` |
| `BROWSER_HEADLESS` | 是否无头运行 Chromium | `true` |
| `BROWSER_TIMEOUT` | 浏览器超时（秒） | `30` |
| `BROWSER_PROXY_SERVER` | 浏览器专用代理；未设置时读取通用代理环境变量 | 自动 |
| `BROWSER_PROXY_BYPASS` | 浏览器直连规则，逗号分隔 | `no_proxy` / `NO_PROXY` |
| `SERVER_HOST` | 监听地址 | `0.0.0.0` |
| `SERVER_PORT` | 监听端口 | `8000` |

## Docker 代理部署

浏览器会按以下优先级选择一个代理，用于所有 HTTP/HTTPS 页面、iframe 和子资源：

`BROWSER_PROXY_SERVER` → `https_proxy` → `HTTPS_PROXY` → `http_proxy` → `HTTP_PROXY` → `all_proxy` → `ALL_PROXY`。

通用变量的空值会跳过。显式设置 `BROWSER_PROXY_SERVER=""` 可关闭浏览器代理。支持 HTTP、HTTPS 和无认证 SOCKS5；HTTP/HTTPS 认证使用 `http://user:password@proxy-host:port`，特殊字符需 URL 编码。

直连规则优先读取 `BROWSER_PROXY_BYPASS`，其次是 `no_proxy`、`NO_PROXY`。空的专用变量会清除继承的规则；`*` 表示全部直连。Chromium 的 CIDR 规则（如 `10.0.0.0/8`）用于 URL 中的 IP 地址，不会先解析域名再匹配；内网域名需单独列出。

复制仓库根目录的 `docker-compose.example.yml` 为 `docker-compose.yml`，并创建 `.env`：

```dotenv
CLIENT_KEY=replace-with-your-secret
HTTP_PROXY=http://proxy-host:20171
HTTPS_PROXY=http://proxy-host:20171
NO_PROXY=localhost,127.0.0.1,::1,10.0.0.0/8,model.internal
```

将 `proxy-host` 换成容器可访问的代理地址，并在 Compose 的 `environment` 中补充任务所需的 `CLOUD_*` 或 `LOCAL_*` 模型配置。容器中的 `127.0.0.1` 指向容器自身。

```bash
docker compose up -d --build --force-recreate
docker compose logs -f ohmycaptcha
```

仓库使用 `Dockerfile.render`，示例已显式指定。必须重新构建并重建容器，单纯重启旧镜像不会应用代码修改。这些是运行时配置；构建时下载系统包和浏览器所需的网络需单独保证。

浏览器专用变量不影响 Python 模型请求和音频下载。这些请求仍由 HTTPX 读取通用代理环境变量；仅设 `https_proxy` 不会代理 Python 的 HTTP 请求。HTTPX 与 Chromium 的绕过规则并不完全相同，内网模型的 IP/主机名应在 `NO_PROXY` 中显式列出。

## 启动服务

```bash
export CLIENT_KEY="your-client-key"
export CAPTCHA_BASE_URL="https://your-openai-compatible-endpoint/v1"
export CAPTCHA_API_KEY="your-api-key"
export CAPTCHA_MODEL="gpt-5.4"
export CAPTCHA_MULTIMODAL_MODEL="qwen3.5-2b"
python main.py
```

## 验证启动

### 根接口

```bash
curl http://localhost:8000/
```

### 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

健康检查响应中应包含已注册任务类型以及当前运行时模型配置。

## 本地 / 自托管模型支持

图片识别路径基于 **OpenAI-compatible API** 设计。因此，只要你的后端具备兼容的 chat-completions 语义并支持图像输入，就可以把 `CAPTCHA_BASE_URL` 指向托管服务、内部网关或本地/自托管多模态网关。

文档采用通用兼容性表述，而不是对每一种模型服务栈做完整验证承诺。
