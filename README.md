# sciforge-desktop

sciforge 的桌面客户端。sciforge 项目以两种形态存在：

1. **MCP 服务器**（`sciforge` 仓库）：面向 agent 的 JSON-RPC-over-stdio 服务；
2. **桌面客户端**（本仓库）：面向人类的 PySide6 图形界面，通过 MCP 客户端与同一套核心能力交互。

两者是同一项目的两种形态，共享同一套核心逻辑（`core` 包）。核心同步在后续任务中完成，本仓库当前仅为骨架。

## 安装

PySide6 需要单独安装（注意：Python 3.14 暂无可用的 PySide6 wheel，请使用受支持的 Python 版本）：

```bash
pip install PySide6
```

## 离线模式

设置环境变量 `SCI_FORGE_OFFLINE=1` 可进入离线模式：所有网络工具（如 `web_search`）返回空结果，不发起任何网络请求。

## 命令行

```bash
sciforge-desktop serve      # 启动本地服务（占位）
sciforge-desktop sessions   # 列出本地会话
sciforge-desktop tools      # 列出 agent 基础工具
```

## 开发

```bash
# 语法检查
python -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read()) for f in glob.glob('**/*.py', recursive=True)]; print('SYNTAX OK')"
```