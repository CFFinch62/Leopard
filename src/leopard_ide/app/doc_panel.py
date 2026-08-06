from pathlib import Path

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class DocPanel(QWidget):
    """Markdown viewer for files in the user-docs directory.

    Internal links between docs (e.g. Language Guide <-> Language Spec)
    resolve in place instead of being handed to the OS; anything else
    (an external http(s) link) opens in the system browser.
    """

    closed = pyqtSignal()

    def __init__(self, docs_dir: Path, parent=None):
        super().__init__(parent)
        self._docs_dir = docs_dir

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = QWidget(self)
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(6, 3, 3, 3)
        header_layout.setSpacing(0)

        self.title_label = QLabel("DOCUMENTATION")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)

        self.close_button = QPushButton("✕")
        self.close_button.setFlat(True)
        self.close_button.setFixedSize(20, 20)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self._on_close_clicked)
        header_layout.addWidget(self.close_button)

        layout.addWidget(self._header)

        self.browser = QTextBrowser(self)
        self.browser.setOpenLinks(False)
        self.browser.setOpenExternalLinks(False)
        self.browser.anchorClicked.connect(self._on_anchor_clicked)
        layout.addWidget(self.browser)

    def show_doc(self, filename: str, title: str) -> None:
        self.title_label.setText(f"  {title.upper()}")
        self._load_doc(filename)
        self.show()

    def _load_doc(self, filename: str) -> None:
        path = self._docs_dir / filename
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            self.browser.setPlainText(f"Could not load {filename}.")
            return
        self.browser.setSearchPaths([str(self._docs_dir)])
        self.browser.setMarkdown(text)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        if not url.scheme() or url.scheme() == "file":
            target = Path(url.path()).name
            if target.endswith(".md"):
                self._load_doc(target)
                return
        QDesktopServices.openUrl(url)

    def _on_close_clicked(self) -> None:
        self.hide()
        self.closed.emit()

    def apply_theme(self, theme) -> None:
        self._header.setStyleSheet(
            f"QWidget {{ background-color: {theme.panel_background}; "
            f"border-bottom: 1px solid {theme.panel_border}; }}"
            f"QLabel {{ color: {theme.foreground}; font-weight: bold; font-size: 11px; "
            f"background: transparent; border: none; }}"
        )
        self.close_button.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {theme.foreground}; border: none; }}"
            f"QPushButton:hover {{ background-color: {theme.button_hover}; }}"
        )
        self.browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.editor_background}; "
            f"color: {theme.foreground}; border: none; }}"
        )
