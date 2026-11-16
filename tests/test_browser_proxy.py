from __future__ import annotations

import asyncio
import importlib
import os
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.config import load_config


PROXY_ENV_VARS = (
    "BROWSER_PROXY_SERVER", "BROWSER_PROXY_BYPASS",
    "https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY",
    "all_proxy", "ALL_PROXY", "no_proxy", "NO_PROXY",
)
SOLVERS = (
    ("recaptcha_v2", "RecaptchaV2Solver"),
    ("recaptcha_v3", "RecaptchaV3Solver"),
    ("hcaptcha", "HCaptchaSolver"),
    ("turnstile", "TurnstileSolver"),
)


@pytest.fixture(autouse=True)
def clean_proxy_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "environ", dict(os.environ))
    for name in PROXY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize(("module_name", "class_name"), SOLVERS)
def test_solver_launch_uses_compose_proxy(
    monkeypatch: pytest.MonkeyPatch, module_name: str, class_name: str
) -> None:
    monkeypatch.setenv("https_proxy", "http://192.0.2.10:20171 ")
    monkeypatch.setenv(
        "no_proxy", "localhost,127.0.0.1,10.0.0.0/8,192.0.2.20,192.0.2.10"
    )
    module = importlib.import_module(f"src.services.{module_name}")
    playwright = Mock()
    playwright.chromium.launch = AsyncMock(return_value=AsyncMock())
    playwright.stop = AsyncMock()
    manager = Mock(start=AsyncMock(return_value=playwright))
    monkeypatch.setattr(module, "async_playwright", Mock(return_value=manager))
    solver = getattr(module, class_name)(load_config())

    async def run() -> None:
        await solver.start()
        try:
            assert playwright.chromium.launch.call_args.kwargs.get("proxy") == {
                "server": "http://192.0.2.10:20171",
                "bypass": "<-loopback>,localhost,127.0.0.1,10.0.0.0/8,192.0.2.20,192.0.2.10",
            }
        finally:
            await solver.stop()

    asyncio.run(run())


@pytest.mark.parametrize("name", PROXY_ENV_VARS[:1] + PROXY_ENV_VARS[2:8])
def test_proxy_environment_aliases(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    monkeypatch.setenv(name, "http://proxy.example:8080")
    assert load_config().browser_proxy == {"server": "http://proxy.example:8080"}


def test_no_proxy_configuration() -> None:
    assert load_config().browser_proxy is None


def test_proxy_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    names = PROXY_ENV_VARS[:1] + PROXY_ENV_VARS[2:8]
    for index, name in enumerate(names):
        monkeypatch.setenv(name, f"http://proxy{index}.example:8080")
    for index, name in enumerate(names):
        assert load_config().browser_proxy == {"server": f"http://proxy{index}.example:8080"}
        monkeypatch.delenv(name)


def test_explicit_empty_server_disables_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("https_proxy", "http://proxy.example:8080")
    monkeypatch.setenv("BROWSER_PROXY_SERVER", "  ")
    assert load_config().browser_proxy is None


def test_empty_standard_variable_uses_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("https_proxy", "  ")
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example:8080")
    assert load_config().browser_proxy == {"server": "http://proxy.example:8080"}


@pytest.mark.parametrize("name", ("no_proxy", "NO_PROXY", "BROWSER_PROXY_BYPASS"))
def test_bypass_rules(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    monkeypatch.setenv("https_proxy", "http://proxy.example:8080")
    monkeypatch.setenv(name, " localhost, 127.0.0.1, 10.0.0.0/8, .example.com, ,")
    assert load_config().browser_proxy == {
        "server": "http://proxy.example:8080",
        "bypass": "<-loopback>,localhost,127.0.0.1,10.0.0.0/8,.example.com",
    }


def test_bypass_precedence_and_empty_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("https_proxy", "http://proxy.example:8080")
    monkeypatch.setenv("NO_PROXY", "upper.example")
    monkeypatch.setenv("no_proxy", "lower.example")
    monkeypatch.setenv("BROWSER_PROXY_BYPASS", "custom.example")
    assert load_config().browser_proxy == {
        "server": "http://proxy.example:8080", "bypass": "<-loopback>,custom.example"
    }
    monkeypatch.setenv("BROWSER_PROXY_BYPASS", "")
    assert load_config().browser_proxy == {"server": "http://proxy.example:8080"}
    monkeypatch.delenv("BROWSER_PROXY_BYPASS")
    assert load_config().browser_proxy == {
        "server": "http://proxy.example:8080", "bypass": "<-loopback>,lower.example"
    }


@pytest.mark.parametrize("bypass", ("*", "localhost, *"))
def test_wildcard_bypasses_all_proxy(monkeypatch: pytest.MonkeyPatch, bypass: str) -> None:
    monkeypatch.setenv("https_proxy", "http://proxy.example:8080")
    monkeypatch.setenv("no_proxy", bypass)
    assert load_config().browser_proxy is None


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        ("proxy.example:8080", {"server": "http://proxy.example:8080"}),
        ("http://[::1]:8080/", {"server": "http://[::1]:8080"}),
        ("https://proxy.example:8443", {"server": "https://proxy.example:8443"}),
        ("socks5://proxy.example:1080", {"server": "socks5://proxy.example:1080"}),
        (
            "http://user%40example:p%3Ass%2Fword@proxy.example:8080",
            {"server": "http://proxy.example:8080", "username": "user@example", "password": "p:ss/word"},
        ),
    ),
)
def test_proxy_url_normalization(
    monkeypatch: pytest.MonkeyPatch, url: str, expected: dict[str, str]
) -> None:
    monkeypatch.setenv("BROWSER_PROXY_SERVER", url)
    assert load_config().browser_proxy == expected


@pytest.mark.parametrize(
    "url",
    (
        "ftp://user:secret@proxy.example:8080",
        "http://user:secret@",
        "http://user:secret@proxy.example:invalid",
        "http://user:secret@proxy.example:99999",
        "http://user:secret@proxy.example:0",
        "http://user:secret@proxy.example/path",
        "http://user:secret@proxy.example?query=1",
        "http://user:secret@proxy.example#fragment",
        "socks5://user:secret@proxy.example:1080",
    ),
)
def test_invalid_proxy_rejected_without_credentials(
    monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    monkeypatch.setenv("BROWSER_PROXY_SERVER", url)
    with pytest.raises(ValueError) as error:
        load_config()
    assert "secret" not in str(error.value)
    assert "secret" not in repr(error.value.__cause__)


def test_config_repr_hides_proxy_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("https_proxy", "http://user:secret@proxy.example:8080")
    assert "secret" not in repr(load_config())


@pytest.mark.skipif(
    os.environ.get("RUN_BROWSER_PROXY_TESTS") != "1",
    reason="Set RUN_BROWSER_PROXY_TESTS=1 with Chromium installed",
)
@pytest.mark.parametrize("bypass", ("localhost,127.0.0.1", "127.0.0.0/8"))
def test_real_chromium_proxy_and_bypass(
    monkeypatch: pytest.MonkeyPatch, bypass: str
) -> None:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    from playwright.async_api import Error, async_playwright

    requests: list[tuple[str, str]] = []

    class ProxyHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests.append(("GET", self.path))
            if self.path.endswith("/script.js"):
                content = b"window.proxiedScript = true;"
                content_type = "application/javascript"
            elif self.path.endswith("/frame"):
                content = b"<p>proxied frame</p>"
                content_type = "text/html"
            else:
                content = (
                    b'<script src="http://assets.proxy-test.invalid/script.js"></script>'
                    b'<iframe src="http://frame.proxy-test.invalid/frame"></iframe>'
                )
                content_type = "text/html"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_CONNECT(self) -> None:
            requests.append(("CONNECT", self.path))
            self.send_error(502)

        def log_message(self, format: str, *args: object) -> None:
            pass

    class DirectHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"direct target")

        def log_message(self, format: str, *args: object) -> None:
            pass

    proxy_server = ThreadingHTTPServer(("127.0.0.1", 0), ProxyHandler)
    direct_server = ThreadingHTTPServer(("127.0.0.1", 0), DirectHandler)
    servers = (proxy_server, direct_server)
    threads = [Thread(target=server.serve_forever, daemon=True) for server in servers]
    for thread in threads:
        thread.start()
    monkeypatch.setenv("https_proxy", f"http://127.0.0.1:{proxy_server.server_port}")
    monkeypatch.setenv("no_proxy", bypass)

    async def run() -> None:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                proxy=load_config().browser_proxy,
                executable_path=os.environ.get("BROWSER_TEST_EXECUTABLE"),
            )
            try:
                page = await browser.new_page()
                await page.goto("http://page.proxy-test.invalid/", timeout=15_000)
                assert await page.evaluate("window.proxiedScript") is True
                assert await page.frame_locator("iframe").locator("p").inner_text() == "proxied frame"
                await page.goto(f"http://127.0.0.1:{direct_server.server_port}/direct")
                assert await page.locator("body").inner_text() == "direct target", requests
                with pytest.raises(Error):
                    await page.goto("https://secure.proxy-test.invalid/", timeout=10_000)
            finally:
                await browser.close()

        assert ("GET", "http://page.proxy-test.invalid/") in requests
        assert ("GET", "http://assets.proxy-test.invalid/script.js") in requests
        assert ("GET", "http://frame.proxy-test.invalid/frame") in requests
        assert ("CONNECT", "secure.proxy-test.invalid:443") in requests
        assert not any(path.endswith("/direct") for _, path in requests)

    try:
        asyncio.run(run())
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=5)
