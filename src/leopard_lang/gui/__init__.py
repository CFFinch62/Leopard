"""GUI runtime: maps window/control AST onto PyQt6 widgets (needs the `gui` extra).

Standalone-first (GRAMMAR.md Phase 4+): `leopard run window.lep` hosts its own
`QApplication` via `app_host.run_window()`. The IDE (Phase 9) reuses the exact same
function, passing its own already-running `QApplication` instead.
"""
