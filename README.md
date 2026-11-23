# 调参宝 TiaoCanBao

把论文里的算法变成**可读、可调、可核对**的代码。

投喂一篇论文和它的实现代码，调参宝会：

1. **抽取参数清单**：列出算法用到的所有变量，区分物理参数、数值参数和导出量，每个数值附上论文出处；
2. **核验出处**：在论文原文里逐字查找模型给出的引文，找不到就标红，防止大模型编造数值；
3. **代码对账**：词法扫描代码里所有写死的常数，列出"论文有、代码没有"和"代码有、论文没有"（magic numbers）的参数；
4. **可读视图**：按算法顺序，把每一步写成公式加白话解释，并对应到代码行；
5. **调参出图**：拖动滑块只改数值、不动代码框架。页面用"代码框架指纹"（把参数值替换为占位符后的 SHA-256）证明这一点。

> 在线使用：`https://YOUR_GITHUB.github.io/tiaocanbao/`（部署后替换成你的地址）

## 特点

- **单文件、零依赖**：`index.html` 内置了公式渲染（KaTeX）和 PDF 解析（pdf.js），不加载任何 CDN 或外网字体。可以双击打开，也可以放到内网服务器上。
- **自带 Key，数据不经过第三方**：论文和代码只会发送给你自己选的模型服务商。支持 DeepSeek、通义千问、Kimi、智谱 GLM（国内可直连）、Claude，以及任何 OpenAI 兼容接口。
- **确定性检查**：出处核验、代码对账、框架指纹都不经过 AI，可以用来检查 AI 的抽取结果。

## 三种用法

| 用法 | 适合 | 怎么做 |
|---|---|---|
| 在线网页 | 大多数人 | 打开 GitHub Pages 地址，在"模型服务"里填 API Key |
| 本地双击 | 不想联网打开网页 | 下载 `index.html`，双击用浏览器打开 |
| 本地服务 + 代理 | 浏览器直连模型服务失败时 | `python serve.py`，会自动打开 `http://127.0.0.1:8964` |

有些模型服务不允许网页直接调用（浏览器的 CORS 限制），或者某些网络下直连不稳定。这时页面会提示"浏览器无法直连"，请改用第三种方式。`serve.py` 只用 Python 标准库，不需要安装任何包；代理只监听本机，只转发 https 请求。

## 快速开始

```bash
git clone https://github.com/YOUR_GITHUB/tiaocanbao.git
cd tiaocanbao
python serve.py
```

打开后页面会先载入一个示例（单轴扭曲模型的量子 Fisher 信息与自旋压缩），不需要 Key 就能拖动参数、看代码和对账结果。要处理自己的论文：

1. 点"填写论文、代码与模型"，选择模型服务，填入 API Key；
2. 粘贴论文正文（推荐 arXiv 的 LaTeX 源码，公式最准；也可以上传 PDF）和 Python 实现；
3. 点"抽取参数"，然后在"对账"标签页检查结果；
4. 需要出图时点"生成预览"。

## 使用须知

- **抽取结果是草稿。** 只有标着"原文已核验"的数值在论文中逐字找到了出处，其余请自己确认。
- **预览图是 JS 移植。** 浏览器不能运行 Python，所以预览图由模型把算法翻译成 JS 来算。它和你的 Python 代码是两份实现，定量结论请以本地运行 Python 为准。内置示例的 JS 版已与 Python 版逐点核对（`examples/oat_qfi.py`）。
- **能调的参数**：代码里写成 `name = 数值` 或 `f(name=数值)` 形式的常数才能绑定和调节。
- **API Key 的存放**：默认不保存。勾选"在本浏览器记住 Key"后，Key 只存在你这台电脑的浏览器 localStorage 里。公共电脑上请不要勾选。

## 部署到 GitHub Pages

1. 把本仓库推到 GitHub；
2. Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`，目录 `/ (root)`；
3. 几分钟后即可通过 `https://<用户名>.github.io/tiaocanbao/` 访问。

国内访问 GitHub Pages 有时不稳定，可以把仓库同步一份到 Gitee，方便下载 `index.html` 或整个仓库在本地运行。

## 开发

页面源码在 `src/app.html`，第三方库在 `vendor/`。修改后运行：

```bash
python build.py   # 生成自包含的 index.html
```

## 许可

本项目采用 MIT 许可证，见 [LICENSE](LICENSE)。第三方组件的许可见 [NOTICE](NOTICE)。

本项目在开发中使用了 AI 辅助编程（Anthropic Claude）；设计、验证和维护由作者负责。

---

## English

**TiaoCanBao** (调参宝, "parameter-tuning helper") turns the algorithm in a paper into readable, tunable, auditable code. Paste a paper and its Python implementation; it extracts every parameter with a verbatim citation, verifies each citation against the paper text, lexically reconciles the parameters with the constants in your code (flagging magic numbers), renders each algorithm step as a formula with a plain-language explanation, and lets you tune values with sliders while a SHA-256 fingerprint proves the code structure is unchanged.

Single self-contained HTML file, no CDN. Bring your own API key (DeepSeek, Qwen, Kimi, GLM, Claude, or any OpenAI-compatible endpoint). If the browser cannot call your provider directly (CORS), run `python serve.py` for a local stdlib-only proxy. MIT licensed.
