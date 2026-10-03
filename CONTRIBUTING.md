# Contributing to sciforge-desktop

感谢你愿意为 sciforge 桌面客户端出力。本文件说明提交流程、环境准备，以及本项目特有的**双仓同步规则**。

English summary: see the "Quick Summary" section at the bottom.

---

## 目录

- [快速概览](#快速概览)
- [双仓同步规则（最重要）](#双仓同步规则最重要)
- [开发环境准备](#开发环境准备)
- [分支与提交规范](#分支与提交规范)
- [Pull Request 流程](#pull-request-流程)
- [Issue 规范](#issue-规范)
- [代码风格](#代码风格)
- [测试与校验](#测试与校验)
- [文档要求](#文档要求)
- [当前仓库的已知技术债](#当前仓库的已知技术债)
- [行为准则](#行为准则)
- [安全漏洞](#安全漏洞)

---

## 快速概览

| 项 | 值 |
| --- | --- |
| 主分支 | `main` |
| 许可 | Apache License 2.0（见 [LICENSE](LICENSE)） |
| 最低 Python | `>= 3.10` |
| 唯一运行依赖 | `PySide6 >= 6.6` |
| 关联仓库 | [`sciforge`](https://github.com/liudongyan13701205717-source/sciforge)（MCP 服务器版） |

---

## 双仓同步规则（最重要）

sciforge 以两个仓库交付，二者的**核心逻辑应当保持一致**。

| 仓库 | 职责 |
| --- | --- |
| `sciforge` | MCP 服务器：学科 registry、论文工具、数据库连接器 |
| `sciforge-desktop`（本仓） | 桌面客户端：界面、本地会话、本地工具、MCP 客户端通道 |

### 默认规则

> **除非你的改动明确只涉及桌面表现层，否则核心逻辑改动必须在两个仓库各提交一个 PR。**

### 判定表

| 改动类型 | 提交范围 | 理由 |
| --- | --- | --- |
| 学科 registry 条目、论文工具逻辑、连接器 | **两仓** | 核心逻辑，属 MCP 版职责；桌面端通过协议消费 |
| `core/` 共享核心 | **两仓** | 共享层本身 |
| 学科计数、常量、枚举口径 | **两仓** | 任一仓单独改会造成文档与实现不符 |
| 界面布局、样式、交互 | 仅桌面仓 | 表现层 |
| 本地会话存储 | 仅桌面仓 | 桌面端本地关注点 |
| 本地 agent 工具（`agent/`） | 仅桌面仓 | 仅存在于桌面端 |
| MCP 客户端桥接（`api/`） | 仅桌面仓 | 仅存在于桌面端 |
| CI、文档、依赖升级 | 视情况 | 依赖升级通常两仓都要做，但可分开提 PR，需在 PR 描述中说明 |

### 跨仓 PR 的写法

1. 先在 `sciforge` 提 PR 并写明「本改动需同步至 sciforge-desktop」；
2. 再在 `sciforge-desktop` 提 PR，描述中链接前一个 PR；
3. 两个 PR 尽量使用相同的分支名与改动描述，便于对照 review。

### 当前现实（请注意）

截至 2026-09-26 的代码核对，本仓库 `core/` 仅为 3 行 docstring 的空占位，`pyproject.toml` 也未声明对 `sci-forge` 的依赖 —— 两仓目前**零共享代码、零同步机制**。上述规则描述的是目标形态与协作约定，落地路径见 [`docs/desktop-core-relationship.md`](docs/desktop-core-relationship.md)。

---

## 开发环境准备

### 1. 克隆

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge-desktop.git
cd sciforge-desktop
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. 安装

```bash
pip install -e .
```

### 4. PySide6 与 Python 版本的兼容性（重要）

**2026-09-26 当次实测**：参考机器上的 Python 为 `3.14.6`，该版本在 PyPI 上没有对应的 PySide6 wheel，`pip install PySide6` 会失败。

这属于会随上游版本推进而变化的环境事实，不是永久结论。可行做法：

- 选用 PySide6 已有 wheel 的 Python 版本（2026-09-26 时点下 3.10 – 3.13 区间为可选项）；
- 或只开发不依赖 PySide6 的部分：`cli/`、`agent/`、`sessions/`、`api/` 四个包在运行时完全不 import PySide6。

`gui/main_window.py` 采用懒加载，模块顶层不 import PySide6，因此无 PySide6 环境下仍可安全 import 该模块做静态检查。

### 5. 关联 MCP 服务器（可选）

若要调试 MCP 桥接，需先安装 `sciforge`：

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge.git
cd sciforge && pip install -e .
```

其控制台入口为 `sci-forge`（等价于 `python -m sciforge`）。

---

## 分支与提交规范

### 分支命名

| 类型 | 格式 | 示例 |
| --- | --- | --- |
| 功能 | `feat/<简短描述>` | `feat/session-list-panel` |
| 修复 | `fix/<简短描述>` | `fix/entry-point-prefix` |
| 文档 | `docs/<简短描述>` | `docs/installation-guide` |
| 重构 | `refactor/<简短描述>` | `refactor/agent-tool-registry` |
| 杂项 | `chore/<简短描述>` | `chore/bump-pyside6` |

### 提交信息

采用 Conventional Commits 前缀：

```
feat: 增加会话列表面板
fix: 修正 session_id 路径穿越校验
docs: 补充 MCP 桥接握手说明
refactor: 抽取路径沙箱校验为独立函数
chore: 升级 PySide6 至 6.7
test: 为 session_store 补充 CRUD 用例
ci: 为 GUI 测试添加无头条件跳过
```

约定：

- 标题行使用中文或英文均可，但同一 PR 内保持一致；
- 标题行末尾不加句号；
- 正文（若需要）说明**为什么**改，而非复述 diff。

---

## Pull Request 流程

1. **先开 Issue**：较大的改动请先开 Issue 讨论，避免白做。
2. **从最新 `main` 切分支**。
3. **保持 PR 聚焦**：一个 PR 一件事。跨仓同步的两个 PR 各自独立。
4. **补齐描述**：使用 [`.github/pull_request_template.md`](.github/pull_request_template.md) 模板。
5. **自查清单**（合并前逐项确认）：

   - [ ] 代码可正常 import（无 PySide6 环境下也应验证 `cli` / `agent` / `sessions` / `api`）
   - [ ] 未引入新的第三方依赖（若引入，在 PR 中说明理由）
   - [ ] 新增行为在 README / `docs/` 中有对应说明
   - [ ] 破坏性变更在 `CHANGELOG.md` 的 `Unreleased` 段落中标注
   - [ ] 涉及核心逻辑的改动已同步提交 `sciforge` 仓 PR（并链接）

6. **CI 通过后请求 review**。

---

## Issue 规范

提交前请搜索是否已有同类 Issue。Issue 模板：

| 模板 | 何时使用 |
| --- | --- |
| [bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md) | 报告可复现的错误 |
| [feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md) | 提出新功能或改进 |

Issue 支持渠道与安全漏洞例外见 [`.github/SUPPORT.md`](.github/SUPPORT.md)。

---

## 代码风格

### 现状

本仓库目前**没有** 统一的 lint / 格式化工具配置（无 `[tool.ruff]`、无 `[tool.black]`、无 `[tool.mypy]`、无 `[tool.coverage]`）。因此以下约定来自现有代码的实际风格，请照此书写。

### 约定

| 项 | 约定 |
| --- | --- |
| 行宽 | 约 88 字符（现有代码的实际取值） |
| 类型注解 | 模块级函数与类方法**必须**带完整注解；使用 `from __future__ import annotations` |
| docstring | 公开模块、类、函数**必须**有中文 docstring；格式为一行摘要 + 空行 + 说明 + `Args:` / `Returns:` / `Raises:` 段 |
| 命名 | 模块与函数 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE` |
| 私有成员 | 前缀单下划线（如 `_safe_path`、`_OFFLINE`） |
| 导入 | 仅标准库；分组顺序为 `__future__` → 标准库 → 第三方 → 本地，空行分隔 |
| 异常处理 | 捕获具体异常类型，禁止裸 `except:` |
| 依赖 | 运行时只允许 `PySide6`；其余能力用标准库实现 |

### 示例（docstring 风格）

```python
def load_session(session_id: str) -> dict[str, Any] | None:
    """按 id 加载会话；不存在或文件损坏时返回 None。

    Raises:
        ValueError: session_id 非法（含路径穿越尝试）。
    """
```

---

## 测试与校验

### 现状（2026-09-26 实测）

本仓库**当前 0 个测试用例**，无 `tests/` 目录，无 pytest 配置，无 dev extras。这是需要补齐的基建。

### 现阶段可用的校验

```bash
# 语法检查（不需要 PySide6）
python -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"

# 无 PySide6 环境下的 import 冒烟
python -c "import cli.main, agent.tools, sessions.session_store, api.mcp_client, gui.main_window; print('IMPORT OK')"
```

### 建议

新增功能请尽量带上测试。若 PR 中新增了 `tests/`，请同时在 `pyproject.toml` 中补上 `[tool.pytest.ini_options]`（例如 `testpaths = ["tests"]`）与 dev extras（`pytest>=8.0`），否则 CI 无法发现这些用例。

### 离线测试

涉及 `web_search` 的测试请设置环境变量：

```bash
SCI_FORGE_OFFLINE=1 python -m pytest
```

注意 `agent/tools.py` 在**模块导入时**读取该变量，因此在测试进程中设置环境变量需早于首次 import。

---

## 文档要求

- 面向用户的说明放 `docs/`，根目录 `README.md` 保持概览与入口；
- 涉及 GUI 截图或布局变化时，同步更新 README 的「界面导览」；
- 涉及环境变量、Python 版本、依赖变化时，同步更新 `docs/installation.md`；
- 修复缺陷时，在 `CHANGELOG.md` 的 `Unreleased` 段落记录；
- 一切会随时间变化的观测（依赖可用性、版本兼容性、计数）**必须标注观测日期**，并用条件式表述，不得写成永久性断言。

---

## 当前仓库的已知技术债

以下是 2026-09-26 代码核对得到的待修复项，欢迎认领：

| # | 问题 | 位置 |
| --- | --- | --- |
| 1 | entry point 缺包前缀，安装后可能无法导入 | `pyproject.toml` |
| 2 | 缺 `authors` / `urls` / `keywords` / `classifiers` | `pyproject.toml` |
| 3 | 无 ruff / mypy / coverage 配置 | `pyproject.toml` |
| 4 | 0 测试、无 pytest 配置 | 全仓 |
| 5 | `web_search` 返回契约与同模块其余工具不一致 | `agent/tools.py` |
| 6 | `cli tools` 不暴露函数签名 | `cli/main.py` |
| 7 | `MCPClient` 无调用方 | `api/mcp_client.py` |
| 8 | `cli serve` 为占位 | `cli/main.py` |
| 9 | 界面导航项与「关于」动作未连接槽 | `gui/main_window.py` |
| 10 | `core/` 为空占位，两仓无同步机制 | `core/__init__.py` |

---

## 行为准则

参与本项目即表示同意遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)（Contributor Covenant v2.1）。不可接受的行为可通过 Issue 或 [`SECURITY.md`](SECURITY.md) 中的渠道报告。

---

## 安全漏洞

**请勿通过公开 Issue 报告安全漏洞。** 报告流程见 [SECURITY.md](SECURITY.md)。

---

## Quick Summary (English)

- **Two-repo sync rule**: core-logic changes must be submitted to **both** `sciforge` and `sciforge-desktop`. Desktop-only PRs are for presentation-layer changes (UI, interaction, local sessions).
- **Setup**: `pip install -e .` in a virtual environment. As measured on 2026-09-26, PySide6 has no wheel for Python 3.14; either pick a Python version with a PySide6 wheel or work on the four PySide6-free packages (`cli`, `agent`, `sessions`, `api`).
- **Branches**: `feat/` `fix/` `docs/` `refactor/` `chore/` prefixes, Conventional Commits messages.
- **Checks today**: AST syntax pass plus an import smoke test. The repo has no test suite yet — new tests should come with pytest config and dev extras.
- **Docs**: user-facing material goes in `docs/`; date-stamp any observation that changes over time.
