"""agent 基础工具（仅标准库实现，离线安全）。

每个工具返回统一字典：成功为 {"ok": True, "result": ...}，
失败为 {"ok": False, "error": str}。
"""

from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

_OFFLINE = os.environ.get("SCI_FORGE_OFFLINE") == "1"

# 允许访问的根目录：用户主目录与当前工作目录
_ALLOWED_ROOTS: tuple[Path, ...] = (Path.home(), Path.cwd())

_USER_AGENT = "Mozilla/5.0 (sciforge-desktop/0.1.0)"


def _is_within_roots(path: Path) -> bool:
    """判断解析后的路径是否位于任一允许根目录内。"""
    resolved = path.resolve()
    for root in _ALLOWED_ROOTS:
        root_resolved = root.resolve()
        if resolved == root_resolved or root_resolved in resolved.parents:
            return True
    return False


def _safe_path(path: str) -> Path:
    """将字符串路径解析为 Path 并做安全校验。

    Raises:
        PermissionError: 路径超出允许根目录（含 `..` 越界）。
    """
    p = Path(path).expanduser()
    if not _is_within_roots(p):
        raise PermissionError(f"路径超出允许范围: {path}")
    return p


class _DDGResultParser(HTMLParser):
    """从 DuckDuckGo HTML 结果页提取标题与链接。"""

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._capture = False
        self._href: str | None = None
        self._chars: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a" and "result__a" in (dict(attrs).get("class") or ""):
            self._capture = True
            self._href = dict(attrs).get("href")
            self._chars = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._chars.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture:
            title = "".join(self._chars).strip()
            if title and self._href:
                self.results.append({"title": title, "url": self._href})
            self._capture = False
            self._href = None


def web_search(query: str, limit: int = 5) -> list[dict[str, str]]:
    """使用 DuckDuckGo HTML 端点执行网络搜索。

    离线模式（SCI_FORGE_OFFLINE=1）或网络错误时返回空列表。
    """
    if _OFFLINE:
        return []
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, ValueError):
        return []
    parser = _DDGResultParser()
    parser.feed(html)
    return parser.results[:limit]


def read_file(path: str) -> dict[str, Any]:
    """读取文本文件内容。"""
    try:
        p = _safe_path(path)
    except PermissionError as exc:
        return {"ok": False, "error": str(exc)}
    if not p.is_file():
        return {"ok": False, "error": f"文件不存在: {path}"}
    try:
        return {"ok": True, "result": p.read_text(encoding="utf-8")}
    except (OSError, UnicodeDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def write_file(path: str, content: str) -> dict[str, Any]:
    """写入文本文件（自动创建父目录）。"""
    try:
        p = _safe_path(path)
    except PermissionError as exc:
        return {"ok": False, "error": str(exc)}
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "result": str(p)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def list_files(path: str) -> dict[str, Any]:
    """列出目录内容（条目名，排序后返回）。"""
    try:
        p = _safe_path(path)
    except PermissionError as exc:
        return {"ok": False, "error": str(exc)}
    if not p.is_dir():
        return {"ok": False, "error": f"目录不存在: {path}"}
    try:
        entries = sorted(e.name for e in p.iterdir())
        return {"ok": True, "result": entries}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def make_dir(path: str) -> dict[str, Any]:
    """递归创建目录。"""
    try:
        p = _safe_path(path)
    except PermissionError as exc:
        return {"ok": False, "error": str(exc)}
    try:
        p.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "result": str(p)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def delete_file(path: str) -> dict[str, Any]:
    """删除文件（仅文件，不删除目录）。"""
    try:
        p = _safe_path(path)
    except PermissionError as exc:
        return {"ok": False, "error": str(exc)}
    if not p.is_file():
        return {"ok": False, "error": f"文件不存在: {path}"}
    try:
        p.unlink()
        return {"ok": True, "result": str(p)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


TOOL_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "make_dir": make_dir,
    "delete_file": delete_file,
}