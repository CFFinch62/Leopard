"""
build_ide.py — Leopard IDE packaging helper
=============================================
Cleans previous build artefacts, then calls PyInstaller to produce a
self-contained Leopard IDE binary in dist/LeopardIDE/, bundling
leopard-icon.svg and user-docs/ alongside the leopard_ide and leopard_lang
packages under src/.

This is a separate, optional distribution path from the Debian package
(packaging/stage.sh + dpkg-deb, see packaging/README.md) — a single
portable binary instead of an apt-installed system package. Most users on
Linux Mint should just use the .deb; this is for a standalone executable on
another OS, or outside apt.

The script adds the project venv's site-packages to sys.path BEFORE
invoking PyInstaller so that dependencies are found even when the system
Python (rather than the activated venv) runs this file.

Usage:
    python3 build_ide.py          # with or without venv activated
"""

import os
import pathlib
import platform
import shutil
import sys

APP_NAME    = "LeopardIDE"
ENTRY_POINT = "src/leopard_ide/main.py"
SCRIPT_DIR  = pathlib.Path(__file__).parent.resolve()
SRC_DIR     = SCRIPT_DIR / "src"


# ──────────────────────────────────────────────────────────────────────
# 1. Ensure the venv site-packages are on sys.path so PyInstaller can
#    find all project dependencies regardless of how this script was run.
# ──────────────────────────────────────────────────────────────────────

def _inject_venv_paths() -> None:
    for venv_name in (".venv", "venv"):
        venv_dir = SCRIPT_DIR / venv_name
        if not venv_dir.exists():
            continue
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_pkgs = venv_dir / "lib" / py_ver / "site-packages"
        if site_pkgs.exists() and str(site_pkgs) not in sys.path:
            sys.path.insert(0, str(site_pkgs))
            print(f"[build_ide] Added venv site-packages to path: {site_pkgs}")
        return

_inject_venv_paths()


# ──────────────────────────────────────────────────────────────────────
# 2. Now import PyInstaller (may come from venv after the path injection)
# ──────────────────────────────────────────────────────────────────────

import PyInstaller.__main__  # noqa: E402  (must be after path injection)


# ──────────────────────────────────────────────────────────────────────
# 3. Helpers
# ──────────────────────────────────────────────────────────────────────

def clean_build_dirs() -> None:
    print("Cleaning build directories...")
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)


def get_args() -> list[str]:
    system = platform.system()
    sep    = ";" if system == "Windows" else ":"  # PyInstaller --add-data separator

    args = [
        "--name",    APP_NAME,
        "--clean",
        "--noconfirm",
        "--windowed",
        "--paths",   str(SRC_DIR),
        "--hidden-import", "PyQt6",
        "--add-data", f"leopard-icon.svg{sep}.",
        "--add-data", f"user-docs{sep}user-docs",
    ]

    if system == "Darwin":
        args += ["--target-architecture", "universal2"]

    args.append(ENTRY_POINT)
    return args


# ──────────────────────────────────────────────────────────────────────
# 4. Build
# ──────────────────────────────────────────────────────────────────────

def build() -> None:
    clean_build_dirs()

    args = get_args()

    print(f"Building {APP_NAME} for {platform.system()} …")
    print()

    try:
        PyInstaller.__main__.run(args)
        print()
        print(f"Build complete!  →  dist/{APP_NAME}/")
    except Exception as exc:
        print(f"Build failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    build()
