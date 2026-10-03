# 安装

本文说明 sciforge-desktop 的安装步骤、版本兼容性与环境变量。

> 观测说明：本文中的版本兼容性与依赖可用性结论基于 **2026-09-26** 的实测。这类事实会随上游版本推进而变化，请在复现时自行确认。

---

## 环境要求

| 项 | 要求 |
| --- | --- |
| Python | `>= 3.10`（`pyproject.toml` 声明） |
| 唯一运行依赖 | `PySide6 >= 6.6` |
| 操作系统 | 未限定；依赖 PySide6 可用的平台 |
| 磁盘 | 未做统计；PySide6 含 Qt 运行时，体积较大 |

**关键区分**：本仓库的 6 个包中，有 **4 个完全不依赖 PySide6**：

| 包 | 是否需要 PySide6 | 说明 |
| --- | --- | --- |
| `cli/` | ❌ | 命令行入口 |
| `agent/` | ❌ | 6 个本地工具 |
| `sessions/` | ❌ | 本地会话存储 |
| `api/` | ❌ | MCP 客户端 |
| `gui/` | ✅ | PySide6 界面（懒加载，模块 import 不需要） |
| `core/` | ❌ | 当前为空占位 |

因此，**不装 PySide6 也能使用本仓库的命令行、会话与工具功能**。

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge-desktop.git
cd sciforge-desktop
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv .venv
```

激活：

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows cmd
.venv\Scripts\activate.bat
```

### 3. 安装

```bash
pip install -e .
```

> **已知缺陷提示**：`pyproject.toml` 声明的 console script 为 `sciforge-desktop = "cli.main:main"`，缺少包限定前缀。在当前包布局下该入口在安装后**很可能无法导入**，因此 `pip install` 可能成功但 `sciforge-desktop` 命令不可用。修复前请改用 `python -m cli.main <子命令>`（见下方「验证安装」）。详见 README 的「已知缺陷与待修复项」第 1 条。

### 4. 验证安装

```bash
# 列出本地 agent 工具（不依赖 PySide6）
python -m cli.main tools

# 列出本地会话（不依赖 PySide6）
python -m cli.main sessions

# import 冒烟（不依赖 PySide6）
python -c "import cli.main, agent.tools, sessions.session_store, api.mcp_client; print('IMPORT OK')"

# gui 模块（懒加载设计，无 PySide6 也应能 import）
python -c "import gui.main_window; print('GUI MODULE OK')"

# 语法全量检查
python -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"
```

预期输出（`tools` 子命令）：

```
web_search	使用 DuckDuckGo HTML 端点执行网络搜索。
read_file	读取文本文件内容。
write_file	写入文本文件（自动创建父目录）。
list_files	列出目录内容（条目名，排序后返回）。
make_dir	递归创建目录。
delete_file	删除文件（仅文件，不删除目录）。
```

### 5. 启动界面（需要 PySide6）

```bash
python -m gui.main_window
```

详见 [quickstart.md](quickstart.md)。

---

## Python 版本与 PySide6 的兼容性

### 已知限制

**2026-09-26 当次实测**：参考机器上的 Python 为 `3.14.6`（`C:/Python314/python.exe`），该版本在 PyPI 上**没有对应的 PySide6 wheel**，`pip install PySide6` 无法完成。

这是会随上游版本推进变化的环境事实，**不是永久不可用**。在需要安装 PySide6 时，可按下列顺序考虑：

1. **选用 PySide6 已提供 wheel 的 Python 版本。** 2026-09-26 时点下，3.10 – 3.13 区间为可选项。安装前可先查询：

   ```bash
   pip index versions PySide6
   # 或
   pip download PySide6 --only-binary=:all: --no-deps -d /tmp/probe
   ```

2. **只使用非 GUI 功能。** `cli/`、`agent/`、`sessions/`、`api/` 在运行时完全不 import PySide6，可直接在 3.14 上使用。

3. **源码方式使用 GUI。** `gui/main_window.py` 的懒加载设计保证模块在无 PySide6 时可安全 import：

   ```python
   import gui.main_window          # ✅ 无 PySide6 也能成功
   gui.main_window.MainWindow()    # ❌ 首次实例化时才导入 PySide6，此时失败
   ```

### 复现本节结论

```bash
# 检查当前解释器是否有可用的 PySide6 wheel
python -c "
import sys, urllib.request, json
print('python', sys.version)
try:
    import PySide6
    print('PySide6 已安装:', PySide6.__version__)
except ImportError:
    print('PySide6 未安装')
"
```

---

## 环境变量

| 变量 | 取值 | 作用 | 读取时机 |
| --- | --- | --- | --- |
| `SCI_FORGE_OFFLINE` | `1` | 离线模式：`web_search` 直接返回空列表，不发起网络请求 | **模块导入时**读取一次（`agent/tools.py`） |
| `PYTHONPATH` | 仓库根目录 | 在不安装包的情况下直接 import 顶层包 | 进程启动时 |

### 离线模式

```bash
# Linux / macOS
SCI_FORGE_OFFLINE=1 python -m cli.main tools

# Windows PowerShell
$env:SCI_FORGE_OFFLINE = "1"; python -m cli.main tools

# Windows cmd
set SCI_FORGE_OFFLINE=1 && python -m cli.main tools
```

**重要**：`agent/tools.py` 中 `_OFFLINE = os.environ.get("SCI_FORGE_OFFLINE") == "1"` 是**模块级常量**，在 import 时求值。运行中修改环境变量不会生效，必须在进程启动前设置，或重新导入模块。

验证：

```bash
SCI_FORGE_OFFLINE=1 python -c "
from agent.tools import web_search
print(web_search('probe'))   # 期望输出 []
"
```

`sciforge`（MCP 版）仓库的工具同样识别此变量。

---

## 关联 MCP 服务器

若要使用 `api/mcp_client.py` 的桥接能力，需先安装 `sciforge`：

```bash
git clone https://github.com/liudongyan13701205717-source/sciforge.git
cd sciforge
pip install -e .
```

验证（`sciforge` 的控制台入口为 `sci-forge`，等价于 `python -m sciforge`）：

```bash
sci-forge          # 启动 stdio MCP 服务，进程会等待 stdin 输入
```

> 注意：MCP 服务以 stdio 传输，直接在终端运行会「挂住」是正常现象 —— 它在等待客户端的 JSON-RPC 消息。桥接方式见 [mcp-bridge.md](mcp-bridge.md)。

**依赖关系说明**：`sciforge-desktop` 的 `pyproject.toml` **未声明**对 `sci-forge` 的依赖（2026-09-26 实测）。两者是松耦合关系，需各自安装。

---

## 故障排查

### `ModuleNotFoundError: No module named 'cli'`

在仓库根目录之外运行了命令。`cli` / `agent` / `sessions` / `api` / `gui` / `core` 是**顶层包名**，不是 `sciforge_desktop.*` 命名空间下的子包，因此需要仓库根在 `sys.path` 上：

```bash
# 方式一：切到仓库根目录
cd sciforge-desktop && python -m cli.main tools

# 方式二：显式设置 PYTHONPATH
export PYTHONPATH=/path/to/sciforge-desktop   # Linux / macOS
python -m cli.main tools
```

若 `pip install -e .` 之后仍报此错，请一并参考下一条。

### `sciforge-desktop: command not found` 或入口导入失败

已知缺陷。`pyproject.toml` 的 entry point 写为裸模块 `cli.main:main`，与 MCP 版仓库的 `sciforge.cli:main` 风格不一致，安装后很可能无法导入。绕过方式：

```bash
python -m cli.main <子命令>
```

或绕过 console script 直接调用：

```python
from cli.main import main
raise SystemExit(main(["tools"]))
```

### `pip install PySide6` 失败 / 无匹配版本

见上文「Python 版本与 PySide6 的兼容性」。最直接的应对是换用已提供 wheel 的 Python 版本，或不使用 GUI 部分。

### `ImportError: libGL.so.1: cannot open shared object file`（Linux）

Qt 依赖的系统库缺失。安装：

```bash
sudo apt-get install libgl1 libegl1 libxkbcommon-x11-0
```

无头环境可用离屏平台绕过：

```bash
QT_QPA_PLATFORM=offscreen python -m gui.main_window
```

### 界面启动后白屏或立即退出

- 确认 `QT_QPA_PLATFORM` 未被设为无效值（可用 `offscreen` 或 `minimal` 验证）；
- 确认 PySide6 完整安装（`pip show PySide6`）；
- 无显示环境（CI、SSH 会话）下必须使用 `offscreen`。

### 工具返回「路径超出允许范围」

`agent/tools.py` 的路径沙箱只允许 `Path.home()` 与**进程启动时**的当前工作目录。检查：

- 目标路径是否在这两个目录之下；
- 是否用了 `..` 回溯到允许范围之外；
- 进程的 cwd 是否符合预期（沙箱以启动时 cwd 为基准）。

### `web_search` 总是返回空列表

可能原因：

1. 处于离线模式（`SCI_FORGE_OFFLINE=1`）；
2. 网络不可达 —— `web_search` 对 `URLError` / `OSError` / `ValueError` 一律返回 `[]`，不抛异常；
3. DuckDuckGo HTML 页面结构变化 —— 解析器依赖 `a.result__a` class，上游改版会静默返回空结果。

前两项属预期行为；第三项是健壮性缺口，可在 Issue 中反馈。

---

## 下一步

- 跑通完整上手流程：[quickstart.md](quickstart.md)
- 接入 MCP 服务器：[mcp-bridge.md](mcp-bridge.md)
- 提交代码：[CONTRIBUTING.md](../CONTRIBUTING.md)
