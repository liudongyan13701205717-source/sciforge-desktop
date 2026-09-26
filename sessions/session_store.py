"""本地 JSON 会话存储（仅标准库实现）。

会话文件保存在 ~/.sciforge-desktop/sessions/{session_id}.json，
每个文件包含 {"session_id", "name", "created_at", "data"}。
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# 会话 id 允许的字符集：uuid4().hex 为 32 位小写十六进制，另允许连字符。
_SESSION_ID_CHARS = frozenset("0123456789abcdefABCDEF-")


def _sessions_dir() -> Path:
    """返回会话存储目录（~/.sciforge-desktop/sessions）。"""
    return Path.home() / ".sciforge-desktop" / "sessions"


def _session_path(session_id: str) -> Path:
    """返回单个会话文件的路径（严格校验 session_id，防路径穿越）。

    校验分两层：
    1. 字符白名单——非空且每个字符都属于 [0-9a-fA-F-]；
    2. 兜底——resolve() 后必须仍位于会话目录内部。

    Raises:
        ValueError: session_id 非法，或解析后路径逃出会话目录。
    """
    if not isinstance(session_id, str) or not session_id:
        raise ValueError(f"路径超出允许范围: {session_id}")
    if any(ch not in _SESSION_ID_CHARS for ch in session_id):
        raise ValueError(f"路径超出允许范围: {session_id}")
    p = _sessions_dir() / f"{session_id}.json"
    if _sessions_dir().resolve() not in p.resolve().parents:
        raise ValueError(f"路径超出允许范围: {session_id}")
    return p


def create_session(name: str) -> str:
    """创建新会话并返回其 session_id（完整数据可用 load_session 读回）。"""
    session_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "session_id": session_id,
        "name": name,
        "created_at": now,
        "data": {},
    }
    _sessions_dir().mkdir(parents=True, exist_ok=True)
    _session_path(session_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return session_id


def list_sessions() -> list[dict[str, Any]]:
    """列出所有会话的元数据（不含 data 内容）。"""
    d = _sessions_dir()
    if not d.exists():
        return []
    result: list[dict[str, Any]] = []
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        meta = {k: data.get(k) for k in ("session_id", "name", "created_at")}
        if meta["session_id"] is None:
            # 防御：跳过缺少 session_id 的文件。
            continue
        result.append(meta)
    return result


def load_session(session_id: str) -> dict[str, Any] | None:
    """按 id 加载会话；不存在或文件损坏时返回 None。

    Raises:
        ValueError: session_id 非法（含路径穿越尝试）。
    """
    p = _session_path(session_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_session(session_id: str, data: dict[str, Any]) -> None:
    """保存会话数据（覆盖式写入）。

    Raises:
        ValueError: session_id 非法（含路径穿越尝试）。
        FileNotFoundError: 会话不存在。
    """
    path = _session_path(session_id)
    existing = load_session(session_id)
    if existing is None:
        raise FileNotFoundError(f"会话不存在: {session_id}")
    existing["data"] = data
    path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def delete_session(session_id: str) -> bool:
    """删除会话文件；文件原本存在则返回 True，否则返回 False。

    Raises:
        ValueError: session_id 非法（含路径穿越尝试）。
    """
    p = _session_path(session_id)
    if not p.exists():
        return False
    p.unlink()
    return True