# Debian packaging for Leopard

This folder contains a self-contained Debian package layout for installing:

- the Leopard language runtime and CLI
- the companion Leopard IDE
- a desktop launcher and Leopard icon

## Structure

- packaging/deb/DEBIAN/ control, maintainer scripts
- packaging/deb/usr/bin/ launcher scripts for `leopard` and `leopard-ide`
- packaging/deb/usr/share/applications/ desktop entry
- packaging/deb/usr/share/icons/hicolor/scalable/apps/ Leopard icon
- packaging/deb/opt/leopard/ staged application tree

## Build

From the repository root:

```bash
chmod 755 packaging/deb/DEBIAN/postinst packaging/deb/DEBIAN/postrm \
  packaging/deb/usr/bin/leopard packaging/deb/usr/bin/leopard-ide

dpkg-deb --build packaging/deb packaging/leopard-lang_0.3.0-1_all.deb
```

## Install on Linux Mint

```bash
sudo dpkg -i packaging/leopard-lang_0.3.0-1_all.deb
sudo apt-get install -f
```

## Notes

The package currently uses a simple staged install layout and wrapper scripts so it does not depend on folders outside this repository tree.

The `leopard build` command (compiles a `.lep` script to a standalone executable) uses PyInstaller, but PyInstaller is not packaged for apt on Debian/Ubuntu/Mint, so it is intentionally **not** a package dependency. `leopard build` detects that it's missing and prints a message instead of crashing. To use that feature, install PyInstaller yourself, e.g.:

```bash
pip install --user pyinstaller
```

Everything else (the `leopard` CLI/interpreter and the Leopard IDE) works without it.
