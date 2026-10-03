# Changelog

本文件记录 sciforge-desktop 的显著变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

English summary: see the bottom section.

---

## [Unreleased]

### 文档

- 建立完整文档套件：`docs/index.md`、`docs/installation.md`、`docs/quickstart.md`、`docs/mcp-bridge.md`、`docs/desktop-core-relationship.md`。
- `README.md` 扩写为完整中文主文档，新增界面导览、与 MCP 版关系、学科/工具能力来源、已知缺陷等章节。
- 新增 `README_EN.md`（独立完整英文文档，非中文版的简写）。
- 新增 `CONTRIBUTING.md`（含双仓同步规则）、`CODE_OF_CONDUCT.md`（Contributor Covenant v2.1）、`SECURITY.md`、`CHANGELOG.md`（本文件）。
- 新增 GitHub 协作基建：Issue 模板（bug_report / feature_request / config.yml）、PR 模板、`CODEOWNERS`、`SUPPORT.md`、`FUNDING.yml`、`dependabot.yml`。
- 新增 CI 工作流 `.github/workflows/ci.yml`：ruff lint + pytest；GUI 相关测试在无 PySide6 或无显示环境时条件跳过。

### 已知问题

- 以下缺陷在本次文档工作中被记录但**未修复**，修复进度见「已知缺陷与待修复项」：
  - entry point 缺包前缀，安装后可能无法导入
  - 打包元数据缺 `authors` / `urls` / `keywords` / `classifiers`
  - 无 ruff / mypy / coverage 配置
  - 0 个测试用例，无 pytest 配置
  - `web_search` 返回契约与同模块其余工具不一致
  - `cli tools` 不暴露函数签名
  - `MCPClient` 在本仓内无调用方
  - PySide6 在 Python 3.14 上无可用 wheel（2026-09-26 实测）

---

## [0.1.0] — 初始骨架

发布日期：仓库未记录。本文档创建于 2026-09-26，此前项目没有变更日志；本节依据当次对仓库代码的逐文件核对整理，不代表完整的提交历史。

### 新增

- **包布局**：6 个平铺顶层包 —— `agent` / `api` / `cli` / `core` / `gui` / `sessions`。
- **`cli/main.py`**：argparse 命令行入口，提供 3 个子命令。
  - `serve`：占位实现，仅打印提示。
  - `sessions`：列出本地会话，输出 `session_id<TAB>name<TAB>created_at`。
  - `tools`：列出 agent 基础工具，输出 `tool_name<TAB>docstring 首行`。
  - `main(argv=None) -> int` 接受可选 argv 并返回退出码。
- **`sessions/session_store.py`**：本地 JSON 会话存储，5 个公开函数 —— `create_session`、`list_sessions`、`load_session`、`save_session`、`delete_session`。存储于 `~/.sciforge-desktop/sessions/{uuid4().hex}.json`；`session_id` 采用字符白名单 + 目录包含性双层校验防路径穿越。
- **`agent/tools.py`**：6 个纯标准库工具 —— `web_search`、`read_file`、`write_file`、`list_files`、`make_dir`、`delete_file`。文件类工具受路径沙箱约束（允许根为 `Path.home()` 与 `Path.cwd()`）；提供 `SCI_FORGE_OFFLINE=1` 离线开关。
- **`api/mcp_client.py`**：`MCPClient` 类，JSON-RPC 2.0 over stdio 客户端。已实现 `start`、`initialize`、`call_tool`、`notify`、`notifications`、`close`；协议版本 `2024-11-05`；客户端身份 `sciforge-desktop/0.1.0`。
- **`gui/main_window.py`**：PySide6 懒加载主窗口，默认 960 × 640。含菜单栏（文件 → 退出；帮助 → 关于）、状态栏（显示「就绪」）、左侧导航（会话 / 工具 / 设置）、中央占位标签。模块顶层不 import PySide6，可在未安装 PySide6 的环境中安全 import。
- **`core/__init__.py`**：空占位包，仅含 docstring，声明核心同步为后续任务。
- **`pyproject.toml`**：`requires-python >= 3.10`，唯一运行依赖 `PySide6 >= 6.6`，build-backend 为 `setuptools>=68 / setuptools.build_meta`。
- **`.gitignore`**：25 行，覆盖 Python 缓存、打包产物、虚拟环境、编辑器与操作系统文件。

### 已知问题

- `core/` 为空占位，与 `sciforge/core`（MCP 版，364 行）无代码级共享；两仓无同步机制，`pyproject.toml` 亦未声明对 `sci-forge` 的依赖。
- `MCPClient` 已实现但本仓内无任何调用方；不存在 agent 主循环与 LLM 接入。
- 界面导航项与「关于」动作未连接槽；无 PyInstaller / Qt 部署脚本；`gui/main_window.py:main()` 未注册为 entry point。
- 0 个测试用例，无 `tests/` 目录，无 pytest 配置；唯一校验手段为 AST 语法检查。

---

## 版本策略

- 采用语义化版本（SemVer）。
- `0.x` 阶段不承诺 API 稳定性；`core/` 同步落地后可能引入破坏性变更。
- 发布时更新本文件的 `[Unreleased]` 段落，并同步更新 `pyproject.toml` 的 `version` 字段。
- 破坏性变更在对应版本条目的 `Changed` 或 `Removed` 小节中显式标注。

---

## 关联仓库

| 仓库 | 变更日志 |
| --- | --- |
| `sciforge`（MCP 服务器版） | 见该仓库自带的变更记录 |

双仓核心逻辑改动需按 [`CONTRIBUTING.md`](CONTRIBUTING.md) 的双仓同步规则同时提交。

---

## English Summary

- Format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).
- **[Unreleased]** adds the full documentation suite (5 files under `docs/`, expanded
  Chinese `README.md`, standalone `README_EN.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, this changelog), the GitHub collaboration
  scaffolding (issue templates, PR template, `CODEOWNERS`, `SUPPORT.md`,
  `FUNDING.yml`, `dependabot.yml`), and a CI workflow running ruff plus pytest
  with GUI tests conditionally skipped. Eight known defects are recorded but
  **not fixed**.
- **[0.1.0]** is the initial skeleton: 6 flat top-level packages, a 3-subcommand
  CLI (with `serve` as a placeholder), JSON-file session storage with two-layer
  path-traversal protection, 6 standard-library agent tools behind a path
  sandbox, a JSON-RPC-over-stdio `MCPClient` with no in-repo caller, and a
  lazily loaded PySide6 window whose navigation and About action are unwired.
  The release date was not recorded in the repository; this entry was
  reconstructed from a code review on 2026-09-26 and is not a substitute for
  full commit history.
- The project is pre-1.0: API stability is not guaranteed, and landing the
  `core/` synchronisation may introduce breaking changes.
