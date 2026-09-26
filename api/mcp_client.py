"""MCP JSON-RPC-over-stdio 客户端（仅标准库实现）。

通过子进程的 stdin/stdout 与 MCP 服务器通信：请求写入 stdin，
响应与通知从 stdout 读取。消息格式为 JSON-RPC 2.0，每行一条。
"""

from __future__ import annotations

import json
import queue
import subprocess
import threading
from typing import Any, Iterator

_PROTOCOL_VERSION = "2024-11-05"


class MCPClient:
    """与 MCP 服务器子进程通信的 JSON-RPC 客户端。"""

    def __init__(self) -> None:
        self._proc: subprocess.Popen[str] | None = None
        self._request_id = 0
        self._responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self._notifications: queue.Queue[dict[str, Any]] = queue.Queue()
        self._reader: threading.Thread | None = None
        self._id_lock = threading.Lock()

    def start(self, server_cmd: list[str]) -> None:
        """启动 MCP 服务器子进程并开启 stdout 读取线程。

        Args:
            server_cmd: 服务器启动命令，如 ["python", "-m", "sciforge.server"]。
        """
        if self._proc is not None:
            raise RuntimeError("MCP 客户端已启动")
        self._proc = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        """持续读取 stdout 上的 JSON-RPC 消息并分发到队列。"""
        assert self._proc is not None and self._proc.stdout is not None
        for line in self._proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in msg:
                self._responses.put(msg)
            else:
                self._notifications.put(msg)

    def _next_id(self) -> int:
        """生成自增请求 id（线程安全）。"""
        with self._id_lock:
            self._request_id += 1
            return self._request_id

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """发送请求并等待对应 id 的响应。"""
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("MCP 客户端未启动")
        msg_id = self._next_id()
        payload = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
        self._proc.stdin.write(json.dumps(payload) + "\n")
        self._proc.stdin.flush()
        while True:
            resp = self._responses.get()
            if resp.get("id") == msg_id:
                return resp

    def initialize(self) -> dict[str, Any]:
        """发送 initialize 请求并返回服务器能力信息。

        成功后自动发送 notifications/initialized 通知。
        """
        resp = self._request(
            "initialize",
            {
                "protocolVersion": _PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "sciforge-desktop", "version": "0.1.0"},
            },
        )
        self.notify("notifications/initialized", {})
        return resp

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """调用服务器上的工具并返回结果。"""
        return self._request("tools/call", {"name": name, "arguments": arguments})

    def notify(self, method: str, params: dict[str, Any]) -> None:
        """发送一条通知（无 id，不等待响应）。"""
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("MCP 客户端未启动")
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        self._proc.stdin.write(json.dumps(payload) + "\n")
        self._proc.stdin.flush()

    def notifications(self) -> Iterator[dict[str, Any]]:
        """迭代服务器主动推送的通知（阻塞式）。"""
        while True:
            yield self._notifications.get()

    def close(self) -> None:
        """终止服务器子进程并清理资源。"""
        if self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None