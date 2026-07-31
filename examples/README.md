# Leopard example programs

Sixteen complete, runnable programs, ordered as a curriculum — each one
introduces a specific part of the language, building on the ones before it.
Open any of them in the Leopard IDE and click Run, or from a terminal:

```bash
cd examples
leopard run 01_variables_and_types.lep
```

Run bare (no-window) scripts from inside this `examples/` folder — a few of
them write a small output file (e.g. `01_output.txt`) you can open afterward
to see what the program computed, since a bare script has no `print`
builtin (see lesson 01). GUI examples that reference a relative file path
(`controls_showcase.lep`'s icon button, `sound_demo.lep`'s chime) also
expect to be run from this folder.

## Part 1 — The language itself (no window)

| # | File | Covers |
|---|---|---|
| 1 | [`01_variables_and_types.lep`](01_variables_and_types.lep) | Assignment, the four value types, `str()`/`num()`, `.length`, 1-based list indexing |
| 2 | [`02_operators_and_expressions.lep`](02_operators_and_expressions.lep) | Every operator (`+ - * / % ^`, `&`, comparisons, `and`/`or`/`not`), why `+`/`&` are picky on purpose, and `eq` as a word alternative to `=` for equality only |
| 3 | [`03_control_flow.lep`](03_control_flow.lep) | `if`/`elseif`/`else`, `while`, `for..to..step` (including counting down), `break`, `continue` |
| 4 | [`04_functions.lep`](04_functions.lep) | Functions with and without `return`, recursion, and why a function can't mutate an outer variable by assigning to it |
| 5 | [`05_lists.lep`](05_lists.lep) | Building, growing (`.add()`), iterating, and rebuilding lists (there's no in-place remove or index-assignment — see below) |
| 6 | [`06_file_io.lep`](06_file_io.lep) | `write_file`/`append_file`/`read_file`/`delete_file`/`make_dir`/`remove_dir`/`file_exists` |

## Part 2 — Windows and controls

| # | File | Covers |
|---|---|---|
| 7 | [`greeter.lep`](greeter.lep) | The smallest complete window: a label, a textbox, a button, one event handler |
| 8 | [`controls_showcase.lep`](controls_showcase.lep) | Every control kind (textbox, textedit, label, button, bmpbutton, listbox, combobox, radiobutton, checkbox, groupbox) and most properties/events at once |
| 9 | [`dialogs.lep`](dialogs.lep) | `notice`/`confirm`/`ask`, plus the file/color/font picker dialogs |
| 10 | [`menus.lep`](menus.lep) | Full menu support: submenus, separators, a checkable item |

## Part 3 — The other window kinds

| # | File | Covers |
|---|---|---|
| 11 | [`turtle_demo.lep`](turtle_demo.lep) | A short first turtle-graphics program: pen state, movement, one filled shape |
| 12 | [`turtle_full.lep`](turtle_full.lep) | Every `graphics window` command: `go`/`turn`/`goto`/`place`/`home`/`north`, every shape (plain and filled), text, fonts, background |
| 13 | [`notes.lep`](notes.lep) | A `text window`: the implicit, fully-editable `page` control |
| 14 | [`sound_demo.lep`](sound_demo.lep) | `play_sound`/`stop_sound` and `play_music`/`pause_music`/`stop_music` (a small bundled WAV under `assets/` makes this runnable out of the box) |

## Part 4 — Putting it together

| # | File | Covers |
|---|---|---|
| 15 | [`fizzbuzz.lep`](fizzbuzz.lep) | Loops, conditionals, a function, string joining, and a list-backed control, all in one window |
| 16 | [`todo_capstone.lep`](todo_capstone.lep) | A small todo-list app: controls, events, functions, parallel lists standing in for "records," and saving state to a file on close |

Lessons 5 and 16 both hit the same real language limit worth knowing up
front: **`list[i] = value` doesn't work** — you can read an item (`list[i]`)
and append one (`.add()`), but not replace or remove one in place. Both
lessons show the standard workaround: build a fresh list with `.add()` and
reassign the whole variable to it. See `GRAMMAR.md`'s §15, open question 5,
for the full detail.

See `LANGUAGES/Leopard/LANGUAGE_GUIDE.md` for a prose walkthrough of the same
material, and `LANGUAGES/Leopard/GRAMMAR.md` for the complete, precise spec.
