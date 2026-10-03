# MCP 桥接层

本文说明 `api/mcp_client.py` 的实现：协议、握手、消息格式、API 清单、已知缺口与使用示例。

> 状态（2026-09-26 核对）：该模块共 124 行，仅用标准库实现，可独立使用，但**本仓库内没有任何调用方** —— 界面中不会执行 MCP 工具，agent 主循环也尚未接入。

---

## 定位

`sciforge-desktop` 是**客户端**，`sci-forge` 是**MCP 服务器**。两者通过 JSON-RPC 2.0 over stdio 通信：

```
┌──────────────────────────┐        stdio（子进程管道）      ┌──────────────────────────┐
│  sciforge-desktop        │  ──── stdin 写入 ────▶      │  sci-forge（MCP 服务器）  │
│                          │  ◀─── stdout 读取 ────       │                          │
│  api/mcp_client.py       │                               │  65 个 MCP 工具           │
│  （MCPClient）            │        stderr 建管道但无人读   │  261 门学科 / 46 个连接器  │
└──────────────────────────┘                               └──────────────────────────┘
```

**传输特点**：本地子进程管道，非网络。因此不存在 TLS、端口、鉴权问题；代价是两端必须同机，且客户端必须自行管理生命周期（见「已知缺口」）。

---

## 协议与常量

模块内**只有一个**模块级常量：

| 项 | 值 | 位置 |
| --- | --- | --- |
| MCP 协议版本 | `2024-11-05` | `_PROTOCOL_VERSION`（`api/mcp_client.py:15`） |
| JSON-RPC 版本 | `2.0` | 每次请求体内硬编码 |
| 客户端名称 | `sciforge-desktop` | `initialize()` 内 `clientInfo` 硬编码 |
| 客户端版本 | `0.1.0` | `initialize()` 内 `clientInfo` 硬编码 |
| stdio 分帧 | **每行一条**（`\n`） | 写入 `json.dumps(payload) + "\n"`；读取按行迭代 |

客户端身份**不是常量**，而是直接写在 `initialize()` 的参数字典里：

```python
"clientInfo": {"name": "sciforge-desktop", "version": "0.1.0"}
```

若改包名或版本号，需同步修改 `initialize()` 内的该字典，并更新本表。

---

## 生命周期

```
MCPClient()                     # 构造无需任何参数
      │
      ├─ start(server_cmd)  ──► subprocess.Popen(server_cmd,
      │                           stdin=PIPE, stdout=PIPE, stderr=PIPE,
      │                           text=True, encoding="utf-8")
      │                       + 1 个后台守护线程：stdout → _read_loop()
      │                         · 含 "id"  → _responses 队列
      │                         · 无 "id"  → _notifications 队列
      │
      ├─ initialize()       ──► _request("initialize") → 返回完整响应信封
      │                       └─ 随后自动 notify("notifications/initialized", {})
      │
      ├─ call_tool(n, a)    ──► _request("tools/call", {...})
      ├─ notify(m, p)       ──► 发送无 id 消息，不等响应
      ├─ notifications()    ──► 无限生成器，阻塞式 yield 通知
      │
      └─ close()            ──► terminate() → wait(5s) → 超时则 kill()
                                  随后 _proc = None（不 join 线程）
```

**必须调用 `close()`**，否则会留下孤儿子进程。

**「未启动 / 运行中 / 已关闭」的实际行为**（与直觉略有差异，务必按下表写代码）：

| 状态 | `start(cmd)` | `initialize()` / `call_tool()` / `notify()` | `notifications()` | `close()` |
| --- | --- | --- | --- | --- |
| 未启动 | 正常启动 | `RuntimeError("MCP 客户端未启动")` | 永久阻塞（生成器等队列） | 静默无操作 |
| 运行中 | `RuntimeError("MCP 客户端已启动")` | 正常 | 永久阻塞直到有通知 | 终止子进程 |
| 已 `close()` | **可再次启动**（`_proc` 已置 `None`） | `RuntimeError` | 永久阻塞 | 静默无操作 |

两点容易踩坑：

- `close()` **幂等**，未启动时调用也不报错；
- `close()` 之后**可以再次 `start()`**，模块不禁止重启。

---

## API 清单

### `MCPClient()`

构造函数**不接受任何参数**。`server_cmd` 在 `start()` 时传入，不在构造时。

### 方法

| 方法 | 签名 | MCP 方法 | 行为 |
| --- | --- | --- | --- |
| `start` | `(server_cmd: list[str]) -> None` | — | 启动子进程与 1 个后台读取线程 |
| `initialize` | `() -> dict` | `initialize` | 发送初始化请求，**返回完整响应信封**，并自动补发 `notifications/initialized` |
| `call_tool` | `(name: str, arguments: dict) -> dict` | `tools/call` | 调用工具；`arguments` 为**必填** |
| `notify` | `(method: str, params: dict) -> None` | 任意 | 发送 notification，不等待响应；`params` 为**必填** |
| `notifications` | `() -> Iterator[dict]` | — | **无限生成器**，阻塞式 yield 通知 |
| `close` | `() -> None` | — | `terminate()` → `wait(5s)` → 超时 `kill()` |

`start()` 使用 `subprocess.Popen` 传列表 argv，**未用 `shell=True`**，因此参数不经 shell 解析，不存在命令拼接注入面。

### 三个必须知道的返回值/签名细节

1. **`initialize()` 返回完整信封**，即 `{"jsonrpc", "id", "result"}`（或含 `error`），**没有剥离** `jsonrpc` / `id`。要拿能力信息需自行取 `resp["result"]`。
2. **`call_tool()` 与 `notify()` 的参数都是必填**。`call_tool("x")` 与 `notify("x")` 会抛 `TypeError`，不存在默认值。
3. **`notifications()` 是无限生成器**，不是「取一批再清空」。它在队列为空时**永久阻塞**，因此调用方必须自己掌控退出条件（例如在另一个线程关闭子进程，或用 `queue` 之外的中止手段）。写成 `for msg in client.notifications()` 的裸循环在无通知时会挂死。

---

## 初始化消息格式

`initialize()` 实际发出的请求体（`id` 从 `1` 开始自增，由 `_id_lock` 保护）：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "sciforge-desktop", "version": "0.1.0" }
  }
}
```

`initialize()` 收到响应后**紧接着自动发送**：

```json
{ "jsonrpc": "2.0", "method": "notifications/initialized", "params": {} }
```

服务器响应形如：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": { "tools": {} },
    "serverInfo": { "name": "sci-forge", "version": "0.1.0" }
  }
}
```

`initialize()` 的返回值就是上面这个**完整对象**，取能力信息写 `resp["result"]["capabilities"]`。

---

## 消息分帧

stdout 采用**逐行分帧**（`\n`），不是空行分帧：

```
{"jsonrpc": "2.0", "id": 1, "result": {...}}\n
{"jsonrpc": "2.0", "method": "notifications/message", "params": {...}}\n
```

读取端 `_read_loop` 的处理顺序：

1. `for line in self._proc.stdout` 逐行迭代；
2. `line.strip()`，**空行直接跳过**；
3. `json.loads(line)`；
4. 解析失败（`JSONDecodeError`）→ **`continue` 静默丢弃**，不重试、不记录、不放入队列；
5. `"id" in msg` → 进 `_responses`；否则进 `_notifications`。

**推论**：

- 服务器必须保证**一条 JSON-RPC 消息占一行**。若把一条消息跨行输出（美化缩进的多行 JSON），`json.loads` 会失败并被**静默丢弃** —— 表现为「客户端永远等不到响应，且没有任何错误提示」。
- 因为失败是静默的，排障时不要只看向服务端，客户端侧完全没有日志可查。

---

## 队列模型

| 队列 | 方向 | 消费者 | 元素 |
| --- | --- | --- | --- |
| `_responses` | 子进程 stdout → 客户端 | `_request()` | `dict`（**必含 `id`**） |
| `_notifications` | 子进程 stdout → 客户端 | `notifications()` | `dict`（**必不含 `id`**） |

分流规则只有一条：消息里**有没有 `id` 键**。

`_request()` 的等待逻辑：

```python
while True:
    resp = self._responses.get()      # 无超时，永久阻塞
    if resp.get("id") == msg_id:
        return resp
    # 不匹配 → 该消息被丢弃，循环继续等下一条
```

由此产生两条实际约束：

- **只支持单个在途请求**。`_request()` 是同步阻塞的，且按 `id` 逐条比对；若两个线程并发调用，或服务器乱序返回，不匹配的消息会被**取出后直接丢弃**，导致真正的持有者永久阻塞。
- **无超时**。服务器不响应即永久挂起（GUI 层会卡死）。

---

## 使用示例

### 最小可用

```python
from api.mcp_client import MCPClient

client = MCPClient()
try:
    client.start(["sci-forge"])
    resp = client.initialize()               # 返回完整信封
    print("服务器:", resp["result"].get("serverInfo"))
finally:
    client.close()
```

### 用 `try / finally` 保证关闭

`close()` 不会在异常路径上自动执行，必须显式包在 `finally` 里（这也是 [SECURITY.md](../SECURITY.md) 把「`close()` 未保证调用」列为已知缺口的原因）：

```python
from api.mcp_client import MCPClient

client = MCPClient()
try:
    client.start(["sci-forge"])
    client.initialize()
    # ... 业务逻辑 ...
except RuntimeError as exc:
    print("生命周期错误:", exc)
finally:
    client.close()
```

### 调用工具

```python
resp = client.call_tool("search_papers", {"query": "CRISPR", "limit": 5})
print(resp["result"])        # 同样需自行从信封里取 result
```

`arguments` **必须显式传入**，即使为空也要写 `{}`。

### 消费通知

`notifications()` 是无限生成器，必须自带退出条件。下面用一个「有界等待 + 主动关闭」的写法，避免裸 `for` 循环挂死：

```python
import threading

stop = threading.Event()

def consume():
    # 每次 yield 最多阻塞到有通知为止；靠外部把 client 关掉来解除阻塞
    for msg in client.notifications():
        print("通知:", msg)
        if stop.is_set():
            break

t = threading.Thread(target=consume, daemon=True)
t.start()
...
stop.set()
client.close()      # 关闭子进程后读取端结束，生成器循环退出
```

由于 `_read_loop` 在子进程 stdout 关闭后自然终止，**先 `close()` 再 `join()`** 是安全顺序。

### 启动 `sci-forge` 服务器

`sci-forge` 仓的 console script 为 `sci-forge`（等价于 `python -m sciforge`），需在 `PATH` 中；否则用模块入口更稳：

```python
client.start(["python", "-m", "sciforge"])
```

### 传环境变量（当前无直接支持）

`MCPClient` 的 `start()` **不接受 `env` / `cwd` 参数**，`Popen` 直接继承父进程环境。因此若要给子进程注入环境变量（如让服务器侧也走离线模式），只能在 `start()` **之前**修改当前进程环境：

```python
import os

os.environ["SCI_FORGE_OFFLINE"] = "1"   # 必须在 start() 之前设置
client.start(["sci-forge"])
```

这是当前实现的限制（见「已知缺口」），不是推荐用法。

---

## 安全边界

| 项 | 现状 |
| --- | --- |
| shell 注入 | 无。`Popen` 传列表 argv，未用 `shell=True` |
| 端口暴露 | 无。走 stdio，不监听任何端口 |
| 鉴权 | 无。本地同机进程间无认证机制 |
| 传输加密 | 不适用。非网络传输 |
| 命令来源 | **需调用方保证**。本仓无调用方；若未来由界面输入拼接 `server_cmd`，必须先做校验 |
| 进程权限 | 子进程继承父进程权限，无降权隔离 |
| 路径穿越 | 不适用。`server_cmd` 是 argv，不经路径解析 |

**离线模式**：`sci-forge` 侧通过 `SCI_FORGE_OFFLINE=1` 关闭出网。`sciforge-desktop` 侧的 `agent/tools.py` **独立**读取同名环境变量（`agent/tools.py:17`），与 `MCPClient` 无联动。

---

## 已知缺口

依据 2026-09-26 的逐行核对：

| # | 缺口 | 影响 | 位置 |
| --- | --- | --- | --- |
| 1 | `_request()` 无超时 | 服务器不响应时**永久阻塞**（GUI 会卡死） | `api/mcp_client.py:78-81` |
| 2 | 不匹配的 `id` 响应被取出后丢弃 | 并发或乱序响应时，真正的请求方可能**永久阻塞** | `api/mcp_client.py:78-81` |
| 3 | 只支持单个在途请求 | 多线程并发调用不安全 | 整体设计 |
| 4 | `stderr` 建了管道但无读取方 | 服务器大量写 stderr 时管道缓冲区填满，**可能反压阻塞子进程**；错误日志完全不可见 | `api/mcp_client.py:42` |
| 5 | JSON 解析失败静默丢弃 | 分帧不符时无任何错误提示，极难排障 | `api/mcp_client.py:57-58` |
| 6 | `notifications()` 为无限生成器 | 队列空时永久阻塞，无「取一批」语义 | `api/mcp_client.py:111-114` |
| 7 | `close()` 不 `join()` 读取线程 | 线程为 daemon，退出时不阻塞，但可能残留瞬时状态 | `api/mcp_client.py:116-124` |
| 8 | `kill()` 后未再 `wait()` | 未回收僵尸进程 | `api/mcp_client.py:122-123` |
| 9 | 不支持 `env` / `cwd` 注入 | 需在 `start()` 前改父进程环境 | `api/mcp_client.py:37-44` |
| 10 | 本仓无调用方 | 界面无法执行 MCP 工具；agent 主循环未接入 | 全仓 |
| 11 | 界面导航与「关于」未连接槽 | 无法从 UI 触达桥接层 | `gui/main_window.py:36,44-45` |

其中 #1 与 #4 已在 [SECURITY.md](../SECURITY.md) 的「已知问题」中登记（性质为可用性风险，非注入类漏洞）。

---

## 双仓关系

| 仓库 | 角色 | 分发名 | 导入包 | 控制台入口 | 许可证 |
| --- | --- | --- | --- | --- | --- |
| `sciforge-desktop`（本仓） | MCP 客户端 | `sciforge-desktop` | `api` / `agent` / `cli` / `core` / `gui` / `sessions` | `sciforge-desktop`（**缺包前缀，暂不可用**） | Apache-2.0 |
| `sci-forge` | MCP 服务器 | `sci-forge` | `sciforge` | `sci-forge` | Apache-2.0 |

- 两仓许可证**相同**（均为 Apache-2.0，2026-09-26 核对），跨仓组合使用无许可证冲突。
- 本仓 `pyproject.toml` **未声明**对 `sci-forge` 的依赖；两者松耦合，需各自安装。
- 核心同步脚本 `scripts/sync_core.py` **已就位**（详见 `docs/architecture/core-sync.md`），但**尚未执行首次 `--apply`**：本仓 `core/` 目前仍只有 1 个 stub 文件。因此「同步机制已建立、投影未落地」是当前准确状态。

---

## 下一步

- 核心同步现状与投影边界：[`docs/architecture/core-sync.md`](../architecture/core-sync.md)
- 双仓关系与目标形态：[desktop-core-relationship.md](desktop-core-relationship.md)
- 安装 `sci-forge` 并启动服务：[installation.md](installation.md)
- 报告桥接层的安全问题：[SECURITY.md](../SECURITY.md)
