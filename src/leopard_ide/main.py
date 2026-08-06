import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from leopard_ide.app.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Leopard IDE")
    app.setOrganizationName("LeopardIDE")

    if hasattr(sys, "_MEIPASS"):
        # Frozen (PyInstaller) build: build_ide.py bundles leopard-icon.svg
        # and user-docs/ directly at the bundle root via --add-data.
        root_dir = Path(sys._MEIPASS)
    else:
        # main.py -> leopard_ide -> src -> repo root
        root_dir = Path(__file__).resolve().parent.parent.parent

    icon_path = root_dir / "leopard-icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(docs_dir=root_dir / "user-docs")
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
