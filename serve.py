#!/usr/bin/env python3
"""调参宝 本地服务：提供页面 + 转发大模型请求的本地代理。

有些模型服务不允许网页直接调用（CORS 限制），或者你的网络环境下浏览器直连不稳定。
这时运行本脚本，在本机打开页面，模型请求会先发到本机，再由 Python 转发出去。

    python serve.py            # 默认 http://127.0.0.1:8964
    python serve.py --port 1024

只用 Python 标准库，不需要 pip 安装任何东西。代理只监听本机 127.0.0.1，
只转发 https 请求，API Key 只在你的电脑和模型服务商之间传输。
"""
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from os.path import abspath, dirname
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from webbrowser import open

ROOT = dirname(abspath(__file__))
PROXY_PATH = "/__tiaocanbao_proxy"
FORWARD_HEADERS = {"content-type", "authorization", "x-api-key", "anthropic-version"}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        if PROXY_PATH not in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def do_GET(self):
        if self.path.split("?")[0] == PROXY_PATH:
            self._send(200, b"ok", "text/plain")
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != PROXY_PATH:
            self._send(404, b"not found", "text/plain")
            return
        target = self.headers.get("x-target-url", "")
        if urlparse(target).scheme != "https":
            self._send(400, b"x-target-url must be an https URL", "text/plain")
            return
        body = self.rfile.read(int(self.headers.get("content-length", 0)))
        headers = {k: v for k, v in self.headers.items() if k.lower() in FORWARD_HEADERS}
        req = Request(target, data=body, headers=headers, method="POST")
        try:
            upstream = urlopen(req, timeout=600)
        except HTTPError as e:
            self._send(e.code, e.read(), e.headers.get("content-type", "text/plain"))
            return
        except Exception as e:  # network problems
            self._send(502, f"proxy error: {e}".encode(), "text/plain")
            return
        self.send_response(upstream.status)
        self.send_header("content-type", upstream.headers.get("content-type", "text/event-stream"))
        self.send_header("cache-control", "no-cache")
        self.end_headers()
        try:
            while True:
                chunk = upstream.read1(8192) if hasattr(upstream, "read1") else upstream.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # user pressed Stop
        finally:
            upstream.close()

    def _send(self, code, data, ctype):
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = ArgumentParser(description="调参宝 本地服务")
    ap.add_argument("--port", type=int, default=8964)
    ap.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = ap.parse_args()
    url = f"http://127.0.0.1:{args.port}/index.html"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"调参宝已启动：{url}\n按 Ctrl+C 退出。")
    if not args.no_browser:
        open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")


if __name__ == "__main__":
    main()
