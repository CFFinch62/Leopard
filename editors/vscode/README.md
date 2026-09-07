# Leopard Language — VS Code extension

Syntax highlighting, editor behaviours, snippets and one-key running for
[Leopard](https://github.com/CFFinch62/Leopard) (`.lep` files).

## Getting Leopard

This extension highlights and runs `.lep` files — it does not bundle the
language. Get it from GitHub:

**<https://github.com/CFFinch62/Leopard>**

Leopard is free and open source under the **MIT License**, as is this extension.

```sh
git clone https://github.com/CFFinch62/Leopard.git
cd Leopard
pip install -e ".[gui]"
```

That puts `leopard` on your `PATH`. The `[gui]` extra pulls in PyQt6, which any
program with a `window` needs; a plain script needs only `pip install -e .`.
If `leopard` is inside a virtualenv, point `leopard.interpreterPath` (below) at
it with an absolute path.

## What it does

**Syntax highlighting** for all 147 reserved words, split by the role
`GRAMMAR.md` gives each one, so a program reads by structure rather than as a
wall of one colour: control flow, control declarations (`button`, `listbox`,
`graphics`…), events (`on click`, `on change`), the turtle-graphics commands,
and the 76 builtin actions each get their own scope. Control names bound with
`as` are highlighted as definitions, `.property` access is distinguished from
dotted turtle calls, and `&` is scoped as string concatenation rather than
bitwise-and.

**Editor behaviours** — `#` comment toggling, bracket matching, auto-closing
pairs, indentation after a line ending in `:`, automatic dedent on `else`,
`elseif`, `case`, `default` and `until`, and offside-rule code folding.

**Snippets** for window and control declarations, every event handler, the loop
and `switch` forms, menus, and a turtle pen-and-draw starter.

**Commands** — each also available from the Command Palette:

| Command | Default key | What it runs |
|---|---|---|
| Leopard: Run File | `Ctrl+F5` | `leopard run` |
| Leopard: Check for Errors | `Ctrl+Shift+F5` | `leopard check` |
| Leopard: Build Standalone Executable | — | `leopard build` |

**Problems panel** — errors become squiggles in the editor. **Check for
Errors** parses without executing, so a script that opens dialogs, writes files
or plays sound stays inert while you are only asking whether it parses. A
file's errors are cleared as soon as you edit it.

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `leopard.interpreterPath` | `leopard` | Path to the `leopard` command |
| `leopard.saveBeforeRun` | `true` | Save before running, checking or building |
| `leopard.runInTerminal` | `true` | Run in a terminal so `input()` and windows work |
| `leopard.checkOnSave` | `false` | Run `leopard check` on every save |
| `leopard.buildOutputDir` | `dist` | Directory passed to `leopard build -o` |

## Why Run and Check are separate

Leopard reports errors as `Line 12: message` — no filename, no column — because
that is what a beginner needs to read. It is also not enough for a task runner
to attribute an error to a file.

So the extension parses that format itself and pins those diagnostics to the
file it just ran. `leopard check` sidesteps the problem entirely by printing
`<path>:<line>: <message>`, which is why it is the command bound to a key and
the one `tasks.example.json` attaches a problem matcher to.

Keep `leopard.runInTerminal` on — it is what makes `input()` and GUI windows
behave — and use **Check for Errors** when you want the Problems panel.

## Installing from source

```sh
cd editors/vscode
npx @vscode/vsce package
code --install-extension leopard-language-0.1.0.vsix
```

## Without the extension

`tasks.example.json` in this directory sets up the same check, run and build
tasks using only VS Code's built-in task runner and problem matcher — no
extension required. Copy it to your project's `.vscode/tasks.json`.

## License

MIT — see [LICENSE](LICENSE).
