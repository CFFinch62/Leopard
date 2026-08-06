<!-- title: The Leopard IDE Guide -->

# The Leopard IDE Guide

A tour of the Leopard IDE — the editor, file browser, console, and the
handful of things that aren't obvious from just poking around. If you want
to learn the *language*, see `LANGUAGE_GUIDE.md` instead; this is about the
tool you write it in.

---

## Getting started

```bash
pip install -e ".[gui]"
leopard-ide
```

The IDE opens with a single untitled tab, a file browser on the left, and a
console at the bottom. Open a `.lep` file (**File → Open...**, or double-click
one in the file browser) and click **Run** on the toolbar.

---

## Layout

- **File browser** (left) — navigate the filesystem, bookmark folders you
  come back to, and open files by double-clicking.
- **Editor** (center) — tabbed, one tab per open file. Tabs are closable and
  reorderable by dragging.
- **Console** (bottom, by default) — output from **Run**, plus an input line
  for anything the running program reads from stdin.
- **Documentation panel** (hidden by default) — renders `LANGUAGE_GUIDE.md`,
  `LANGUAGE_SPEC.md`, or this guide right inside the IDE. Toggle it with
  **View → Toggle Documentation**, or open a specific doc from the **Help**
  menu.

**View → Console on Right** moves the console from below the editor to
beside it — the documentation panel follows along next to whichever one is
on the right. **View → Toggle File Browser** and **Toggle Console** hide
either panel entirely if you want the editor full-width.

---

## Editing

- **Syntax highlighting** for Leopard: keywords, builtins/turtle commands,
  strings, numbers, comments, operators, and `.property` access each get
  their own color, following whichever theme is active.
- **Line numbers** and **current-line highlight**, both toggleable in
  Preferences.
- **Auto-indent**: pressing Enter after a line ending in `:` (the start of a
  block — `if`, `while`, `function`, `window`, ...) indents the new line one
  level further, matching Leopard's indentation-delimited blocks. Also
  toggleable in Preferences.
- **Indent / Dedent Selection** (`Ctrl+]` / `Ctrl+[`) — shift the selected
  lines a tab stop in either direction.
- **Comment / Uncomment Selection** (`Ctrl+/`) — toggles a `# ` prefix on
  each selected line.
- **Find / Replace** (`Ctrl+F`) — a dialog for search, replace, and
  replace-all within the current tab.

## Running and building

- **Run** (toolbar, or `leopard run` equivalent) — executes the current
  tab's program. A bare script (no `window`/`text window`/`graphics window`
  header) runs straight through to completion; a windowed program opens its
  window using the IDE's own Qt event loop. Errors — syntax or runtime —
  print to the console with a line number, the same format `leopard run`
  itself uses on the command line.
- **Build** (toolbar) — compiles the current program into a standalone,
  double-clickable executable via PyInstaller, the same thing
  `leopard build script.lep` does from the command line. No Python
  installation is required on the machine that runs the result. Progress and
  any errors print to the console.
- **Clear Console** — empties the console pane without affecting anything
  else.

---

## File browser

- Double-click a file to open it in a new (or existing) editor tab.
- The **★** button bookmarks the currently browsed folder; bookmarks appear
  in the list above the tree and persist across restarts. Right-click a
  bookmark to remove it.
- Right-click inside the tree for **New File...**, **New Folder...**,
  **Rename...** (files/folders you created), **Delete**, and **Refresh**.

---

## Preferences (Ctrl+,)

Four tabs:

- **Editor** — font size, tab width, word wrap, line numbers, current-line
  highlight, auto-indent.
- **Console** — font size.
- **Theme** — pick the active color theme (see below); the same list as
  the **Theme** menu.
- **Shortcuts** — a reference list of the current keyboard shortcuts (not
  yet editable from here — see the **Edit** and **Help** menus for the live
  actions).

Window size, splitter positions, and the active theme are all remembered
between sessions automatically — nothing to save by hand.

## Themes

Six built in, switchable from the **Theme** menu or the Preferences dialog:
`dark`, `light`, `grey`, `solarized_light`, `solarized_dark`, and
`high_contrast`. Themes affect the whole IDE chrome as well as the editor
and console color scheme — not just syntax colors.

---

## Documentation panel

**Help → Language Guide**, **Help → Language Spec**, and **Help → IDE
Guide** each open the corresponding file from this project's `user-docs/`
folder in the panel on the right (or left, if the console is on the right).
Internal links between the three documents resolve in place; an external
`http(s)` link opens in your system browser instead.

---

## Where to go next

- `LANGUAGE_GUIDE.md` — a tutorial through the Leopard language itself, with
  every example runnable straight from this IDE.
- `LANGUAGE_SPEC.md` — the complete, flat language reference.
- **[examples/](../examples/)** — sixteen sample programs, from bare-script
  fundamentals through every window kind to two capstone projects. Open any
  of them here and click Run.
