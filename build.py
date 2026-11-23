#!/usr/bin/env python3
"""把 src/app.html 和 vendor/ 里的第三方库打包成一个自包含的 index.html。

    python build.py

生成的 index.html 不依赖任何 CDN 或外网字体，可以直接双击打开、放到 GitHub Pages，
或者拷到内网服务器上使用。
"""

from os.path import abspath, dirname, getsize, join

ROOT = dirname(abspath(__file__))


def read(*paths: str):
    with open(join(ROOT, *paths), encoding="utf-8") as f:
        return f.read()


def main():
    html = read("src", "app.html")
    vendors = {
        "/*VENDOR:katex*/": read("vendor", "katex.min.js"),
        "/*VENDOR:pdf*/": read("vendor", "pdf.min.js"),
        "/*VENDOR:pdfworker*/": read("vendor", "pdf.worker.min.js"),
    }
    for marker, code in vendors.items():
        assert html.count(marker) == 1, f"marker {marker} not found exactly once"
        assert "</script" not in code.lower(), f"{marker} contains </script"
        html = html.replace(marker, code)
    if "</html>" not in html:
        html += "\n</body>\n</html>\n"
    out = join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out} ({getsize(out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
