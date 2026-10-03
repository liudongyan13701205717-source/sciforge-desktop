# sciforge-desktop

> The **desktop client** for the sciforge project. The other form of the same project is an MCP server for AI agents, hosted in the [`sci-forge`](https://github.com/liudongyan13701205717-source/sci-forge) repository.
>
> 中文版：[README.md](README.md)

---

## Table of Contents

- [Positioning](#positioning)
- [Current Status — Read This First](#current-status--read-this-first)
- [Repository Layout](#repository-layout)
- [Installation](#installation)
- [GUI Tour](#gui-tour)
- [Command Line](#command-line)
- [Local Agent Tools](#local-agent-tools)
- [Relationship to the MCP Build](#relationship-to-the-mcp-build)
- [Where Disciplines and Tool Capabilities Come From](#where-disciplines-and-tool-capabilities-come-from)
- [Local Session Storage](#local-session-storage)
- [Offline Mode](#offline-mode)
- [Known Defects and Open Issues](#known-defects-and-open-issues)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Positioning

sciforge targets the full research workflow — topic selection, literature review, reproduction, writing, and submission — and ships in two forms:

| Form | Repository | Audience | Interaction |
| --- | --- | --- | --- |
| MCP server | `sci-forge` | AI agents / LLM clients | JSON-RPC 2.0 over stdio |
| Desktop client | `sciforge-desktop` (this repo) | Human researchers | PySide6 GUI |

This repository owns the layer meant for humans: the graphical interface, local session management, local file and search tools, and the client side of the bridge to the MCP server.

**This repository does not provide an MCP service and does not embed a discipline knowledge base.** The discipline registry, paper tooling, and database connectors all live in the `sci-forge` repository and are meant to be reached from this GUI over the MCP protocol.

---

## Current Status — Read This First

This repository is at **skeleton stage**. To avoid over-estimating what is here, each part is classified below.

### Working today

| Capability | Location | Notes |
| --- | --- | --- |
| CLI entry point | `cli/main.py` | The `sessions` and `tools` subcommands work |
| Local session CRUD | `sessions/session_store.py` | Create / list / read / overwrite / delete, backed by JSON files |
| Local agent tools | `agent/tools.py` | 6 standard-library-only tools with a path sandbox and an offline switch |
| MCP client bridge | `api/mcp_client.py` | `MCPClient`: spawn subprocess, handshake, call tools, receive notifications, shut down |
| GUI shell | `gui/main_window.py` | Main window renders: menu bar, status bar, left navigation, central placeholder |

### Not implemented yet

| Item | Status |
| --- | --- |
| `core/` shared core | **A 3-line docstring stub** with no executable code; the source repo's core has not been projected in yet |
| Cross-repo core sync | The sync script **is in place** (`scripts/sync_core.py`, byte-identical to the same-named file in the source repo), but the **first `--apply` has not been run** — mechanism built, projection not landed. See `docs/architecture/core-sync.md` |
| `cli serve` subcommand | Placeholder — it only prints `serve 子命令尚未实现（占位）` |
| GUI functionality | The three left-nav entries (会话 / 工具 / 设置) have **no slots connected**; the centre shows a placeholder label `sciforge 桌面客户端骨架 — 功能开发中`; Help → About is not wired to anything |
| Agent main loop | Does not exist. **No code path in this repository calls `MCPClient.call_tool`** — `MCPClient` is implemented but has no caller here |
| Model / LLM integration | Does not exist |
| Packaging and distribution | No PyInstaller or Qt deployment script; `gui/main_window.py:main()` is not registered as an entry point |
| Tests | **Zero test cases**, no `tests/` directory, no pytest configuration |

> The status above comes from a file-by-file review of the repository code on 2026-09-26. Every figure in this document labelled "measured" carries its observation date, because the code is still moving.

---

## Repository Layout

```
sciforge-desktop/
├── agent/                  # Local agent tools (standard library only)
│   └── tools.py            #   6 tools + path sandbox + offline switch
├── api/                    # Talking to the MCP server
│   └── mcp_client.py       #   JSON-RPC 2.0 over stdio client
├── cli/                    # Command line entry point
│   └── main.py             #   serve (placeholder) / sessions / tools
├── core/                   # Shared core package — currently an empty stub
│   └── __init__.py         #   docstring only, no code
├── gui/                    # PySide6 graphical interface
│   └── main_window.py      #   lazily loaded MainWindow
├── sessions/               # Local session storage
│   └── session_store.py    #   JSON file CRUD, two-layer path-traversal guard
├── docs/                   # Documentation suite
└── pyproject.toml
```

Six flat top-level packages: `agent` / `api` / `cli` / `core` / `gui` / `sessions`. Note that these are top-level package names, not subpackages under a `sciforge_desktop.*` namespace.

---

## Installation

### Requirements

- Python `>= 3.10` (see the known limitation below)
- Sole runtime dependency: `PySide6 >= 6.6`

### Install from source

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge-desktop.git
cd sciforge-desktop
pip install -e .
```

### Known limitation: PySide6 and Python 3.14

**Measured on 2026-09-26**: the Python available on the reference machine is `3.14.6` (`C:/Python314/python.exe`), for which no PySide6 wheel exists on PyPI, so `pip install PySide6` cannot complete.

This is not a permanent verdict — PySide6's wheel coverage moves forward with upstream releases. Options as of that observation:

1. Use a Python version for which PySide6 does ship a wheel (the 3.10 – 3.13 range was viable at that point) and install into a virtual environment;
2. Use the CLI only — `cli/`, `agent/`, `sessions/`, and `api/` have **no PySide6 dependency at all**;
3. `gui/main_window.py` uses **lazy loading**: the module top level does not `import PySide6`, and the real `QMainWindow` subclass is built only on first instantiation. The module can therefore be safely `import`ed on a machine without PySide6 — only `MainWindow()` instantiation or `main()` will fail.

---

## GUI Tour

Launch (requires PySide6 installed):

```bash
python -m gui.main_window
# or (currently broken — see Known Defect #1)
sciforge-desktop
```

The main window defaults to 960 × 640 and uses a two-pane `QSplitter` layout:

```
┌──────────────────────────────────────────────────────────┐
│ 文件(&F)  帮助(&H)                                        │
├────────────┬─────────────────────────────────────────────┤
│  会话       │                                             │
│  工具       │   sciforge 桌面客户端骨架 — 功能开发中        │
│  设置       │   (centred placeholder label)               │
│            │                                             │
├────────────┴─────────────────────────────────────────────┤
│ 状态栏：就绪                                               │
└──────────────────────────────────────────────────────────┘
```

| Region | Status |
| --- | --- |
| Menu → 文件 | 「退出(&Q)」 closes the window (**wired**) |
| Menu → 帮助 | 「关于(&A)」 — **no slot connected**, clicking does nothing |
| Left navigation | Fixed three entries: 会话 / 工具 / 设置, **none wired**, clicking does not switch views |
| Centre panel | A single centred `QLabel` placeholder, **no real content** |
| Status bar | Always shows 「就绪」, with no dynamic updates |

---

## Command Line

```
sciforge-desktop serve      # Start the local service — placeholder, prints a notice
sciforge-desktop sessions   # List local sessions (works)
sciforge-desktop tools      # List the local agent tools (works)
```

`main()` takes an optional `argv` sequence and returns a process exit code, so it can be called directly from Python:

```python
from cli.main import main
raise SystemExit(main(["tools"]))
```

> **Known defect**: `pyproject.toml` declares the entry point as `sciforge-desktop = "cli.main:main"`, which is missing the package qualifier. Under the current package layout that entry point will most likely fail to import after installation, so the `sciforge-desktop ...` commands above may not be available following `pip install`. Until this is fixed, use `python -m cli.main tools` or import `main` from `cli.main` directly. See [Known Defects](#known-defects-and-open-issues).

`sessions` prints `session_id<TAB>name<TAB>created_at` (ISO 8601, UTC). `tools` prints `tool_name<TAB>first docstring line` — it currently prints only the first docstring line and **does not expose the function signature**.

---

## Local Agent Tools

`agent/tools.py` provides 6 tools, all implemented with the Python standard library (no third-party dependency):

| Tool | Signature | Behaviour |
| --- | --- | --- |
| `web_search` | `(query, limit=5) -> list[dict]` | Queries the DuckDuckGo HTML endpoint and parses result titles and links with a built-in `HTMLParser`; returns `[]` when offline or on network error |
| `read_file` | `(path) -> dict` | Reads a UTF-8 text file |
| `write_file` | `(path, content) -> dict` | Writes UTF-8 text, creating parent directories as needed |
| `list_files` | `(path) -> dict` | Lists directory entry names, sorted |
| `make_dir` | `(path) -> dict` | Creates a directory recursively |
| `delete_file` | `(path) -> dict` | Deletes a single file (never a directory) |

**Return contract**: `read_file` / `write_file` / `list_files` / `make_dir` / `delete_file` all return `{"ok": True, "result": ...}` or `{"ok": False, "error": str}`. `web_search` is the exception and returns a bare `list[dict]` — that inconsistency is a known issue.

**Path sandbox**: every file tool validates through `_safe_path()` first. The permitted roots are `Path.home()` and `Path.cwd()`. Validation resolves the path and then checks whether it equals a root or sits inside that root's `parents`, so `..` traversal is rejected with a `PermissionError`, which each tool catches and converts into `{"ok": False, "error": ...}`.

**Offline switch**: `_OFFLINE = os.environ.get("SCI_FORGE_OFFLINE") == "1"`, read **once at module import time**. Changing the environment variable at runtime has no effect; set it before the process starts or re-import the module.

---

## Relationship to the MCP Build

```
┌──────────────────────────┐        MCP (JSON-RPC 2.0 / stdio)       ┌──────────────────────────┐
│  sciforge-desktop        │  ───────────────────────────────────▶   │  sciforge (MCP server)   │
│  ├─ gui/    PySide6 UI    │   api/mcp_client.py : MCPClient         │  ├─ disciplines/ 261     │
│  ├─ agent/  6 local tools │   protocolVersion "2024-11-05"         │  ├─ research/ writing    │
│  ├─ sessions/ local store │                                         │  ├─ science/ 46 connectors│
│  └─ core/  empty stub     │  ◀───────────────────────────────────  │  └─ server.py 65 tools   │
└──────────────────────────┘        responses / notifications        └──────────────────────────┘
```

`api/mcp_client.py` implements the following `MCPClient` methods:

| Method | Purpose |
| --- | --- |
| `start(server_cmd)` | Launches the server subprocess with `subprocess.Popen` and starts a daemon reader thread |
| `initialize()` | Sends the `initialize` request (client identity `{"name": "sciforge-desktop", "version": "0.1.0"}`), then automatically sends `notifications/initialized` |
| `call_tool(name, arguments)` | Sends a `tools/call` request and blocks until the matching-id response arrives |
| `notify(method, params)` | Sends an id-less notification without waiting for a response |
| `notifications()` | Generator that blocks while yielding server-pushed notifications |
| `close()` | Calls `terminate()`, escalating to `kill()` if the process does not exit within 5 seconds |

The wire format is JSON-RPC 2.0, one message per line. The protocol version constant is `_PROTOCOL_VERSION = "2024-11-05"`.

**This bridge currently has no caller inside the repository** — the GUI is not wired up yet; that work is in progress.

---

## Where Disciplines and Tool Capabilities Come From

**This repository contains no discipline knowledge base and exposes no MCP tools.** Discipline and tool capabilities belong to the `sci-forge` repository:

| Capability | Count | Repository |
| --- | --- | --- |
| Discipline modules / registry entries | 261, spanning 14 categories | `sci-forge` |
| MCP tools | 65 (3 of which are compatibility aliases; 61 have distinct behaviour) | `sci-forge` |
| MCP resources | 1 static resource + 1 parameterised template | `sci-forge` |
| Scientific database connectors | 46, across 7 domains | `sci-forge` |
| Local agent tools | 6 | `sciforge-desktop` (this repo) |
| Discipline modules | 0 | `sciforge-desktop` (this repo) |

> The counts above were measured against the `sci-forge` repository on 2026-09-26 and will change as that repository evolves. Note that the discipline entry count (261) and the number of `.py` files under `disciplines/` (264, measured 2026-09-26) are different metrics — do not conflate them.

The design intent is that the desktop side does not reimplement discipline logic but consumes the capabilities exposed by `sci-forge` over MCP, so the same discipline configuration is never maintained in two places. That intent has not yet landed at the code level (`core/` is an empty stub) — see `docs/desktop-core-relationship.md`.

---

## Local Session Storage

`sessions/session_store.py` exposes 5 public functions:

```python
from sessions.session_store import (
    create_session,   # (name) -> session_id
    list_sessions,    # () -> list[{session_id, name, created_at}]
    load_session,     # (session_id) -> dict | None
    save_session,     # (session_id, data) -> None, overwrites
    delete_session,   # (session_id) -> bool
)
```

- Storage location: `~/.sciforge-desktop/sessions/{uuid4().hex}.json`
- File shape: `{"session_id", "name", "created_at", "data"}`, UTF-8, `ensure_ascii=False`, indent 2
- `created_at` is `datetime.now(timezone.utc).isoformat()`
- `list_sessions()` returns metadata only, never `data`; corrupt files or files missing `session_id` are skipped silently

**Two-layer path-traversal guard**: `_session_path()` first applies a character allowlist (non-empty, every character in `[0-9a-fA-F-]`), then a fallback check that the resolved path is still inside the sessions directory. Either failure raises `ValueError`.

---

## Offline Mode

Set the environment variable `SCI_FORGE_OFFLINE=1` to enter offline mode: `web_search` returns an empty list immediately and issues no network request.

```bash
# Linux / macOS
SCI_FORGE_OFFLINE=1 python -m cli.main tools

# Windows PowerShell
$env:SCI_FORGE_OFFLINE = "1"; python -m cli.main tools
```

The other 5 tools are local file operations and involve no network. Tools in the `sci-forge` repository honour the same variable.

---

## Known Defects and Open Issues

The following were identified from a review of the code and configuration on 2026-09-26. All are **open**:

1. **Entry point is missing its package qualifier.** `pyproject.toml` declares `sciforge-desktop = "cli.main:main"` while the package declaration lists six flat top-level packages: `cli*` / `core*` / `api*` / `sessions*` / `agent*` / `gui*`. That form will most likely fail to import after installation. Fix direction: use a fully importable path (for example `sciforge_desktop.cli.main:main` with a matching package layout change), or switch to an in-package relative entry.
2. **Incomplete packaging metadata.** `pyproject.toml` has no `authors` / `maintainers` / `urls` / `keywords` / `classifiers` fields. The `sci-forge` repository is missing the same fields.
3. **No lint / typing / coverage configuration.** There is no `[tool.ruff]`, no `[tool.mypy]`, and no `[tool.coverage]`.
4. **No test infrastructure.** Zero test files, no `[tool.pytest.ini_options]`, no `[project.optional-dependencies]`. The only available check today is an AST syntax pass:

   ```bash
   python -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"
   ```

5. **`web_search` return contract is inconsistent.** It returns a bare `list[dict]` where the other 5 tools in the same module return `{"ok": ...}`.
6. **`cli tools` does not expose signatures.** It prints only the first docstring line.
7. **`MCPClient` has no caller.** Its lifecycle is not bound to the GUI.
8. **No PySide6 wheel for Python 3.14.** See [Installation](#installation); this is an environment limitation, not a code defect.

---

## Documentation

| Document | Contents |
| --- | --- |
| [`docs/index.md`](docs/index.md) | Documentation overview and suggested reading paths |
| [`docs/installation.md`](docs/installation.md) | Installation, environment variables, PySide6 / Python version compatibility |
| [`docs/quickstart.md`](docs/quickstart.md) | Five-minute start: CLI, GUI, sessions, tools |
| [`docs/mcp-bridge.md`](docs/mcp-bridge.md) | The MCP bridge layer: protocol, handshake, message format, examples |
| [`docs/desktop-core-relationship.md`](docs/desktop-core-relationship.md) | Present state and target shape of desktop/MCP core synchronisation |
| [`docs/architecture/core-sync.md`](docs/architecture/core-sync.md) | Core-sync contract (desktop view): projection boundary, script usage, consistency criteria |

For issue routing and support channels, see [`.github/SUPPORT.md`](.github/SUPPORT.md).

---

## Contributing

Issues and pull requests are welcome. Please read these first:

- [CONTRIBUTING.md](CONTRIBUTING.md) — submission flow, environment setup, the two-repo sync rule
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — code of conduct (Contributor Covenant v2.1)
- [SECURITY.md](SECURITY.md) — vulnerability reporting process
- [CHANGELOG.md](CHANGELOG.md) — release history in Keep a Changelog format

**Two-repo sync rule**: changes to core logic land in the `sci-forge` repo **only**, then get projected one-way into this repo's `core/` by `scripts/sync_core.py --apply`. **Do not edit files inside `core/` directly** — the projection is a byte-for-byte copy, so your changes will be silently overwritten on the next sync with no conflict prompt. A desktop-only PR is appropriate only when the change is clearly confined to the presentation layer (interface, interaction, local sessions); such PRs should note "does not affect the MCP contract" in the description. See `docs/architecture/core-sync.md` and `CONTRIBUTING.md`.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).

```
Copyright 2026 liudongyan13701205717
```

The `sci-forge` (MCP build) repository also uses the **Apache License 2.0** (verified 2026-09-26), which matches this one — so there is no licence conflict when the two are combined. Both repos carry the same `Copyright 2026 liudongyan13701205717` notice.
