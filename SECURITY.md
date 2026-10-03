# Security Policy

本文件说明 sciforge-desktop 的安全边界与漏洞报告流程。

English summary: see "English Summary" at the bottom.

---

## 支持版本

| 版本 | 支持安全修复 |
| --- | --- |
| `0.1.x` | ✅ |

本项目目前处于 `0.1.0` 骨架阶段，尚未发布稳定版本，因此所有版本都在维护范围内。发布 `0.2.0` 之后本表将更新。

---

## 报告漏洞

**请勿通过公开 Issue 报告安全漏洞。** 公开 Issue 会让漏洞细节与利用方式提前扩散。

### 首选渠道

1. 打开本仓库的 **Security** 标签页；
2. 点击 **Report a vulnerability**（GitHub 私密漏洞报告）；
3. 按表单填写漏洞描述。

GitHub 私密漏洞报告允许你与维护者私下沟通，不经过公开的 Issue 列表。若该功能在仓库设置中不可用，请使用下面的备用渠道。

### 备用渠道

通过 `.github/SUPPORT.md` 中列出的维护者联系方式直接联系。

**请勿**在 Issue、Pull Request 讨论、社交媒体或聊天记录中披露漏洞细节。

---

## 报告内容建议

一份高质量的报告请包含：

| 项 | 说明 |
| --- | --- |
| 受影响版本 | 仓库 commit SHA 或发布版本 |
| 受影响平台 | 操作系统 / Python 版本 / PySide6 版本 |
| 漏洞类型 | 路径穿越、命令注入、任意文件读写、权限提升、拒绝服务、信息泄露等 |
| 复现步骤 | 最小可复现代码或操作序列 |
| 影响面 | 攻击者能达成什么，需要何种前置条件 |
| 严重性自评 | 你判断的严重程度及理由 |

---

## 本项目的安全边界

以下是设计层面的安全属性，理解它们有助于判断报告是否成立。

### 1. 路径沙箱（`agent/tools.py`）

6 个工具中，5 个文件类工具全部经 `_safe_path()` 校验：

- 允许的根目录为 `Path.home()` 与 `Path.cwd()`；
- 校验方式为 `resolve()` 后判断路径是否等于根目录或位于根目录的 `parents` 之内；
- 越界（含 `..` 回溯）抛 `PermissionError`，由各工具捕获后转成 `{"ok": False, "error": ...}`。

**边界说明**：沙箱以**进程启动时**的 `Path.cwd()` 为基准。若进程以高权限（如管理员）运行，可写范围也随之扩大 —— 沙箱不提供降权保护。

### 2. 会话 ID 校验（`sessions/session_store.py`）

`_session_path()` 采用双层校验：

1. **字符白名单**：`session_id` 非空，且每个字符都属于 `[0-9a-fA-F-]`；
2. **目录包含性兜底**：`resolve()` 后必须仍位于 `~/.sciforge-desktop/sessions/` 内部。

任一失败抛 `ValueError`。`list_sessions()` 另有防御：跳过缺少 `session_id` 键的文件。

### 3. 子进程边界（`api/mcp_client.py`）

- `MCPClient.start()` 通过 `subprocess.Popen` 以列表参数启动（未使用 `shell=True`），因此参数不经 shell 解析，不存在命令拼接注入面；
- **但**调用方需自行确保 `server_cmd` 来源可信 —— 目前本仓内无调用方，若未来由界面输入拼接命令，需先做校验；
- 读写均为管道 + 独立线程，`stderr` 单独接管，**未被读回**，长时间运行可能积压（可用性风险，非直接漏洞）；
- `_request()` 无超时机制，若服务器不响应将永久阻塞（可用性风险）。

### 4. 网络出口

- 唯一出网工具是 `agent/tools.py:web_search`，硬编码访问 `https://html.duckduckgo.com/html/`，仅 GET、无请求体；
- 设置 `SCI_FORGE_OFFLINE=1` 后该工具直接返回空列表，不发起任何网络请求（该变量在**模块导入时**读取，运行中改环境变量不生效）；
- User-Agent 为 `Mozilla/5.0 (sciforge-desktop/0.1.0)`。

### 5. 外部数据渲染

`web_search` 的结果由 `html.parser.HTMLParser` 解析，只提取 `<a class="result__a">` 的 `title` 与 `href` 属性值，不执行 HTML 解析后的内容。**当前界面未渲染这些结果**；若将来渲染，需注意转义。

### 6. 明确不提供的保证

| 项 | 说明 |
| --- | --- |
| 加密存储 | 会话数据以**明文 JSON** 存于 `~/.sciforge-desktop/sessions/` |
| 身份认证 | 桌面端本地应用，无认证机制 |
| 沙箱进程隔离 | 无。工具在主进程内执行 |
| 签名与公证 | 无打包签名配置 |
| 网络传输加密 | 桥接走本地 stdio，不涉及网络传输 |

---

## 已知问题（安全相关，待修复）

依据 2026-09-26 的代码核对：

| # | 问题 | 位置 | 性质 |
| --- | --- | --- | --- |
| 1 | `_request()` 无超时，服务器无响应时永久阻塞 | `api/mcp_client.py` | 可用性 |
| 2 | `stderr` 管道无读取方，长时间运行可能积压 | `api/mcp_client.py` | 可用性 |
| 3 | `close()` 未在 `finally` 或信号处理中保证调用，异常退出可能留下孤儿子进程 | `api/mcp_client.py` | 资源泄漏 |
| 4 | 路径沙箱以启动时 cwd 为基准，进程权限越高可写范围越大 | `agent/tools.py` | 设计限制（已在边界说明中记录） |
| 5 | `web_search` 依赖 HTML 页面结构，上游改版会导致解析失效（非安全问题，但会静默返回空结果） | `agent/tools.py` | 健壮性 |
| 6 | 会话数据明文存储 | `sessions/session_store.py` | 设计限制（已在边界说明中记录） |

发现上表未覆盖的问题，请按上述渠道报告。

---

## 响应流程

1. **确认收到**：维护者会在收到报告后尽快确认。
2. **评估**：判断严重性与影响面，必要时复现。
3. **修复**：在私密分支修复并准备补丁。
4. **披露**：与报告者协商披露时间；修复发布后同步更新 `CHANGELOG.md` 的安全小节。

本项目尚无正式的安全响应时限承诺。具体的响应时效以维护者实际确认为准。

---

## 安全相关的贡献

以下改动请在 PR 中显式标注安全影响：

- `agent/tools.py` 中沙箱逻辑的修改；
- `api/mcp_client.py` 中子进程启动方式的修改；
- 会话文件路径或校验逻辑的修改；
- 新增任何出网能力；
- 新增任何执行外部代码的路径。

---

## English Summary

- **Do not open a public Issue for security problems.** Use GitHub's private
  vulnerability reporting via the repository's Security tab, or the fallback
  contact in `.github/SUPPORT.md`.
- **Supported versions**: `0.1.x` (the project is still at `0.1.0` skeleton stage).
- **Security boundaries in this repo**: a path sandbox limited to `Path.home()`
  and the process-start-time `Path.cwd()`; two-layer `session_id` validation;
  `subprocess.Popen` with a list argv and no `shell=True`; a single outbound GET
  to DuckDuckGo that is fully disabled under `SCI_FORGE_OFFLINE=1`.
- **Explicitly not provided**: encryption at rest, authentication, process-level
  sandboxing, code signing, and request timeouts.
- **Open security-adjacent issues** (as of 2026-09-26): no timeout in
  `_request()`, unconsumed `stderr` pipe, `close()` not guaranteed on abnormal
  exit. See the table above for the full list.
- Security-sensitive PRs must explicitly state their security impact.
