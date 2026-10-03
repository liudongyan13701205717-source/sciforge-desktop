# sciforge-desktop

> sciforge 项目的**桌面客户端**。同一项目的另一种形态是面向 agent 的 MCP 服务器（[`sci-forge`](https://github.com/liudongyan13701205717-source/sci-forge) 仓库）。
>
> English version: [README_EN.md](README_EN.md)

---

## 目录

- [项目定位](#项目定位)
- [当前状态（请先读这一节）](#当前状态请先读这一节)
- [仓库结构](#仓库结构)
- [安装](#安装)
- [界面导览](#界面导览)
- [命令行](#命令行)
- [本地 agent 工具](#本地-agent-工具)
- [与 MCP 版的关系](#与-mcp-版的关系)
- [学科与工具能力从哪来](#学科与工具能力从哪来)
- [本地会话存储](#本地会话存储)
- [离线模式](#离线模式)
- [已知缺陷与待修复项](#已知缺陷与待修复项)
- [文档](#文档)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

---

## 项目定位

sciforge 面向科研全流程（选题 → 文献 → 复现 → 写作 → 投稿），以两种形态交付：

| 形态 | 仓库 | 使用者 | 交互方式 |
| --- | --- | --- | --- |
| MCP 服务器 | `sci-forge` | AI agent / LLM 客户端 | JSON-RPC 2.0 over stdio |
| 桌面客户端 | `sciforge-desktop`（本仓库） | 人类研究者 | PySide6 图形界面 |

本仓库负责「人看的那一层」：图形界面、本地会话管理、本地文件与检索工具、以及与 MCP 服务器通信的客户端通道。

**本仓库不提供 MCP 服务，也不内置学科知识库。** 学科体系、论文工具、数据库连接器全部位于 `sci-forge` 仓库，通过 MCP 协议被本仓库的界面调用。

---

## 当前状态（请先读这一节）

本仓库目前处于**骨架（skeleton）阶段**。为免误解，以下逐项说明哪些能用、哪些不能用。

### 已经可用的部分

| 能力 | 位置 | 说明 |
| --- | --- | --- |
| 命令行入口 | `cli/main.py` | `sessions` 与 `tools` 两个子命令可正常使用 |
| 本地会话 CRUD | `sessions/session_store.py` | 创建 / 列出 / 读取 / 覆盖保存 / 删除，JSON 文件存储 |
| 本地 agent 工具 | `agent/tools.py` | 6 个纯标准库工具，带路径沙箱与离线开关 |
| MCP 客户端通道 | `api/mcp_client.py` | `MCPClient` 类：启动子进程、握手、调用工具、接收通知、关闭 |
| 图形界面外壳 | `gui/main_window.py` | 主窗口可显示：菜单栏、状态栏、左侧导航、中央占位区 |

### 尚未实现的部分

| 项 | 现状 |
| --- | --- |
| `core/` 共享核心 | **仅 3 行 docstring 的空占位**，无任何可执行代码；源仓核心尚未投影进来 |
| 两仓核心同步 | 同步脚本**已就位**（`scripts/sync_core.py`，与源仓同名文件逐字节一致），但**尚未执行首次 `--apply`** —— 机制已建、投影未落地。详见 `docs/architecture/core-sync.md` |
| `cli serve` 子命令 | 占位实现，只打印 `serve 子命令尚未实现（占位）` |
| 界面功能 | 左侧导航「会话 / 工具 / 设置」三项**均未连接任何槽**；中央为占位标签「sciforge 桌面客户端骨架 — 功能开发中」；「帮助 → 关于」动作未连接 |
| agent 主循环 | 不存在。本仓库**没有任何代码路径调用 `MCPClient.call_tool`** —— `MCPClient` 已实现但在本仓内无调用方 |
| 模型 / LLM 接入 | 不存在 |
| 打包分发 | 无 PyInstaller / Qt 部署脚本；`gui/main_window.py:main()` 未注册为 entry point |
| 测试 | **0 个测试用例**，无 `tests/` 目录，无 pytest 配置 |

> 以上状态依据 2026-09-26 对仓库代码的逐文件核对。文档中凡涉及「实测」的数据均标注观测日期。

---

## 仓库结构

```
sciforge-desktop/
├── agent/                  # 本地 agent 基础工具（纯标准库）
│   └── tools.py            #   6 个工具 + 路径沙箱 + 离线开关
├── api/                    # 与 MCP 服务器通信
│   └── mcp_client.py       #   JSON-RPC 2.0 over stdio 客户端
├── cli/                    # 命令行入口
│   └── main.py             #   serve（占位）/ sessions / tools
├── core/                   # 共享核心包 —— 当前为空占位
│   └── __init__.py         #   仅 docstring，无代码
├── gui/                    # PySide6 图形界面
│   └── main_window.py      #   懒加载 MainWindow
├── sessions/               # 本地会话存储
│   └── session_store.py    #   JSON 文件 CRUD，双层防路径穿越
├── scripts/                # 维护脚本
│   └── sync_core.py        #   单向核心投影 + 一致性校验（--dry-run/--apply/--check）
├── docs/                   # 文档套件
│   ├── architecture/       #   架构约定（含 core-sync.md）
│   └── *.md
└── pyproject.toml
```

6 个平铺包：`agent` / `api` / `cli` / `core` / `gui` / `sessions`。**注意**这些是顶层包名而非 `sciforge_desktop.*` 命名空间下的子包。

---

## 安装

### 前置条件

- Python `>= 3.10`（见下方已知限制）
- 唯一运行依赖：`PySide6 >= 6.6`

### 从源码安装

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge-desktop.git
cd sciforge-desktop
pip install -e .
```

### 已知限制：PySide6 与 Python 3.14

**2026-09-26 当次实测**：本机可用 Python 为 `3.14.6`（`C:/Python314/python.exe`），该版本在 PyPI 上没有对应的 PySide6 wheel，`pip install PySide6` 无法完成。

这不是永久结论 —— PySide6 的 wheel 覆盖范围会随上游版本推进变化。可选应对：

1. 使用 PySide6 已提供 wheel 的 Python 版本（3.10 – 3.13 区间在 2026-09-26 时点为可选项），并在虚拟环境中安装；
2. 只使用命令行功能 —— `cli/`、`agent/`、`sessions/`、`api/` 四个包**完全不依赖 PySide6**；
3. `gui/main_window.py` 采用**懒加载**设计：模块顶层不 `import PySide6`，真正的 `QMainWindow` 子类在首次实例化时才创建。因此在未安装 PySide6 的环境中，该模块仍可安全 `import`（只有实例化 `MainWindow()` 或调用 `main()` 时才会失败）。

---

## 界面导览

启动方式（需已安装 PySide6）：

```bash
python -m gui.main_window
# 或（当前不可用，见「已知缺陷」第 1 条）
sciforge-desktop
```

主窗口默认尺寸 960 × 640，布局为左右分栏（`QSplitter`）：

```
┌──────────────────────────────────────────────────────────┐
│ 文件(&F)  帮助(&H)                                        │
├────────────┬─────────────────────────────────────────────┤
│  会话       │                                             │
│  工具       │   sciforge 桌面客户端骨架 — 功能开发中        │
│  设置       │   （居中占位标签）                          │
│            │                                             │
├────────────┴─────────────────────────────────────────────┤
│ 状态栏：就绪                                               │
└──────────────────────────────────────────────────────────┘
```

| 区域 | 现状 |
| --- | --- |
| 菜单栏 → 文件 | 「退出(&Q)」→ 关闭窗口（**已连接**） |
| 菜单栏 → 帮助 | 「关于(&A)」→ **未连接任何槽**，点击无反应 |
| 左侧导航 | 固定三项：会话 / 工具 / 设置，**均未连接槽**，点击不切换视图 |
| 中央区域 | 单个居中 `QLabel` 占位，**无实际内容** |
| 状态栏 | 固定显示「就绪」，无动态状态更新 |

---

## 命令行

```
sciforge-desktop serve      # 启动本地服务 —— 当前为占位，仅打印提示
sciforge-desktop sessions   # 列出本地会话（可用）
sciforge-desktop tools      # 列出 agent 基础工具（可用）
```

`main()` 接受可选的 `argv` 参数并返回退出码，可从 Python 侧直接调用：

```python
from cli.main import main
raise SystemExit(main(["tools"]))
```

> **已知缺陷**：`pyproject.toml` 中 entry point 写为 `sciforge-desktop = "cli.main:main"`，缺少包限定前缀。在当前包布局下该入口在安装后**很可能无法导入**，因此上表中的 `sciforge-desktop ...` 命令在 `pip install` 后不一定可用。修复前请改用 `python -m cli.main tools` 或直接 `from cli.main import main`。详见「已知缺陷与待修复项」。

`sessions` 输出格式为 `session_id<TAB>name<TAB>created_at`（ISO 8601 UTC）。`tools` 输出格式为 `tool_name<TAB>docstring 首行` —— 当前只打印 docstring 首行，**不暴露函数签名**。

---

## 本地 agent 工具

`agent/tools.py` 提供 6 个工具，全部基于 Python 标准库实现（无第三方依赖）：

| 工具 | 签名 | 行为 |
| --- | --- | --- |
| `web_search` | `(query, limit=5) -> list[dict]` | 请求 DuckDuckGo HTML 端点，用内置 `HTMLParser` 解析结果标题与链接；离线或网络错误时返回 `[]` |
| `read_file` | `(path) -> dict` | 读取 UTF-8 文本文件 |
| `write_file` | `(path, content) -> dict` | 写入 UTF-8 文本，自动创建父目录 |
| `list_files` | `(path) -> dict` | 列出目录条目名（排序后返回） |
| `make_dir` | `(path) -> dict` | 递归创建目录 |
| `delete_file` | `(path) -> dict` | 删除单个文件（不删目录） |

**返回契约**：`read_file` / `write_file` / `list_files` / `make_dir` / `delete_file` 统一返回 `{"ok": True, "result": ...}` 或 `{"ok": False, "error": str}`。`web_search` 例外，返回裸 `list[dict]` —— 该不一致是已知问题。

**路径沙箱**：所有文件类工具先经 `_safe_path()` 校验，允许的根目录为 `Path.home()` 与 `Path.cwd()`。校验方式是 `resolve()` 后判断是否为根目录本身或位于其 `parents` 之内，因此 `..` 越界会被拒绝并抛出 `PermissionError`（被各工具捕获后转成 `{"ok": False, "error": ...}`）。

**离线开关**：`_OFFLINE = os.environ.get("SCI_FORGE_OFFLINE") == "1"`，**在模块导入时读取一次**。运行时修改环境变量不会生效，必须在进程启动前设置或重新导入模块。

---

## 与 MCP 版的关系

```
┌──────────────────────────┐        MCP (JSON-RPC 2.0 / stdio)       ┌──────────────────────────┐
│  sciforge-desktop        │  ───────────────────────────────────▶   │  sci-forge (MCP server)  │
│  ├─ gui/    PySide6 界面  │   api/mcp_client.py : MCPClient         │  ├─ disciplines/ 261 门   │
│  ├─ agent/  6 个本地工具  │   protocolVersion "2024-11-05"         │  ├─ research/ 写作与评审  │
│  ├─ sessions/ 本地会话    │                                         │  ├─ science/ 46 个连接器  │
│  └─ core/  空占位（待同步）│  ◀───────────────────────────────────  │  └─ server.py 65 个工具  │
└──────────────────────────┘        响应 / 通知                       └──────────────────────────┘
```

`api/mcp_client.py` 实现的 `MCPClient` 具备以下方法：

| 方法 | 说明 |
| --- | --- |
| `start(server_cmd)` | 以 `subprocess.Popen` 启动服务器子进程，开启守护读取线程 |
| `initialize()` | 发送 `initialize` 请求（客户端身份 `{"name": "sciforge-desktop", "version": "0.1.0"}`），成功后自动发送 `notifications/initialized` |
| `call_tool(name, arguments)` | 发送 `tools/call` 请求并等待同 id 响应 |
| `notify(method, params)` | 发送无 id 通知，不等待响应 |
| `notifications()` | 生成器，阻塞式迭代服务器推送的通知 |
| `close()` | `terminate()` 子进程，5 秒未退出则 `kill()` |

消息格式为 JSON-RPC 2.0，每行一条。协议版本常量 `_PROTOCOL_VERSION = "2024-11-05"`。

**当前该通道在本仓库内没有调用方** —— 界面尚未接入，功能开发中。

---

## 学科与工具能力从哪来

**本仓库不含任何学科知识库，也不提供 MCP 工具。** 学科与工具能力属于 `sci-forge` 仓库：

| 能力 | 数量 | 所在仓库 |
| --- | --- | --- |
| 学科模块 / registry 条目 | 261 门，覆盖 14 个门类 | `sci-forge` |
| MCP 工具 | 65 个（其中 3 个为兼容别名，有独立行为者 61 个） | `sci-forge` |
| MCP 资源 | 1 个静态资源 + 1 个参数化模板 | `sci-forge` |
| 科学数据库连接器 | 46 个，横跨 7 个领域 | `sci-forge` |
| 本地 agent 工具 | 6 个 | `sciforge-desktop`（本仓库） |
| 学科模块 | 0 | `sciforge-desktop`（本仓库） |

> 上述数量为 2026-09-26 对 `sci-forge` 仓库的实测值，随上游演进会变化。注意「学科条目数（261 门）」与 `disciplines/` 目录下的 `.py` 文件数（264 个，2026-09-26 实测）是不同口径，勿混用。

设计意图是：桌面端不重复实现学科逻辑，而是经 MCP 协议消费 `sciforge` 暴露的能力，避免两处维护同一套学科配置。目前该意图尚未在代码层落地（`core/` 为空占位），详见 `docs/desktop-core-relationship.md`。

---

## 本地会话存储

`sessions/session_store.py` 提供 5 个公开函数：

```python
from sessions.session_store import (
    create_session,   # (name) -> session_id
    list_sessions,    # () -> list[{session_id, name, created_at}]
    load_session,     # (session_id) -> dict | None
    save_session,     # (session_id, data) -> None，覆盖式写入
    delete_session,   # (session_id) -> bool
)
```

- 存储位置：`~/.sciforge-desktop/sessions/{uuid4().hex}.json`
- 文件结构：`{"session_id", "name", "created_at", "data"}`，UTF-8、`ensure_ascii=False`、缩进 2
- `created_at` 为 `datetime.now(timezone.utc).isoformat()`
- `list_sessions()` 只返回元数据，不含 `data`；损坏或缺少 `session_id` 的文件被静默跳过

**双层防路径穿越**：`_session_path()` 先做字符白名单校验（每个字符必须属于 `[0-9a-fA-F-]` 且非空），再做 `resolve()` 后的目录包含性兜底校验。任一失败抛 `ValueError`。

---

## 离线模式

设置环境变量 `SCI_FORGE_OFFLINE=1` 进入离线模式：`web_search` 直接返回空列表，不发起任何网络请求。

```bash
# Linux / macOS
SCI_FORGE_OFFLINE=1 python -m cli.main tools

# Windows PowerShell
$env:SCI_FORGE_OFFLINE = "1"; python -m cli.main tools
```

其余 5 个工具均为本地文件操作，不涉及网络。`sci-forge` 仓库的工具同样识别此变量。

---

## 已知缺陷与待修复项

以下问题依据 2026-09-26 的代码与配置核对列出，均为**待修复**状态：

1. **entry point 缺包前缀**：`pyproject.toml` 声明 `sciforge-desktop = "cli.main:main"`，而包声明为 `cli*` / `core*` / `api*` / `sessions*` / `agent*` / `gui*` 六个平铺顶层包。该写法在安装后很可能无法导入。修复方向：改为完整可导入路径（如 `sciforge_desktop.cli.main:main` 并相应调整包布局），或改用包内相对入口。
2. **打包元数据不完整**：`pyproject.toml` 缺 `authors` / `maintainers` / `urls` / `keywords` / `classifiers` 字段（`sci-forge` 仓库同样缺失）。
3. **无 lint / 类型 / 覆盖率配置**：无 `[tool.ruff]`、无 `[tool.mypy]`、无 `[tool.coverage]`。
4. **无测试基建**：0 个测试文件，无 `[tool.pytest.ini_options]`，无 `[project.optional-dependencies]`。当前唯一的校验手段是 AST 语法检查：

   ```bash
   python -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"
   ```

5. **`web_search` 返回契约不一致**：返回裸 `list[dict]`，与同模块其余 5 个工具的 `{"ok": ...}` 约定不符。
6. **`cli tools` 不暴露签名**：仅打印 docstring 首行。
7. **`MCPClient` 无调用方**：`close()` 之外未与界面生命周期绑定。
8. **PySide6 / Python 3.14 无 wheel**：见[安装](#安装)节的说明，属环境限制而非代码缺陷。

---

## 文档

| 文档 | 内容 |
| --- | --- |
| [`docs/index.md`](docs/index.md) | 文档总览与阅读路径 |
| [`docs/installation.md`](docs/installation.md) | 安装、环境变量、PySide6 / Python 版本兼容性 |
| [`docs/quickstart.md`](docs/quickstart.md) | 5 分钟上手：跑通命令行、界面、会话、工具 |
| [`docs/mcp-bridge.md`](docs/mcp-bridge.md) | MCP 桥接层：协议、握手、消息格式、示例 |
| [`docs/desktop-core-relationship.md`](docs/desktop-core-relationship.md) | 桌面版与 MCP 版的核心同步现状与目标形态 |
| [`docs/architecture/core-sync.md`](docs/architecture/core-sync.md) | 核心同步约定（桌面端视角）：投影边界、脚本用法、一致性判定 |

Issue 反馈与支持渠道见 [`.github/SUPPORT.md`](.github/SUPPORT.md)。

---

## 参与贡献

欢迎提交 Issue 与 Pull Request。请先阅读：

- [CONTRIBUTING.md](CONTRIBUTING.md) —— 提交流程、环境准备、双仓同步规则
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) —— 行为准则（Contributor Covenant v2.1）
- [SECURITY.md](SECURITY.md) —— 漏洞报告流程
- [CHANGELOG.md](CHANGELOG.md) —— 版本历史（Keep a Changelog 格式）

**双仓同步约定**：核心逻辑的改动**只在 `sci-forge` 仓提交**，然后由 `scripts/sync_core.py --apply` 单向投影到本仓 `core/`。**不要直接编辑 `core/` 内的文件** —— 投影是逐字节复制，你的修改会在下次同步时被静默覆盖，且没有任何冲突提示。仅当改动明确只涉及桌面端表现层（界面、交互、本地会话）时，才可只在桌面仓提交，此类 PR 需在描述中注明「不影响 MCP 契约」。详见 `docs/architecture/core-sync.md` 与 `CONTRIBUTING.md`。

---

## 许可证

本项目采用 [Apache License 2.0](LICENSE)。

```
Copyright 2026 liudongyan13701205717
```

`sci-forge`（MCP 版仓库）同样采用 **Apache License 2.0**（2026-09-26 核对），与本仓库**一致**，跨仓组合使用无许可证冲突。两仓的版权声明同为 `Copyright 2026 liudongyan13701205717`。
