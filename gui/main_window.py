"""sciforge 桌面客户端主窗口（PySide6 懒加载）。

PySide6 在 Python 3.14 下暂无可用 wheel，因此本模块顶层不导入
PySide6；真正的 QMainWindow 子类在首次实例化时才创建，保证模块
可在未安装 PySide6 的环境中安全导入。
"""

from __future__ import annotations

import sys
from typing import Any


def _create_main_window_class() -> type:
    """延迟导入 PySide6 并构造 QMainWindow 子类。"""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel, QListWidget, QMainWindow, QSplitter

    class MainWindow(QMainWindow):
        """sciforge 桌面客户端主窗口。"""

        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("sciforge 桌面客户端")
            self.resize(960, 640)
            self._build_menu_bar()
            self._build_status_bar()
            self._build_body()

        def _build_menu_bar(self) -> None:
            """构建 File / Help 菜单栏。"""
            menubar = self.menuBar()
            file_menu = menubar.addMenu("文件(&F)")
            file_menu.addAction("退出(&Q)", self.close)
            help_menu = menubar.addMenu("帮助(&H)")
            help_menu.addAction("关于(&A)")

        def _build_status_bar(self) -> None:
            """构建状态栏。"""
            self.statusBar().showMessage("就绪")

        def _build_body(self) -> None:
            """构建左侧导航列表与中央占位面板。"""
            self.nav_list = QListWidget()
            self.nav_list.addItems(["会话", "工具", "设置"])
            self.placeholder = QLabel("sciforge 桌面客户端骨架 — 功能开发中")
            self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            splitter = QSplitter()
            splitter.addWidget(self.nav_list)
            splitter.addWidget(self.placeholder)
            self.setCentralWidget(splitter)

    return MainWindow


class MainWindow:
    """主窗口（QMainWindow 子类，PySide6 懒加载）。

    首次实例化时才导入 PySide6 并创建真正的 QMainWindow 子类，
    因此本模块可在未安装 PySide6 的环境中安全导入。
    """

    _impl: type | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._impl is None:
            cls._impl = _create_main_window_class()
        return cls._impl(*args, **kwargs)


def main() -> int:
    """创建 QApplication 并显示主窗口。"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())