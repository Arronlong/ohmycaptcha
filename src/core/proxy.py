from __future__ import annotations

import os
from urllib.parse import unquote, urlsplit

from playwright.async_api import ProxySettings


def load_browser_proxy() -> ProxySettings | None:
    server = os.environ.get("BROWSER_PROXY_SERVER")
    if server is None:
        server = next(
            (
                value
                for name in (
                    "https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY",
                    "all_proxy", "ALL_PROXY",
                )
                if (value := os.environ.get(name, "").strip())
            ),
            "",
        )
    server = server.strip()
    if not server:
        return None

    bypass = os.environ.get(
        "BROWSER_PROXY_BYPASS",
        os.environ.get("no_proxy", os.environ.get("NO_PROXY", "")),
    )
    bypass_rules = [rule.strip() for rule in bypass.split(",") if rule.strip()]
    if "*" in bypass_rules:
        return None

    if "://" not in server:
        server = f"http://{server}"
    try:
        parsed = urlsplit(server)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        raise ValueError("Invalid browser proxy URL or port") from None
    if (
        parsed.scheme not in {"http", "https", "socks5"}
        or not hostname
        or any(character.isspace() for character in hostname)
        or port == 0
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Browser proxy must be an HTTP, HTTPS or SOCKS5 server URL")
    if parsed.scheme == "socks5" and parsed.username is not None:
        raise ValueError("Chromium does not support SOCKS5 proxy authentication")

    host = f"[{hostname}]" if ":" in hostname else hostname
    address = f"{host}:{port}" if port is not None else host
    proxy: ProxySettings = {"server": f"{parsed.scheme}://{address}"}
    if parsed.username is not None:
        proxy["username"] = unquote(parsed.username)
        proxy["password"] = unquote(parsed.password or "")
    if bypass_rules:
        # 将 Playwright 的隐式本机代理规则放在前面，让用户的显式直连规则优先生效。
        proxy["bypass"] = ",".join(["<-loopback>", *bypass_rules])
    return proxy
