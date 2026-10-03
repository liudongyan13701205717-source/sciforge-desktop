# 获取支持

本文件说明 sciforge-desktop 的支持渠道，以及提问前应先自查的内容。

English summary: see the bottom section.

---

## 先查文档

大多数问题在下列文档中有答案：

| 文档 | 覆盖内容 |
| --- | --- |
| [`README.md`](../README.md) | 项目定位、当前状态、界面导览、命令行、已知缺陷 |
| [`docs/installation.md`](../docs/installation.md) | 安装、Python / PySide6 版本兼容性、环境变量 |
| [`docs/quickstart.md`](../docs/quickstart.md) | 上手操作 |
| [`docs/mcp-bridge.md`](../docs/mcp-bridge.md) | MCP 桥接层用法 |
| [`docs/desktop-core-relationship.md`](../docs/desktop-core-relationship.md) | 桌面版与 MCP 版的关系 |
| [`SECURITY.md`](../SECURITY.md) | 安全边界与漏洞报告 |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | 开发与提交流程 |

---

## 提问前请先确认

本仓库处于 `0.1.0` 骨架阶段，以下限制**已知且有记录**（依据 2026-09-26 的代码核对）：

1. **`sciforge-desktop` 命令可能不可用** —— entry point 缺包前缀，安装后可能无法导入。改用 `python -m cli.main <子命令>`。
2. **界面只有外壳** —— 左侧导航三项与「帮助 → 关于」均未连接槽，中央为占位标签。
3. **`cli serve` 是占位** —— 只打印提示，不启动任何服务。
4. **MCP 桥接无调用方** —— 桌面端尚未调用 `MCPClient`，因此界面里不会执行任何 MCP 工具。
5. **没有测试** —— 0 个测试用例，无法通过 `pytest` 验证；请用 AST 语法检查代替。
6. **PySide6 与 Python 3.14** —— 2026-09-26 实测该版本无 PySide6 wheel，需换用已提供 wheel 的 Python 版本。
7. **学科与论文工具不在本仓** —— 261 门学科、65 个 MCP 工具、46 个数据库连接器均在 [`sciforge`](https://github.com/liudongyan13701205717-source/sciforge) 仓。

若你的问题命中以上任一条，无需提 Issue。

---

## 支持渠道

| 需求 | 渠道 |
| --- | --- |
| 报告可复现的错误 | [Bug 报告模板](ISSUE_TEMPLATE/bug_report.md) |
| 提出新功能 | [功能请求模板](ISSUE_TEMPLATE/feature_request.md) |
| 使用问题 / 文档缺口 | 公开 Issue，标题前缀 `[Question]` |
| 安全漏洞 | **不要**用公开 Issue，见 [`SECURITY.md`](../SECURITY.md) |
| 学科 / 论文工具 / 连接器 | [`sciforge` 仓的 Issue](https://github.com/liudongyan13701205717-source/sciforge/issues) |
| 行为准则相关 | 见 [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) |

---

## 提问的效率建议

提问时请附上：

- `python -V` 的输出
- `pip show PySide6` 的输出（未安装则说明）
- 操作系统与版本
- 你执行的确切命令
- 完整错误文本（先脱敏，注意路径、令牌与个人信息）
- 是否处于离线模式（`SCI_FORGE_OFFLINE=1`）

这些信息能显著缩短来回确认的轮次。

---

## 响应预期

本项目为个人维护的早期开源项目，**不承诺响应时限**。Issue 可能需要较长时间才会得到回复；在此期间，先依据文档中的「已知缺陷」排查往往更有效。

---

## English Summary

- Check the docs first: `README.md`, `docs/installation.md`, `docs/quickstart.md`,
  `docs/mcp-bridge.md`, `docs/desktop-core-relationship.md`.
- Seven limitations are already documented (as reviewed on 2026-09-26): the
  `sciforge-desktop` console script may not import after install (entry point
  lacks a package qualifier — use `python -m cli.main <subcommand>`); the GUI is
  a shell with unwired navigation and About action; `cli serve` is a placeholder;
  the MCP bridge has no caller; there are no tests; PySide6 had no wheel for
  Python 3.14; and disciplines / paper tools / connectors live in the `sciforge`
  repository, not here.
- Report bugs and features via the issue templates. **Never** report security
  issues publicly — use the private channel in `SECURITY.md`.
- Include `python -V`, `pip show PySide6`, OS and version, the exact command,
  the full error text (redacted), and whether offline mode was active.
- No response-time commitment is made for this early-stage, single-maintainer
  project.
