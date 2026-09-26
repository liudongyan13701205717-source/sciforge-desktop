"""sciforge 桌面客户端命令行入口。"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence


def _cmd_serve(args: argparse.Namespace) -> int:
    """serve 子命令：占位实现，后续接入 MCP 服务。"""
    print("serve 子命令尚未实现（占位）")
    return 0


def _cmd_sessions(args: argparse.Namespace) -> int:
    """sessions 子命令：列出本地会话。"""
    from sessions.session_store import list_sessions

    sessions = list_sessions()
    if not sessions:
        print("（暂无会话）")
        return 0
    for s in sessions:
        print(f"{s['session_id']}\t{s['name']}\t{s['created_at']}")
    return 0


def _cmd_tools(args: argparse.Namespace) -> int:
    """tools 子命令：列出 agent 基础工具。"""
    from agent.tools import TOOL_REGISTRY

    for name, fn in TOOL_REGISTRY.items():
        doc = (fn.__doc__ or "").strip().splitlines()
        print(f"{name}\t{doc[0] if doc else ''}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="sciforge-desktop",
        description="sciforge 桌面客户端",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="启动本地服务（占位）")
    sub.add_parser("sessions", help="列出本地会话")
    sub.add_parser("tools", help="列出 agent 基础工具")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """命令行入口，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return _cmd_serve(args)
    if args.command == "sessions":
        return _cmd_sessions(args)
    if args.command == "tools":
        return _cmd_tools(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())