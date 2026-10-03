# 快速上手

本文用 5 分钟走完 sciforge-desktop 的主要可操作路径。

> 前提：已完成 [installation.md](installation.md) 的步骤。下列所有命令均在**仓库根目录**下执行（原因见该文「故障排查」）。

---

## 1. 确认当前能力边界

本仓库处于骨架阶段。先看清「什么能用、什么还不行」，可以省掉大量困惑。

```bash
# 列出本仓库提供的本地工具
python -m cli.main tools
```

预期输出（6 行，`名称<TAB>说明`）：

```
web_search	使用 DuckDuckGo HTML 端点执行网络搜索。
read_file	读取文本文件内容。
write_file	写入文本文件（自动创建父目录）。
list_files	列出目录内容（条目名，排序后返回）。
make_dir	递归创建目录。
delete_file	删除文件（仅文件，不删除目录）。
```

目前**还不可用**的能力（依据 2026-09-26 实测）：

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| `sciforge-desktop` 命令 | 不可用 | entry point 缺包前缀；用 `python -m cli.main` |
| `python -m cli.main serve` | 占位 | 只打印 `serve 子命令尚未实现（占位）`，不启动服务 |
| 界面左侧导航、帮助 → 关于 | 无响应 | 三项导航与「关于」均未连接槽 |
| 界面内执行 MCP 工具 | 不可用 | `MCPClient` 在本仓无调用方 |
| 学科 registry、论文工具、数据库连接器 | 不在本仓 | 位于 `sci-forge` 仓库 |
| pytest 测试 | 无用例 | 0 个测试，无 pytest 配置 |

---

## 2. 本地会话

会话以 JSON 文件存于 `~/.sciforge-desktop/sessions/`，文件名是 `uuid4().hex`。

### 列出全部会话

```bash
python -m cli.main sessions
```

输出格式为 `session_id<TAB>name<TAB>created_at`。空仓库下无输出（正常）。

### 创建一个会话

没有对应的 CLI 子命令，请用 Python API：

```bash
python - <<'PY'
from sessions.session_store import create_session

sid = create_session("我的第一次会话")   # 返回的是 str（session_id），不是 dict
print("session_id:", sid)
PY
```

再用 `python -m cli.main sessions` 确认它出现在列表中。

### 读取 / 更新 / 删除

```bash
python - <<'PY'
from sessions.session_store import (
    create_session, list_sessions, load_session, save_session, delete_session,
)

# 1) 新建：返回 session_id 字符串
sid = create_session("draft")
print("新建:", sid)

# 2) 列出：只含元数据，没有 data 字段
for item in list_sessions():
    print(item["session_id"], item["name"], item["created_at"])

# 3) 读取：返回完整记录（含 session_id / name / created_at / data），不存在时返回 None
rec = load_session(sid)
print("data 初始值:", rec["data"])        # 初始为 {}，不是消息列表

# 4) 更新并保存：save_session 需要 (session_id, data) 两个参数
rec["name"] = "draft（已整理）"
rec["data"] = {"note": "hello", "tags": ["a", "b"]}
save_session(sid, rec["data"])

# 注意：save_session 只写入 data 字段，name / created_at 不在 data 内
print("保存后:", load_session(sid))

# 5) 删除：返回 bool。删不存在的 id 返回 False，不抛异常
print("删除:", delete_session(sid))
print("再删一次:", delete_session(sid))   # False
print("剩余会话数:", len(list_sessions()))
PY
```

要点：

- `create_session()` 返回 **`str`**（session_id），不是 dict；
- `save_session()` 的签名是 `save_session(session_id, data)` —— **两个参数**，只写入 `data` 字段；
- 会话内容存在 `data` 字段里，**初始值为 `{}`（空字典）**，不是消息列表；
- `load_session()` 返回完整记录（含 `session_id` / `name` / `created_at` / `data`），会话不存在时返回 `None`；
- `list_sessions()` 只返回元数据，**不含 `data`**；
- `delete_session()` 返回 `bool`：删除成功为 `True`，id 不存在为 `False`，**不抛异常**。

### 会话路径的安全校验

`session_store` 用两层校验防止路径穿越：

1. 字符白名单 —— `session_id` 非空且每个字符都属于 `[0-9a-fA-F-]`；
2. 目录包含性兜底 —— `resolve()` 后必须仍位于 `~/.sciforge-desktop/sessions/` 内。

任意一层失败抛 `ValueError`：

```bash
python - <<'PY'
from sessions.session_store import load_session

for bad in ["../../etc/passwd", "..\\windows\\system32", "abc$def", ""]:
    try:
        load_session(bad)
    except ValueError as e:
        print(f"拒绝 {bad!r}: {type(e).__name__}")
    else:
        print(f"!! 未被拒绝: {bad!r}")
PY
```

---

## 3. 本地 agent 工具

`agent/tools.py` 中有 6 个工具。**5 个文件类工具**统一返回 `{"ok": True, "result": ...}` 或 `{"ok": False, "error": str}`；**`web_search` 例外**，返回裸 `list[dict]`（此不一致是已知问题，见「已知缺陷」第 5 条）。

### 文件操作与路径沙箱

5 个文件类工具（`read_file`、`write_file`、`list_files`、`make_dir`、`delete_file`）都经 `_safe_path()` 校验，**允许的根目录只有两个**：

- `Path.home()`（用户主目录）
- `Path.cwd()`（进程启动时的当前工作目录）

```bash
python - <<'PY'
from agent.tools import TOOL_REGISTRY

root = TOOL_REGISTRY["make_dir"]("demo_dir")
print("make_dir:", root)

w = TOOL_REGISTRY["write_file"]("demo_dir/hello.txt", "你好，sciforge\n")
print("write_file:", w)

r = TOOL_REGISTRY["read_file"]("demo_dir/hello.txt")
print("read_file:", r)

l = TOOL_REGISTRY["list_files"]("demo_dir")
print("list_files:", l)

d = TOOL_REGISTRY["delete_file"]("demo_dir/hello.txt")
print("delete_file:", d)

# 越界会被拒绝，且以字典形式返回错误而不是抛异常
print("越界读根目录:", TOOL_REGISTRY["read_file"]("/"))
print("越界回溯:", TOOL_REGISTRY["read_file"]("demo_dir/../../../etc/passwd"))
PY
```

行为要点：

- `write_file` 会自动创建父目录；
- `delete_file` 只删文件，不删目录；删不存在的文件返回 `ok: False`；
- 越界（含 `..` 回溯、绝对路径越界）返回 `{"ok": False, "error": "..."}`；
- **沙箱以进程启动时的 cwd 为基准** —— 在别处启动进程，可写范围随之改变。

### 工具注册表

`TOOL_REGISTRY` 是 `name -> callable` 的映射：

```bash
python -c "
from agent.tools import TOOL_REGISTRY
for name, fn in TOOL_REGISTRY.items():
    print(name, '->', fn.__name__)
"
```

### 网络搜索与离线模式

```bash
# 联网（依赖网络可达性；失败时返回空列表而非抛错）
python -c "
from agent.tools import web_search
r = web_search('CRISPR')
print(type(r).__name__, len(r))
print(r[:2])
"

# 离线（不发起任何网络请求）
SCI_FORGE_OFFLINE=1 python -c "
from agent.tools import web_search
print(web_search('CRISPR'))
"
```

`web_search` 的**返回契约与同模块其余 5 个工具不一致**：其余返回带 `ok` 键的 `dict`，它返回裸 `list`（每项含 `title` 与 `url` 两个键，**不是** `href`）。调用方需按类型区分处理。此为已知项。

---

## 4. 图形界面

```bash
# 需要 PySide6；无显示环境时加离屏平台
python -m gui.main_window

# 无头环境
QT_QPA_PLATFORM=offscreen python -m gui.main_window
```

### 界面导览

当前窗口只有外壳，结构如下：

```
┌────────────────────────────────────────────────────────┐
│ 文件        帮助                                          │
├──────────────┬─────────────────────────────────────────┤
│  会话         │                                         │
│  工具         │            （中央占位标签）                │
│  设置         │                                         │
├──────────────┴─────────────────────────────────────────┤
│ 就绪                                                  │
└────────────────────────────────────────────────────────┘
```

| 元素 | 数量 / 文案 | 当前行为 |
| --- | --- | --- |
| 菜单栏 | 「文件(&F)」「帮助(&H)」 | 「文件 → 退出(&Q)」**已连接 `self.close`，可关闭窗口**；「帮助 → 关于(&A)」未连接槽 |
| 左侧导航 | 3 项：会话 / 工具 / 设置 | **均未连接槽**，点击无反应 |
| 中央区域 | 1 个占位标签 | 空白，文案「sciforge 桌面客户端骨架 — 功能开发中」 |
| 状态栏 | 「就绪」 | 静态文案 |
| 窗口标题 | `sciforge 桌面客户端` | — |
| 默认尺寸 | 960 × 640 | — |

即：界面目前用于确认环境可启动，**唯一可用的交互是「文件 → 退出」关闭窗口**；其余导航与「关于」均无响应。若期望点击导航切换内容，需要等界面逻辑落地（见 [desktop-core-relationship.md](desktop-core-relationship.md)）。

### 验证懒加载设计

```bash
python -c "
import sys, gui.main_window as m
assert 'PySide6' not in sys.modules, 'import 时不应加载 PySide6'
print('懒加载 OK:', m.__doc__.strip().splitlines()[0])
"
```

---

## 5. MCP 桥接（进阶）

`api/mcp_client.py` 的 `MCPClient` 已实现 JSON-RPC 2.0 over stdio，但**本仓内无调用方**。用法：

```bash
python - <<'PY'
from api.mcp_client import MCPClient

# 注意：MCPClient() 不接受任何参数，server_cmd 在 start() 时传入
client = MCPClient()
try:
    client.start(["python", "-m", "sciforge"])
    resp = client.initialize()
    # initialize() 返回完整信封，能力信息在 resp["result"]["capabilities"]
    print("服务器身份:", resp["result"].get("serverInfo"))

    tools = client.call_tool("tool_name", {})   # arguments 为必填参数
    print("工具结果 keys:", list(tools.keys()))
finally:
    client.close()   # 重要：不关闭会留下孤儿子进程
PY
```

完整的协议细节、消息格式、API 清单与示例见 [mcp-bridge.md](mcp-bridge.md)。

---

## 6. 校验当前工作副本

本仓库暂无测试基建，可用以下方式做基本校验：

```bash
# 全量 AST 语法检查
python -c "import ast, glob; [ast.parse(open(f, encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"

# import 冒烟（4 个非 GUI 包）
python -c "import cli.main, agent.tools, sessions.session_store, api.mcp_client; print('IMPORT OK')"

# 离线模式确认
python -c "
import os
assert os.environ.get('SCI_FORGE_OFFLINE') == '1'
from agent.tools import web_search
assert web_search('probe') == []
print('OFFLINE OK')
"
```

若本地装有 `ruff`（仓库当前无 `[tool.ruff]` 配置，ruff 会以默认规则集运行）：

```bash
ruff check .
```

---

## 下一步

| 你想做的事 | 去哪里 |
| --- | --- |
| 遇到报错 | [installation.md](installation.md) 的「故障排查」、`.github/SUPPORT.md` |
| 接入 MCP 服务器 | [mcp-bridge.md](mcp-bridge.md) |
| 了解双仓关系与核心同步 | [desktop-core-relationship.md](desktop-core-relationship.md) |
| 提交代码 | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 报告安全问题 | [SECURITY.md](../SECURITY.md) |
