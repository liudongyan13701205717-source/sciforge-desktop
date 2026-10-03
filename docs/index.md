# sciforge-desktop 文档

本目录是 sciforge 桌面客户端的面向用户文档。

> 文档状态基于 2026-09-26 对仓库代码的逐文件核对。所有会随时间变化的观测（依赖可用性、版本兼容性、功能计数）均标注观测日期，并使用条件式表述。

---

## 文档清单

| 文档 | 读者 | 内容 |
| --- | --- | --- |
| [installation.md](installation.md) | 首次使用者 | 安装、Python / PySide6 版本兼容性、环境变量、故障排查 |
| [quickstart.md](quickstart.md) | 首次使用者 | 5 分钟跑通命令行、界面、会话、本地工具 |
| [mcp-bridge.md](mcp-bridge.md) | 开发者 | MCP 桥接层：协议版本、握手、消息格式、API 清单、示例 |
| [desktop-core-relationship.md](desktop-core-relationship.md) | 维护者 / 贡献者 | 桌面版与 MCP 版的核心同步现状与目标形态 |
| [index.md](index.md) | 全部 | 本文件，总览与阅读路径 |

仓库根目录另有面向全部读者的概览文档：

| 文档 | 内容 |
| --- | --- |
| [README.md](../README.md) | 中文主文档：定位、当前状态、界面导览、命令行、已知缺陷 |
| [README_EN.md](../README_EN.md) | 英文完整版 |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 提交流程、双仓同步规则、代码风格 |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | 行为准则（Contributor Covenant v2.1） |
| [SECURITY.md](../SECURITY.md) | 安全边界与漏洞报告流程 |
| [CHANGELOG.md](../CHANGELOG.md) | 版本历史（Keep a Changelog） |

---

## 阅读路径

### 我想先用起来

```
installation.md  →  quickstart.md  →  README.md 的「界面导览」
```

### 我遇到了报错

```
SUPPORT.md（在 .github/）  →  README.md 的「已知缺陷与待修复项」  →  installation.md 的「故障排查」
```

### 我想接入 MCP 服务器

```
installation.md（准备 sciforge）  →  mcp-bridge.md  →  README.md 的「与 MCP 版的关系」
```

### 我想参与开发

```
CONTRIBUTING.md  →  desktop-core-relationship.md（双仓边界）  →  mcp-bridge.md（接口细节）
```

---

## 现状速览

**本仓库处于骨架阶段**，以下为 2026-09-26 的实测状态：

| 能力 | 状态 |
| --- | --- |
| 命令行 `sessions` / `tools` | 可用 |
| 本地会话 CRUD | 可用 |
| 6 个本地 agent 工具 | 可用 |
| `MCPClient` 类 | 已实现，但本仓内无调用方 |
| 图形界面 | 仅外壳，导航与「关于」未连接槽 |
| `cli serve` | 占位 |
| `core/` 共享核心 | 空占位（3 行 docstring） |
| 两仓核心同步 | 未建立 |
| 测试 | 0 个用例，无 pytest 配置 |
| entry point | 缺包前缀，安装后可能无法导入 |

细节与成因见 [desktop-core-relationship.md](desktop-core-relationship.md) 与 README 的「已知缺陷与待修复项」。

---

## 文档约定

本项目的文档遵循以下约定：

1. **中文为主，英文为辅。** 根目录 `README.md` 为中文主文档，`README_EN.md` 是**独立完整**的英文文档（不是中文版的压缩版）。
2. **观测数据必须标注日期。** 涉及依赖可用性、版本兼容性、接口计数等会随时间变化的内容，一律写明观测日期，并使用条件式表述（「当 X 条件下可采用 Y 方法」），不写永久性断言。
3. **不把待办写成已完成。** 例如桌面版核心与 MCP 版同步，在落地前一律描述为待办。
4. **已知缺陷写在明处。** 打包缺陷、测试缺口、环境限制都进文档，不留给使用者去踩。
