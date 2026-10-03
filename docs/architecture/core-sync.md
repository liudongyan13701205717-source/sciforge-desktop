# 核心同步约定（桌面端视角）

> 适用范围：本文件描述 `sciforge-desktop`（消费方）的 `core/` 目录该如何被维护。
> 源仓侧的对应说明在 `sciforge` 仓库的 `docs/architecture/core-sync.md`；逐目录映射见该仓的
> `docs/architecture/core-sync-mapping.md`。
>
> 本文件与源仓同名文件**内容对称、视角相反**：同一套规则，从消费方角度叙述。

本文档中的所有数量与状态均标注观测日期 **2026-09-26**，为当次实测值，会随上游演进变化。

---

## 1. `core/` 是什么

**`core/` 是源仓核心库的只读投影，不是本仓 hand-written 的代码。**

```
sciforge（源仓）                        sciforge-desktop（本仓）
sciforge/sciforge/<12 个目录>  ──▶  core/<投影内容>
```

| 本仓自有（不参与同步） | 投影所得（源仓独占内容） |
| --- | --- |
| `agent/`（6 个本地工具） | `core/*.py`（源仓 `core/` 内容，落在根） |
| `api/`（`MCPClient`，JSON-RPC over stdio） | `core/claims/` `core/deliver/` `core/disciplines/` |
| `cli/`（`serve` 占位 / `sessions` / `tools`） | `core/export/` `core/parse/` `core/reproduce/` |
| `gui/`（PySide6 外壳，懒加载） | `core/research/` `core/review/` `core/science/` |
| `sessions/`（本地会话 JSON 存储） | `core/venue/` `core/write/` |

### 最重要的一条规则

> **不要直接编辑 `core/` 内的任何文件。**

投影是**逐字节**复制。你在 `core/` 里的任何修改都会在下一次同步时被源文件**静默覆盖**，
且不会有任何冲突提示。

需要桌面端专属逻辑时，**在 `core/` 之外新增模块**（例如放进 `api/` 或新建 `adapters/`），
由它去调用 `core/` 的能力。这样核心更新能直接受益，本地特化也不会被冲掉。

---

## 2. 同步边界

### 2.1 会出现在本仓 `core/` 下的内容

源仓包目录下 **12 个**目录整体投影而来：`core/`、`claims/`、`deliver/`、`disciplines/`、
`export/`、`parse/`、`reproduce/`、`research/`、`review/`、`science/`、`venue/`、`write/`。

其中源仓的 `core/` 是**锚点**：它的内容直接落在本仓 `core/` 的**根**，不加 `core/core/` 这层。
其余 11 个目录保持原名，作为 `core/` 的子目录。

### 2.2 不会出现在本仓 `core/` 下的内容

| 项 | 理由 |
| --- | --- |
| 源包根层 `server.py` / `cli.py` / `__main__.py` / `__init__.py` | MCP server 传输层入口与包导出面，仅源仓有意义。**2026-09-26 实测源包根层 `.py` 恰为这 4 个** |
| 源仓的 `pyproject.toml` / `tests/` / `docs/` | 不属于核心库；两仓依赖不同（本仓 `PySide6>=6.6`，源仓 `mcp>=1.29.0`） |
| `__pycache__/`、隐藏文件、`.pyc` / `.pyo` / `.orig` / `.rej` | 编译缓存与本地残留，遍历时跳过 |
| 本仓 `core/` 之外的任何文件 | 本仓自有，不受同步机制影响 |

### 2.3 现有的 `core/__init__.py` stub 会被覆盖

**2026-09-26 当次实测**：本仓 `core/` 下只有一个 `__init__.py`，内容为 3 行 docstring 的空占位
（"核心同步在后续任务中完成，本包当前为空占位"），**无任何可执行代码**。

首次执行同步时，源仓 `core/__init__.py` 会**覆盖**这个 stub。这是预期行为：
stub 的存在意义就是被真实内容替换。本次任务**不执行**同步，stub 保持原样未被改动。

> 本仓 README 记载源仓 `sciforge/core` 为 364 行（2026-09-26 核对 README 所得，非本次逐行统计）。

---

## 3. 方向：单向，桌面端是下游

```
sciforge（源，唯一真值）  ──(只写、不删)──▶  sciforge-desktop/core/（投影）
        上游                                        下游
```

- 只有 `源 → 桌面` 一个方向，**没有任何反向路径**。
- 桌面端**不能**把改动推回源仓。想改核心？改源仓，再同步。
- 同步脚本也**不做删除**：源仓删掉的文件，在桌面端会残留为 `target-only`，
  只在校验报告里列出，**需人工确认后处置**。

---

## 4. 冲突优先级（从桌面端看）

| 优先级 | 规则 | 对桌面端的含义 |
| --- | --- | --- |
| 1 | **源仓为唯一真值源** | 核心语义以源仓为准；桌面端读到与源仓不一致的内容即为缺陷 |
| 2 | **同名文件一律由源覆盖** | 别在 `core/` 里改代码 —— 改了会被覆盖，且无提示 |
| 3 | **目标侧独有文件一律保留** | 你的文件不会被同步脚本删掉，但会持续出现在 `target-only` 报告里 |
| 4 | **禁止反向同步** | 桌面端的"修复"无法回流源仓 |
| 5 | **本地特化只允许在 `core/` 之外** | 保证投影可被安全覆盖 |

第 3 条带来一个实际后果：**删除源文件不会自动传播**。若某个模块在源仓被移除，
桌面端会留下一个孤儿文件，需要人工删除。`--check` 报告的 `target-only` 段落就是为此存在。

---

## 5. 一致性判定

- 判定方式：逐文件 **SHA-256** 比对，不看 mtime、不做文本比较。
- 复制方式：`shutil.copy2`（保留 mtime），因此重复同步不产生无谓差异。
- "一致" ≡ `missing-in-target` 为 0 **且** `content-differs` 为 0。
- `target-only` 存在**不**破坏一致性判定 —— 它是设计允许的状态。

| 状态 | 含义 | 对桌面端的含义 |
| --- | --- | --- |
| `identical` | 两侧摘要相同 | 正常 |
| `missing-in-target` | 本仓缺该文件 | 该跑 `--apply` 了 |
| `content-differs` | 两侧都有但内容不同 | 多半是有人手改了 `core/`，应撤销改动 |
| `target-only` | 仅本仓有 | 桌面端自建文件，或源仓已删除该文件 |

---

## 6. 脚本用法

同步脚本在本仓位于 `scripts/sync_core.py`，与源仓同名文件**内容逐字节一致**。

在本仓目录下直接运行即可 —— 脚本会依据自身位置自动推断路径
（源根 = `../sciforge/sciforge`，目标根 = `./core`）：

```bash
# 预览差异（默认模式，不写任何文件）
python scripts/sync_core.py --dry-run

# 落盘同步
python scripts/sync_core.py --apply

# 只校验；发现漂移以退出码 1 结束
python scripts/sync_core.py --check

# 机器可读输出
python scripts/sync_core.py --check --json

# 打印同步清单（12 项）
python scripts/sync_core.py --list-manifest
```

若两仓不同处一文件夹，显式指定：

```bash
python scripts/sync_core.py --check \
  --source /path/to/sciforge/sciforge \
  --target /path/to/sciforge-desktop/core
```

### 退出码

| 码 | 含义 |
| --- | --- |
| `0` | 正常结束；`--check` 下表示两侧一致 |
| `1` | `--check` 检出漂移 |
| `2` | 用法或环境错误（源根不存在、源与目标同路径、目标位于源内部等） |

### 安全护栏

- 默认 `--dry-run`：**不加参数绝不写盘**。
- 拒绝 `--source == --target`。
- 拒绝目标根位于源根内部。
- 脚本不含 `subprocess` / `os.system` / `shutil.rmtree`，无任何删除路径。
- 仅用 Python 标准库，Python 3.11+（实测本机为 3.14.6）。

---

## 7. 已知适配问题：绝对导入（当前最大障碍）

**2026-09-26 当次实测**：源仓有 **482 处** `sciforge.` 绝对导入，分布于 **320 个**文件
（grep 文本匹配口径，含注释与字符串字面量，为上界估计）。

投影是逐字节复制，所以投影后的文件仍然写着 `from sciforge.disciplines import ...`。
本仓的包布局是 **6 个平铺顶层包**（`agent` / `api` / `cli` / `core` / `gui` / `sessions`），
**不是** `sciforge.*` 命名空间，因此这些导入在投影后**不会自动成立**。

也就是说：**完成首次 `--apply` 后，`core/` 里的文件在导入层面很可能直接报错。**
同步机制保证的是字节一致，不保证导入可解析 —— 后者是适配层的责任。

三种应对（本仓需自行选型，同步脚本的行为不受影响）：

| 方案 | 做法 | 代价 |
| --- | --- | --- |
| A. 提供 `sciforge` 兼容包 | 在 `core/` 之外建 `sciforge` 包，转调 `core.*` | 需维护一层薄映射；投影保持逐字节，**推荐** |
| B. 改包命名空间 | 把投影放进 `sciforge_desktop.core` 之类 | 动本仓既有包名，破坏性最大 |
| C. 同步后批量改写导入 | 投影完跑一次导入重写 | 破坏「逐字节」前提，需引入改写步骤与额外校验 |

无论选哪个，都**不要**因此去改 `core/` 内的文件 —— 那是第 1 节禁止的动作。

另有两项依赖缺口（2026-09-26 实测）：`parse/` 依赖 `pymupdf>=1.24`、
`reproduce/` 依赖 `numpy>=1.26` + `matplotlib>=3.8`，二者都属源仓的 `reproduce` extra，
本仓默认不装 —— 投影后这两个子包**导入即失败**，需按需安装。

---

## 8. 现状快照（2026-09-26 实测）

| 项 | 观测值 |
| --- | --- |
| 本仓 `core/` 文件数 | 1（仅 `__init__.py` stub） |
| 本仓 `core/` 可执行代码 | 无 |
| 本仓 `docs/` 目录 | **不存在**（本文件会创建 `docs/architecture/`） |
| 本仓 `.github/` 内容 | `ISSUE_TEMPLATE/`、`pull_request_template.md`；**无 `workflows/`** |
| 本仓顶层包 | `agent/` `api/` `cli/` `core/` `gui/` `sessions/`（6 个平铺包） |
| 本仓是否声明对源仓的依赖 | 未声明（`pyproject.toml` 无 `sci-forge` 依赖） |
| 两仓代码级共享 | 零（同步机制本次才建立，且尚未执行首次投影） |
| 本仓测试 | 无 `tests/` 目录 |

### 文档漂移（既有 README 问题，非本任务引入）

本仓 README 引用了以下文件，但 2026-09-26 的工作树中**不存在**：

- `docs/index.md`、`docs/installation.md`、`docs/quickstart.md`、`docs/mcp-bridge.md`、
  `docs/desktop-core-relationship.md` —— 整个 `docs/` 目录当时不存在
- `.github/SUPPORT.md` —— `.github/` 下只有 `ISSUE_TEMPLATE/` 与 `pull_request_template.md`
- `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `SECURITY.md` / `CHANGELOG.md` / `LICENSE` ——
  这些**确实存在**于本仓根目录，仅前述 `docs/*` 与 `.github/SUPPORT.md` 缺失

本任务新增的 `docs/architecture/core-sync.md` 会使 `docs/` 目录首次存在。
`docs/desktop-core-relationship.md`（README 指向的同步现状文档）仍缺失，
其应承载的内容已由本文件覆盖，是否补建待定。

---

## 9. CI 与自动化的实际限制（必须知情）

校验工作流位于**源仓** `.github/workflows/core-consistency.yml`。它做两件事：

1. 校验本仓 `scripts/sync_core.py` 与源仓同名文件**逐字节一致**；
2. 克隆本仓到相邻目录并跑 `--check`，把漂移作为失败。

**一个 GitHub Actions 工作流只能响应本仓事件，无法订阅另一仓库的 push/PR。** 因此：

| 仓库 | push / PR | 手动触发 |
| --- | --- | --- |
| `sciforge`（源仓） | ✅ 自动 | ✅ `workflow_dispatch` |
| `sciforge-desktop`（本仓） | ❌ **不触发** | 需在源仓手动 `workflow_dispatch` |

要让本仓事件也获得自动校验，必须在**本仓**也放一份工作流（内容可与源仓一致）。
本仓 `.github/` 下当前**没有** `workflows/` 目录。这超出本任务的文件范围，
因此此处**如实标注为已知缺口**，不假装已覆盖。

### 首次落地的预期结果

在真正执行 `--apply` 之前，本仓 `core/` 只有 1 个 stub 文件，
因此 CI 的 `--check` **必然报漂移并失败**（预期数百个 `missing-in-target`，
外加 `core/__init__.py` 一条 `content-differs`）。

这是**预期初始状态**，不是配置错误：CI 的作用正是让"本仓核心还没投影"这件事可见。
完成首次 `--apply`（并解决第 7 节的导入适配）后 CI 转绿。

---

## 10. 给桌面端贡献者的检查清单

改动涉及核心时：

1. **不要**改 `core/` 内的文件。
2. 改源仓 `sciforge/` 下的对应文件。
3. 在源仓提交，然后跑 `python scripts/sync_core.py --apply`（或让 CI 校验）。
4. 本仓若需适配，在 `core/` 之外加模块。
5. 只涉及界面、交互、本地会话的改动，可只在本仓提交 —— 与本仓 README 的
   "双仓同步约定"一致：这类 PR 需在描述中注明"不影响 MCP 契约"。

---

## 11. 明确不做

- 不做反向同步（桌面 → 源）。
- 不删除本仓任何文件。
- 不用同步机制同步依赖声明、测试或 `pyproject.toml`。
- 不改写投影内容的导入路径（见第 7 节，属架构选型）。
- 不提供 Git hooks、不自动提交、不自动推送。
- 不在文档中作永久性断言：一切数量与状态均带观测日期。
