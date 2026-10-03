# 桌面版核心与 MCP 版的关系

本文说明 `sciforge-desktop`（桌面客户端）与 `sciforge`（MCP 服务器）的关系、当前同步现状，以及核心层同步的目标形态。

> 状态依据 2026-09-26 对两仓的逐文件核对。本文的「现状」部分是快照，会随开发推进变化；「目标」部分是设计意图，尚未实现。

---

## 摘要

| 问题 | 答案 |
| --- | --- |
| 两仓是同一个项目吗？ | 不是。是**同一产品的两个形态**，分属两个 Git 仓库。 |
| 有代码共享吗？ | **没有。** 两仓 `core/` 无任何共享代码，无同步机制。 |
| 本仓 `core/` 里有东西吗？ | **没有。** 只有 3 行 docstring，是空占位。 |
| 有依赖关系吗？ | 没有。本仓 `pyproject.toml` 未声明对 `sciforge` 的依赖。 |
| 桌面版能调用 MCP 工具吗？ | 桥接类已实现，但**本仓无调用方**，界面上不可用。 |
| 学科、论文工具、连接器在哪？ | 全在 `sciforge` 仓，本仓没有。 |

---

## 两个仓库

| 维度 | `sciforge-desktop`（本仓） | `sciforge` |
| --- | --- | --- |
| 角色 | MCP 客户端 / 桌面外壳 | MCP 服务器 / 能力实现方 |
| 包名 | `sciforge-desktop` | `sciforge` |
| 版本 | `0.1.0` | 见其 `pyproject.toml` |
| 控制台入口 | `sciforge-desktop`（**缺包前缀，暂不可用**） | `sci-forge`（= `python -m sciforge`） |
| 许可证 | Apache-2.0 | MIT |
| 依赖声明 | `PySide6 >= 6.6` | 本文档未核对 |
| 学科数 | 0 | 261 |
| MCP 工具数 | 0（`agent/tools.py` 的 6 个是**本地**工具，非 MCP 工具） | 65 |
| 数据库连接器 | 0 | 46 |

**许可证不同**是合规上的要点：本仓 Apache-2.0，`sciforge` MIT。若未来把 `sciforge` 代码复制进本仓（而非通过 MCP 调用），需按 Apache-2.0 要求处理版权与声明（保留原 MIT 声明、标注修改、提供 NOTICE）。**通过 MCP 协议调用不属于复制**，无此义务。

---

## 依赖关系

```
sciforge-desktop                    sciforge
├── cli/main.py                     ├── sciforge/cli.py
│    (serve 占位)                   │    (控制台入口 sci-forge)
├── api/mcp_client.py ─── stdio ──▶ │    (stdio MCP 服务器)
│    (JSON-RPC 2.0 客户端)          ├── sciforge/core/
├── sessions/session_store.py       │    (364 行，真实实现)
├── agent/tools.py                  ├── 学科 registry (261)
│    (6 个本地工具，不经 MCP)        ├── MCP 工具 (65)
├── gui/main_window.py              └── 数据库连接器 (46)
└── core/__init__.py
     (3 行 docstring，空占位)
```

箭头是**运行时的进程间通信**，不是 Python import。

**关键澄清**：

1. `sciforge-desktop` **不 import** `sciforge`。两者在 Python 层面互不知晓。
2. 本仓 `pyproject.toml` 没有 `dependencies = ["sciforge"]` 之类的声明。
3. `sciforge` 也不依赖本仓。
4. 若要使用桥接层，需**分别安装两个仓库**（见 [installation.md](installation.md) 的「关联 MCP 服务器」）。

---

## `core/` 同步现状

### 观测到的事实

| 项 | `sciforge/core` | `sciforge-desktop/core` |
| --- | --- | --- |
| 文件数 | 有真实实现，约 364 行 | 仅 `__init__.py` |
| `__init__.py` 内容 | 导出实际符号 | 3 行 docstring |
| 可执行代码 | 有 | **无** |

本仓 `core/__init__.py` 的全部内容是一个声明性 docstring，意思是「核心同步是后续任务」。

### 这意味着什么

1. **本仓当前没有任何共享业务逻辑。** 所有逻辑要么在 `cli` / `agent` / `sessions` / `api` / `gui` 中重复实现，要么根本不存在。
2. **本仓的 `core/` 不可 import 出任何能力。**

```bash
python -c "
import core
print([n for n in dir(core) if not n.startswith('_')])
"
```

预期为空列表（除 dunder 之外没有可导出符号）。

3. **本仓文档中所有「学科」「论文工具」「连接器」相关的表述都是对 `sciforge` 仓的引用**，不是本仓的功能。本仓 README 与本文件都不应把它们写成本仓能力。

### 尚未建立的机制

同步 `core/` 需要以下机制，**目前一个都没有**：

| 需要的机制 | 现状 |
| --- | --- |
| 双仓 PR 联动（改动一个仓时提醒改另一个） | 无 |
| 版本一致性检查 | 无 |
| `core/` 内容一致性校验（CI 或脚本） | 无 |
| 依赖声明（`install_requires` 引用 `sciforge`） | 无 |
| 共享发布流程 | 无 |

`.github/dependabot.yml` 与 `.github/workflows/ci.yml` 已在注释中提示「涉及核心逻辑需同步双仓」，但**这是人工流程约定，不是自动化保障**。

---

## 目标形态

以下是设计意图，**尚未实现**。写在这里是为了让后续贡献者知道方向，以及避免误读现状。

### 目标 1：`core/` 承载共享逻辑

学科 registry、工具元数据、数据库连接器定义等**与形态无关**的逻辑应收敛到 `core/`，两仓各自消费。

```
sciforge/core/          ← 单一事实来源
sciforge-desktop/core/  ← 同步副本，或改为对 sciforge.core 的依赖
```

### 目标 2：依赖方向明确

两种可行方向：

| 方案 | 做法 | 代价 |
| --- | --- | --- |
| A. 桌面端依赖 MCP 版 | `sciforge-desktop` 声明 `dependencies = ["sciforge==x.y.z"]`，直接 import `sciforge.core` | 破坏 stdio 解耦；两个 pip 包强绑定，版本需严格对齐 |
| B. 保持进程隔离 + 同步副本 | 桌面端不 import MCP 版，`core/` 内容在两仓各存一份，靠流程/脚本保证一致 | 存在副本漂移风险，需要一致性校验机制兜底 |

**当前无法判断最终采用哪种** —— 决策尚未做出。

### 目标 3：核心层变化需要回归保障

一旦 `core/` 承载真实逻辑，本仓当前的「0 个测试」就不可接受了。最低要求：

- `core/` 有单元测试；
- CI 中加入 `core/` 一致性校验（若采用方案 B）；
- 双仓版本号联动检查。

---

## 本仓的分工

`sciforge-desktop` 该做什么（**已在做**）：

| 模块 | 职责 |
| --- | --- |
| `gui/` | 桌面界面：导航、面板、交互 |
| `cli/` | 命令行入口；`serve` 待落地为真正的客户端入口 |
| `api/mcp_client.py` | MCP 客户端：协议、握手、子进程生命周期 |
| `sessions/` | 本地会话存储 |
| `agent/tools.py` | **本地**工具（文件、搜索），不经 MCP |

`sciforge-desktop` 不该做什么：

| 不该做 | 原因 | 实际在哪 |
| --- | --- | --- |
| 实现学科 registry | 属于能力实现方 | `sciforge` |
| 实现论文检索工具 | 同上 | `sciforge` |
| 实现数据库连接器 | 同上 | `sciforge` |
| 复制 `sciforge` 的业务代码 | 许可证与维护成本 | — |

**注意区分**：`agent/tools.py` 的 6 个工具是**本地标准库实现**（文件读写、目录、DuckDuckGo 搜索），与 `sciforge` 的 65 个 MCP 工具**没有重叠，也不是同一套东西**。本地工具不经 MCP 协议。

---

## 改动的双仓影响

提交代码前先判断是否触及核心逻辑：

| 改动位置 | 是否需同步 `sciforge` |
| --- | --- |
| `gui/`、`cli/` | 否 |
| `sessions/` | 否 |
| `agent/tools.py`（本地工具） | 否 |
| `api/mcp_client.py`（客户端协议） | 通常否（除非协议版本变更） |
| `core/` | **是** |
| 学科 / 论文工具 / 连接器 | **是** |
| `pyproject.toml` 版本号 | **视情况**（若两仓版本需对齐） |

PR 模板与 Issue 模板都要求填写这一项。规则详见 [CONTRIBUTING.md](../CONTRIBUTING.md)。

---

## 常见误解

| 误解 | 事实 |
| --- | --- |
| 「桌面版有 261 门学科」 | 没有。学科 registry 在 `sciforge` 仓。 |
| 「桌面版有 65 个 MCP 工具」 | 没有。本仓的 6 个是本地工具，不经 MCP。 |
| 「两仓共享 `core/`」 | 不共享。本仓 `core/` 是空占位。 |
| 「`pip install sciforge-desktop` 后 `sciforge-desktop` 命令可用」 | 2026-09-26 实测很可能不可用：entry point 缺包前缀。用 `python -m cli.main`。 |
| 「界面上可以搜索论文」 | 不可以。界面导航未连接槽，桥接层无调用方。 |
| 「`cli serve` 能启动服务」 | 不能。它只打印提示。 |

---

## 下一步

- 安装并启动 `sciforge`：[installation.md](installation.md) 的「关联 MCP 服务器」
- 桥接层用法与协议细节：[mcp-bridge.md](mcp-bridge.md)
- 贡献流程与双仓规则：[CONTRIBUTING.md](../CONTRIBUTING.md)
