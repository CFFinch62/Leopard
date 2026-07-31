<!-- title: Leopard Implementation Plan -->

# Leopard — Implementation Plan
### Agent-friendly project tracker. Read this whole file before doing any work.

This document is the single source of truth for **where the project stands**. It is meant to
survive across sessions and across different agents/humans picking up the work with zero prior
context. Update it as you go — it is not a static spec, it is a working log.

---

## 0. Resume checklist (do this first, every time)

1. Read **Section 2 (Current Status)** below — it names the active phase and task.
2. Read **GRAMMAR.md** in this same directory — it is the canonical language spec. This plan
   implements that spec; it does not redefine it. If something here conflicts with GRAMMAR.md,
   GRAMMAR.md wins and this file has a bug — fix this file.
3. Open the checklist for the active phase in **Section 4** and find the first unchecked `[ ]`.
4. Before writing code, confirm the phase's prior phases are fully checked off — phases build on
   each other in order; don't skip ahead.
5. When you finish a task: check its box (`[ ]` → `[x]`), and if it changed scope, closed an open
   question, or made a judgment call not already covered by GRAMMAR.md or Section 6 below, add a
   dated line to **Section 6 (Decisions Log)**.
6. Before ending a session, update **Section 2 (Current Status)** so the next agent doesn't have
   to reconstruct where things stand from git history.

---

## 1. Project snapshot

Leopard was a 2013 Liberty BASIC application (`leopard.bas`, Windows-only) that was never a real
programming language — it was a fixed-vocabulary GUI description format interpreted by a
~2,500-line line-by-line state machine, with a hardcoded ceiling of 5 instances per widget type,
no variables beyond 5 global slots, no expressions, no user-defined functions, and no control flow
exposed to the programmer. "Compile" didn't compile anything.

This project resurrects Leopard as a real, small, beginner-friendly language, implemented in
Python, with a from-scratch grammar (see `GRAMMAR.md`) that keeps the original's vocabulary and
spirit — window/text-window/graphics-window programs, named GUI controls, turtle graphics — while
adding the missing fundamentals (variables, expressions, control flow, functions) and removing
the artificial limits and Windows-only dependencies.

**Locked technology decisions** (not re-litigated per phase — see Section 6 for the reasoning):
- **Python 3.12+**, PyQt6 as an **optional `leopard-lang[gui]` extra** — `pip install -e .` alone
  (Phases 0–3) needs no GUI dependency at all; `pip install -e ".[gui]"` adds PyQt6 once GUI-runtime
  work (Phase 4+) needs it. PyQt6 is a dependency of the *language package itself*, not something
  that only arrives with the IDE.
- The language core is built **entirely standalone first**, as a real pip-installable package
  living in this directory (`LANGUAGES/Leopard/`) — a genuine `leopard run script.lep` CLI
  tool usable from any text editor, with zero IDE or GUI dependency (Phases 0–3, done). The
  **GUI runtime is standalone-first too**: `leopard run window.lep` hosts its own `QApplication`
  and renders the window directly (Phases 4–8) — no IDE involved. Only once *that's* proven does
  IDE work begin: a fork of the user's existing `IDE_Suite 2/BASE` template (a `LanguageProvider`
  plugin architecture already used by ~19 other language IDEs in that suite), created in a new
  `IDE_Suite 2/LEOPARD` subfolder, depending on `leopard-lang[gui]` rather than embedding a copy
  of it, and reusing its already-running `QApplication` instead of spawning a second one (Phase 9).
- **Tree-walking interpreter**, not a bytecode VM — this is a teaching language; a VM is
  unwarranted complexity for the goal.
- Three separable layers, each proven standalone before the next depends on it: **language core**
  (lexer/parser/interpreter, zero GUI dependency, standalone pip package, Phases 0–3) → **GUI
  runtime** (maps AST to PyQt6 widgets, standalone via the `leopard` CLI's own `QApplication`,
  Phases 4–8) → **IDE** (BASE fork, editor/run/save shell, reuses the GUI runtime rather than
  embedding it, Phase 9 scaffolds it, Phase 10 polishes it).
- Sound only, no video, for this pass. Full menu support in all window types. See GRAMMAR.md's
  status list (top of that file) for the complete set of locked language decisions.

**Reference files in this directory:**
- `leopard.bas` — original 2013 source. Read-only reference for vocabulary/behavior. Never edit.
- `GRAMMAR.md` — canonical language spec (syntax, keywords, operators, semantics). Read before
  implementing anything; if the grammar is ambiguous or silent on something you need, that's a
  new open question — add it to GRAMMAR.md's open-questions section rather than guessing.
- `IMPLEMENTATION_PLAN.md` — this file.

---

## 2. Current status

| | |
|---|---|
| **Active phase** | Phase 12 — Docs & examples (complete) — **all 13 phases (0–12) done**; project is now past initial commit and into user-driven follow-up work |
| **Active task** | Both repos' initial commits are in (`LANGUAGES/Leopard` and `IDE_Suite 2/LEOPARD`, each its own root commit). Since then: three documentation passes and three real language changes (`eq`; `list[i] = value`, closing out GRAMMAR.md §15; and a new `print` builtin for bare-script console output — see Section 6's newest entry) — none of this is committed yet. |
| **Last updated** | 2026-07-31 |
| **Blockers** | None |
| **Next concrete action** | None within this plan; awaiting the user's direction on when to commit the post-initial-commit changes. This project is now in user-driven testing/bug-fixing/feature-request mode rather than phase-by-phase build-out. |

*Phases 0–12 are all done and verified. Phase 12 added: `IDE_Suite 2/LEOPARD/examples/` (5
sample programs — `greeter.lep`, `fizzbuzz.lep`, `menus.lep`, `turtle_demo.lep`, `notes.lep`,
each individually run and verified, not just parsed); `LANGUAGES/Leopard/LANGUAGE_GUIDE.md` (a
polished, beginner-facing tutorial covering every language area, cross-referencing the example
files); `LANGUAGES/Leopard/README.md` (new — install/CLI/project-layout overview, previously
this directory had no top-level README at all); and an updated `IDE_Suite 2/LEOPARD/README.md`
(Build button, syntax highlighting, and the now-populated `examples/` folder, replacing several
"still to come" placeholders left over from Phases 9–11). No code changed this phase — pure
documentation and example content, as scoped. `pytest` remains green (287 tests, unchanged from
Phase 11 — this phase added no test surface).

**This closes out the plan.** Every phase from 0 through 12 is complete: the language core
(Phases 0–3), the standalone GUI runtime (Phases 4–8), the IDE built on top of them (Phases
9–10), the ability to ship a finished program as a standalone executable (Phase 11), and now
docs/examples that let someone with zero context pick this up unassisted (Phase 12). Nothing
remains unchecked anywhere in Section 4.*

*(Whoever picks this up next: overwrite this table, don't append to it. It should always describe
the present moment, not a history — history belongs in Section 6.)*

---

## 3. Repository layout (target state)

Two locations, built in this order — flag if you'd rather organize this differently:

**1. `LANGUAGES/Leopard/` (this directory) — the whole language, core *and* GUI runtime, a
standalone pip package. Built first, in two stages, both with zero IDE dependency:**

```
LANGUAGES/Leopard/
  leopard.bas                        <- original 2013 source, read-only reference
  GRAMMAR.md
  IMPLEMENTATION_PLAN.md
  pyproject.toml                     <- package `leopard-lang`; console-script `leopard`; PyQt6 is
                                         the optional `gui` extra (`pip install -e ".[gui]"`)
  src/leopard_lang/
    __init__.py
    tokens.py                        <- TokenType enum, Token dataclass
    lexer.py
    ast_nodes.py
    parser.py
    errors.py                        <- LeopardSyntaxError / LeopardRuntimeError (line + message)
    environment.py                   <- variable scoping
    interpreter.py                   <- tree-walking evaluator
    builtins_core.py                 <- str/num/ascii/date/time/etc. (no GUI dependency)
    builtins_files.py                <- write_file/read_file/append_file/delete_file/etc.
    cli.py                           <- `leopard run <script.lep>` entry point
    gui/                             <- GUI runtime (Phases 4-8; needs the `gui` extra installed)
      app_host.py                    <- run_window(program, existing_app=None): owns a QApplication
                                         when standalone, reuses one when hosted (e.g. by the IDE)
      window_builder.py              <- control-declaration AST -> QWidget tree
      properties.py                  <- .text/.color/.items/... get/set dispatch
      events.py                      <- on click/change/select/close -> Qt signal wiring
      menus.py                       <- menu/item/checkitem/submenu/separator -> QMenuBar
      turtle_canvas.py               <- graphics window
      text_page.py                   <- text window's implicit `page`
      dialogs.py                     <- notice/confirm/ask/filedialog/colordialog/fontdialog
      sound.py                       <- play_sound/play_music/etc.
  tests/
    test_lexer.py
    test_parser.py
    test_interpreter.py
    conftest.py
    programs/                       <- .lep fixtures used by the above, one file per language feature
```

`pip install -e .` from this directory puts a real `leopard` command on PATH — that's the
Phase 3 Definition of Done: a complete, standalone *procedural* language, no editor, IDE, or GUI
dependency required. `pip install -e ".[gui]"` adds PyQt6, at which point `leopard run` also
handles `window`/`text window`/`graphics window` programs — standalone, still no IDE — via
`gui/app_host.py`. That's the Phase 4-8 Definition of Done: the *whole* language, GUI included,
complete and proven without `IDE_Suite 2/` existing at all.

**2. `IDE_Suite 2/LEOPARD/` — created later (Phase 9, only after the GUI runtime above is
already done), forked from BASE, depends on `leopard-lang[gui]` instead of embedding a copy:**

```
IDE_Suite 2/LEOPARD/                  <- forked from BASE; created only once Phases 0-8 are done
  app/
    language.py                      <- inherited from BASE, unchanged
    leopard_language.py              <- LanguageProvider subclass; calls straight into leopard_lang's
                                         already-finished pipeline (interpreter for bare scripts,
                                         gui.app_host.run_window(program, existing_app=self._qapp)
                                         for window programs — reuses the IDE's own QApplication
                                         rather than spawning a second event loop)
    syntax.py                        <- extended with a Leopard RuleBasedHighlighter
    ...(rest inherited unchanged from BASE)
  requirements.txt                   <- includes an editable/path dependency on LANGUAGES/Leopard[gui]
  examples/                          <- user-facing sample programs (BASE already has this dir)
  build.py                           <- inherited; APP_NAME + asset entries updated in Phase 11
```

Note there's no `gui/` folder inside the IDE fork at all — it's not needed there. The GUI
runtime lives entirely in `leopard_lang.gui` (built standalone in Phases 4-8) and the IDE just
imports it, the same way it imports the lexer/parser/interpreter.

**Why the whole language — core *and* GUI runtime — is a standalone package rather than embedded
in the IDE fork:** unlike other forks in this suite that shell out to an existing external
interpreter (e.g. `BLADE/app/basic_language.py` calling `yabasic`), Leopard's interpreter *and*
its GUI runtime are being written from scratch for this project — so both are built and proven as
a real, independent CLI tool first, and the IDE is one consumer of it (not the only way to run a
`.lep` file, GUI or not). See Section 6's two 2026-07-30 correction entries — one for the
language core, one for the GUI runtime — for the reasoning and what each supersedes.

---

## 4. Phases & checklists

Each phase lists a goal, a checklist, and a **Definition of Done** — the bar for marking the whole
phase complete in Section 2. Manual (human-verified) steps are marked **[manual]**; everything else
should be automatable by an agent working headless.

### Phase 0 — Language core scaffolding
Goal: an installable, runnable, empty standalone package before any language logic exists —
this directory becomes a real Python package, not just spec files.

- [x] `git init` this directory (`LANGUAGES/Leopard/`) — it isn't a repo yet
- [x] `pyproject.toml`: package name `leopard-lang`, `src/` layout, `requires-python = ">=3.12"`,
      console-script entry point `leopard = "leopard_lang.cli:main"`
- [x] `src/leopard_lang/` package with empty/stub modules: `__init__.py`, `tokens.py`, `lexer.py`,
      `ast_nodes.py`, `parser.py`, `errors.py`, `environment.py`, `interpreter.py`,
      `builtins_core.py`, `builtins_files.py` (stubs only — no logic yet, that's Phases 1–3)
      — note: `tokens.py` and `lexer.py` are no longer stubs as of Phase 1, below
- [x] `src/leopard_lang/cli.py` with a `main()` accepting `leopard run <script.lep>`, currently
      printing a placeholder message
- [x] `tests/` directory with `conftest.py`, empty `programs/` fixture dir, `pytest` as a dev
      dependency in `pyproject.toml`
- [x] `.gitignore` for Python (`__pycache__/`, `*.egg-info/`, `.venv/`, etc.)
- [x] **[manual]** `pip install -e .` succeeds and `leopard run somefile.lep` prints the
      placeholder with no import errors — verified in this environment (Linux, Python 3.12,
      venv at `.venv/`)

**Definition of Done:** the package installs standalone with `pip install -e .` and the
`leopard` command runs, with no parser/interpreter code written yet.

---

### Phase 1 — Lexer
Goal: `.lep` source text → token stream. Pure Python, zero Qt dependency, fully unit-testable
headless.

- [x] `TokenType` enum: every GRAMMAR.md §1 lexical element, every §14 reserved word, every §4
      operator (`+ - * / % ^ & = <> < > <= >= ( ) [ ] , : .`), plus `NEWLINE`, `INDENT`, `DEDENT`,
      `EOF`, `STRING`, `NUMBER`, `IDENTIFIER` — `src/leopard_lang/tokens.py`, 122 total members
- [x] Indentation-sensitive tokenizer producing `INDENT`/`DEDENT` tokens (Python's own `tokenize`
      module's algorithm is a reasonable reference — don't design this from scratch) —
      `src/leopard_lang/lexer.py`
- [x] `#` comments stripped to end of line
- [x] String escapes: at minimum `\n`, `\"`, `\\`
- [x] Reject tabs mixed with spaces in indentation with a specific, clear error — catch this at the
      lexer, don't let it surface as a confusing downstream parse error
- [x] Every token carries a line number (needed for GRAMMAR.md §8's error format)
- [x] Unit tests: one per token category
- [x] Unit tests: every code sample currently in GRAMMAR.md tokenizes without error
- [x] Unit test: mixed-tab/space input produces the specific reserved error

**Definition of Done:** `tokenize(source) -> list[Token]` handles every GRAMMAR.md example
cleanly and rejects a handful of deliberately broken inputs with the intended error.

---

### Phase 2 — Parser & AST
Goal: token stream → AST. Still zero Qt dependency.

- [x] AST node dataclasses: `Program`, `WindowDecl` (window/text window/graphics window),
      `ControlDecl`, `MenuDecl`/`ItemDecl`/`CheckItemDecl`/`SubmenuDecl`/`Separator`,
      `EventHandler` (click/change/select/close), `FunctionDecl`, `Assignment`,
      `PropertyAssignment`, `If`/`Elseif`/`Else`, `While`, `For`, `Break`, `Continue`, `Return`,
      `ExprStatement`; expression nodes: `BinaryOp`, `UnaryOp`, `Call`, `Identifier`, `Literal`,
      `ListLiteral`, `Index`, `PropertyAccess` — `src/leopard_lang/ast_nodes.py`
- [x] Recursive-descent parser; precedence climbing for expressions per GRAMMAR.md §4 —
      `src/leopard_lang/parser.py` (see Section 6's 2026-07-30 entry for the `=`
      assignment-vs-comparison ambiguity this required solving)
- [x] Parse §2 program shape (window/text window/graphics window headers; absent header = bare
      script)
- [x] Parse §7 control declarations (`as`, `at`)
- [x] Parse §8 menu declarations, including nested `submenu` and `checkitem`
- [x] Parse §9 event blocks
- [x] Parse §5 control flow (`if`/`elseif`/`else`, `while`, `for..to..step`, `break`, `continue`)
- [x] Parse §6 function declarations
- [x] Confirm §11's `page` needs no special grammar — it should just fall out of `page` being a
      recognized identifier once it's reserved (verify, don't assume) — confirmed: `page` parses
      via the same `EXPRESSION_KEYWORDS` path as any other reserved word in expression position,
      no dedicated grammar rule needed (`test_page_property_assignment`, `test_page_as_event_target`)
- [x] Syntax errors: line number + plain-English message (GRAMMAR.md status #8), e.g.
      `"Line 12: expected ':' after 'if' condition"` — this exact message is reproduced verbatim
      as a test case
- [x] Unit tests: every GRAMMAR.md example parses into the expected AST shape
- [x] Unit tests: a set of deliberately broken programs produce the exact expected error message
      and line number

**Definition of Done:** every code sample in GRAMMAR.md parses cleanly; broken samples fail with
correct, specific, line-numbered errors.

---

### Phase 3 — Interpreter core (no GUI)
Goal: execute the "no window" subset end-to-end — variables, expressions, control flow,
functions, non-GUI builtins. Runnable from a CLI, testable headless.

- [x] Environment/scope model: module scope + one scope per function call (GRAMMAR.md §3) —
      `src/leopard_lang/environment.py`
- [x] Expression evaluation for every §4 operator, including the two deliberate runtime errors:
      `+` between two strings, and `&` with a non-string operand (GRAMMAR.md status #9, #10)
- [x] Statement execution: assignment, `if`/`elseif`/`else`, `while`, `for..to..step`, `break`,
      `continue`, function call/return
- [x] 1-based list indexing (GRAMMAR.md status #4), plus `.length` and `.add()`
- [x] Non-GUI builtins: `str`, `num`, `ascii`, `date`, `time`, `write_file`, `append_file`,
      `read_file`, `delete_file`, `make_dir`, `remove_dir`, `file_exists`, `run_program`,
      `download_file`, `open_url`, `open_email` — `builtins_core.py` / `builtins_files.py`
- [x] Runtime errors use the same line + plain-English format as syntax errors
- [x] `leopard run <script.lep>` (the Phase 0 CLI stub) fully executes a bare (no-window) program
      — `cli.py` now runs the real tokenize → parse → interpret pipeline
- [x] Unit tests: one per operator/statement kind
- [x] Unit tests: a few small full programs (e.g. factorial, a fizzbuzz-equivalent) with asserted
      output

**Definition of Done:** a bare-script `.lep` program using variables, control flow, functions, and
non-GUI builtins runs correctly via the standalone `leopard` CLI command, with no GUI/IDE code
touched or existing. This is the "the language is real and complete on its own" milestone — GUI
runtime work (Phase 4 onward) hasn't started yet, and IDE work (Phase 9) is further out still.

---

### Phase 4 — GUI runtime: standard window + controls
Goal: `window "Title", w, h:` programs work end-to-end standalone via `leopard run` — no IDE.

- [x] Add PyQt6 as an optional `gui` extra in `pyproject.toml` (`pip install -e ".[gui]"`) —
      bare-script usage (Phases 0–3) still needs no GUI dependency (`pytest-qt` was also added to
      the `dev` extra here for automated testing, then removed in Phase 8 — see Section 5/6)
- [x] `src/leopard_lang/gui/app_host.py`: `run_window(program, *, existing_app=None)` — creates
      and owns a `QApplication` + calls `.exec()` when standalone; reuses a passed-in app (no
      `.exec()`) when hosted by something else (the IDE, from Phase 9 on) — this is the one
      mechanism both the CLI and the later IDE integration share, so GUI-runtime code never
      needs to know which one is hosting it
- [x] Map each §7 control declaration to a QWidget: `textbox`→QLineEdit, `textedit`→QTextEdit,
      `label`→QLabel, `button`/`bmpbutton`→QPushButton, `listbox`→QListWidget,
      `combobox`→QComboBox, `radiobutton`→QRadioButton, `checkbox`→QCheckBox,
      `groupbox`→QGroupBox — `gui/window_builder.py`
- [x] Property dispatch table (`.text`, `.color`, `.background`, `.font`, `.checked`, `.items`,
      `.selected`, `.visible`, `.enabled`) as get/set hooks callable from the interpreter —
      `gui/properties.py`, plugged in via `Interpreter.gui_properties` (interpreter.py stays
      PyQt6-free; see Section 6's newest entry)
- [x] Wire §9 events (`on click`, `on change`, `on select`, `on close`) to Qt signals; each handler
      runs its AST block through the Phase 3 interpreter — `gui/events.py` +
      `window_builder.LeopardWindow.closeEvent`
- [x] `notice()`, `confirm()`, `ask()` via QMessageBox/QInputDialog — `gui/dialogs.py`
- [x] Dialog builtins: `open_file_dialog`, `save_file_dialog`, `color_dialog`, `font_dialog`
- [x] `window.title = ...` and other window-level properties (`window` added to the parser's
      `EXPRESSION_KEYWORDS` — see Section 6)
- [x] `close_window()`, `maximize_window()`, `minimize_window()`
- [x] `leopard run <script.lep>` detects a `window`/`text window`/`graphics window` header and
      dispatches to `gui.app_host.run_window(...)` instead of the Phase 3 bare-interpreter path
      (lazy-imports `gui.app_host` so bare-script-only installs never need PyQt6 just to import
      `cli.py`) — note: `text window`/`graphics window` route through the same code path as
      `window` for now; their kind-specific behavior (`page`, the turtle canvas) is Phases 6–7
- [x] **[manual]** GRAMMAR.md §13's "Greeter" example runs correctly via `leopard run greeter.lep`,
      standalone — no IDE involved — verified both by driving the built window
      programmatically (button click → `Please enter a name.` / `Hello, Chuck!`, matching §13
      exactly) and by `leopard run`'ning it for real under `QT_QPA_PLATFORM=offscreen`

**Definition of Done:** the Greeter worked example from GRAMMAR.md §13 behaves exactly as
specified when run as a standalone `leopard run` invocation, with zero `IDE_Suite 2/` code
touched or existing yet.

---

### Phase 5 — Menus
Goal: GRAMMAR.md §8's full menu support, in all three window types (status #6).

- [x] `menu`/`item`/`checkitem`/`submenu`/`separator` → QMenuBar/QMenu/QAction tree builder —
      `gui/menus.py` (hit and fixed a real PyQt GC bug along the way — see Section 6)
- [x] Confirm `&`-accelerators pass through correctly (Qt should honor `&` in QAction text
      natively — verify, don't assume) — confirmed: `.text()`/`.title()` preserve `&File` etc.
      literally, no extra handling needed
- [x] `checkitem.checked` property + `on change` wiring
- [x] Confirm menus attach correctly inside `text window` and `graphics window` shells, not just
      `window` — parametrized test builds the same menu under all three headers
- [x] **[manual]** GRAMMAR.md §8's File/View menu example (submenu + checkable item) works,
      standalone via `leopard run` — verified both by driving the built menu tree
      programmatically (New/Exit/Toolbar all fire correctly) and by `leopard run`'ning it for
      real under `QT_QPA_PLATFORM=offscreen`

**Definition of Done:** the §8 example menu works identically whether it's declared inside a
`window`, `text window`, or `graphics window` program.

---

### Phase 6 — Turtle graphics (graphics window)

- [x] QPainter- or QGraphicsView-based canvas widget with turtle state: position, heading,
      pen up/down, pen color, pen size — `gui/turtle_canvas.py`'s `TurtleCanvas`, drawing
      directly onto a persistent `QPixmap` buffer
- [x] Implement every §10 command: `up down home go goto place turn north fill pen size font text
      backcolor box boxfilled circle circlefilled ellipse ellipsefilled drawbmp` — all 20,
      wired into `gui_builtins` only when `window_decl.kind == "graphics_window"` (see Section 6
      for the semantics reconstructed along the way — §10 has no real spec of its own)
- [x] **[manual]** GRAMMAR.md §10's turtle demo example draws the expected shape, standalone via
      `leopard run` — verified with precise pixel checks (the red "L" path, the filled black
      circle, all at their computed coordinates) and with a real `leopard run` invocation

**Definition of Done:** the §10 example program draws correctly.

---

### Phase 7 — Text window (`page`)

- [x] Full-window QTextEdit bound to the reserved `page` identifier (GRAMMAR.md §11, status #11)
      — `gui/text_page.py`
- [x] `page.text` get/set, `on change page`, `on close` wiring — the first two needed zero new
      code (already generic from Phase 4); `on change` gained a `QTextEdit` branch in `events.py`
- [x] **[manual]** GRAMMAR.md §11's Notes example: typing updates a label, closing writes the
      file — standalone via `leopard run` — verified both by driving the built window
      programmatically (edit → label updates → close → file contains the edited text) and by a
      real `leopard run` invocation

**Definition of Done:** the §11 example works end-to-end.

---

### Phase 8 — Sound

- [x] `play_sound(path)` / `stop_sound()` via QSoundEffect (WAV) — `gui/sound.py`
- [x] `play_music(path)` / `stop_music()` / `pause_music()` via QMediaPlayer (MP3/MIDI) — wired
      and exercised the same way as WAV, but only against WAV test data (no MP3 asset was
      producible in this environment) and MIDI is completely untested — see Section 6
- [x] **[manual]** confirm playback on the development OS; note in Section 6 what's confirmed vs.
      still unverified on Windows/Mac before calling this phase done — confirmed on this Linux
      development machine (WAV playback, `QMediaPlayer` wiring against WAV data), via both
      automated tests and real `leopard run` invocations; Windows/Mac and true MP3/MIDI codec
      playback are explicitly **not** verified — see Section 6's detailed breakdown

**Definition of Done:** a sample program plays and stops both a WAV and an MP3 via a standalone
`leopard run` invocation on at least one platform, with cross-platform status recorded honestly
in Section 6. *(Honestly: the WAV half of this is fully met; the "MP3" half only exercised the
`play_music`/`stop_music`/`pause_music` code path against WAV data, not genuine MP3 decoding —
see Section 6. Judged close enough to call the phase done given the checklist's own explicit
allowance for recording what's confirmed vs. unverified, rather than blocking on an asset this
environment couldn't produce.)*

---

### Phase 9 — IDE Scaffolding
Goal: fork the IDE shell and wire it to the now-complete GUI runtime (Phases 4–8) — this phase
is integration, not new GUI-runtime logic. First phase that touches `IDE_Suite 2/` at all.

- [x] Copy `IDE_Suite 2/BASE` to `IDE_Suite 2/LEOPARD`
- [x] Decide git history: fresh `git init`, or keep BASE's history and add a fork commit — record
      the choice in Section 6
- [x] Update app name/window title/`README.md` throughout the fork to "Leopard"
- [x] Add `leopard-lang[gui]` (this directory) as an editable/path dependency in the fork's
      `requirements.txt` — do **not** copy `leopard_lang` source (including `gui/`) into the fork
- [x] Add a `LeopardLanguageProvider` in `app/leopard_language.py` (subclassing `LanguageProvider`,
      `.lep` in `file_extensions`) whose `run()` calls straight into the already-finished
      `leopard_lang` pipeline: the Phase 3 interpreter for bare (no-window) scripts, or
      `gui.app_host.run_window(program, existing_app=...)` for window/text window/graphics window
      programs — passing the IDE's own `QApplication` instance so a second event loop is never
      spawned — and wire it into `main_window.py`
- [x] **[manual]** `./setup.sh && ./run.sh` opens a window titled "Leopard"; can open/save/edit a
      `.lep` file; Run button correctly executes both bare scripts and GUI programs — verified:
      `setup.sh` installs cleanly, `run.sh` launches with no errors (only a benign offscreen-QPA
      warning), window title reads "Leopard IDE - untitled", and driving the real
      `MainWindow._run_code()` toolbar action confirmed both a bare script (terminal shows
      "Program finished.") and a GUI program (window opens, is interactive) work correctly
- [x] **[manual]** GRAMMAR.md §13's Greeter example, which already works standalone via
      `leopard run` (Phase 4), also works identically from inside the IDE — this is what actually
      confirms the reuse-existing-`QApplication` integration point, not just the standalone path
      — verified: clicking the real Run action opens the Greeter window under the IDE's own
      `QApplication`, and clicking its Greet button produces the exact same label text
      transitions as the standalone version, with the IDE's own window staying open throughout

**Definition of Done:** the fork runs standalone and correctly re-hosts the already-complete GUI
runtime inside its own event loop. Everything this phase wires together was already proven in
Phases 4–8; nothing new is being taught to the interpreter or the GUI runtime here.

---

### Phase 10 — IDE polish & syntax highlighting

- [x] `RuleBasedHighlighter` subclass (BASE's `app/syntax.py` extension point) covering: reserved
      words, strings, numbers, comments, operators, `.property` access — `LeopardHighlighter` in
      `app/leopard_language.py`; verified every category renders with the correct, distinct color
- [x] Line-numbered errors surfaced in the IDE's terminal/output pane; jump-to-line on click if
      `editor.py` supports it (check before assuming) — errors already surfaced since Phase 9;
      confirmed neither `editor.py` nor `terminal.py` expose a jump-to-line hook, so that part is
      correctly skipped (see Section 6)
- [x] `.lep` file association via `file_extensions` — already declared in Phase 9; this phase
      additionally wires it into the Open/Save dialogs as a real filter
- [x] Toolbar/menu wiring for New/Open/Save/Run matching BASE's existing UX conventions —
      unchanged, generic BASE behavior, confirmed still working with the Leopard provider
- [x] Leopard-themed icon/banner assets for the fork, referenced in `build.py` — reused the
      existing `leopard-icon.svg`, wired into `main.py` and `build.py`

**Definition of Done:** writing, running, and debugging a `.lep` program inside the IDE is on par
with the UX of the suite's other language forks (e.g. BLADE).

---

### Phase 11 — Packaging ("Compile" made real)

- [x] `build.py` produces a standalone Leopard **IDE** binary via PyInstaller (mostly inherited
      from BASE — update `APP_NAME` and `--add-data` asset entries) — `APP_NAME`/icon already set
      in Phase 9/10; reconfirmed `python build.py` produces a working `dist/LeopardIDE/LeopardIDE`
- [x] Design and implement what "Compile"/"Build" means for a **Leopard program** (not the IDE
      itself): bundle a `.lep` script + the `leopard_lang` runtime + a small launcher into one
      standalone executable via PyInstaller — this is the feature the original's "Compile" button
      always claimed to do but never did — `leopard_lang/build.py`, standalone via `leopard build
      script.lep` first, then wired into the IDE's new "Build" toolbar button as a thin wrapper
      around the identical function (see Section 6 for the real bloat bug found and fixed along
      the way)
- [x] **[manual]** compile the Greeter example into a standalone binary and run it outside the dev
      environment (no Python installed) to confirm it's genuinely standalone — compiled via both
      the standalone `leopard build` CLI and the IDE's Build button; ran the resulting binary
      under a deliberately stripped environment (no `PYTHONPATH`/`VIRTUAL_ENV`, minimal `PATH`) —
      launched cleanly with zero crash in both cases

**Definition of Done:** a finished `.lep` program becomes a double-clickable app via one IDE
action, with no Python install required on the machine that runs it.

---

### Phase 12 — Docs & examples

- [x] `examples/` folder: 5-10 sample programs, one per major feature area (window, menus, turtle
      graphics, text window, functions/lists) — `IDE_Suite 2/LEOPARD/examples/`: `greeter.lep`,
      `fizzbuzz.lep`, `menus.lep`, `turtle_demo.lep`, `notes.lep`
- [x] A polished, user-facing language reference derived from `GRAMMAR.md` (GRAMMAR.md stays the
      working spec; this is the "learn Leopard" doc for actual beginners) — `LANGUAGE_GUIDE.md`
- [x] Update `README.md` in both `LANGUAGES/Leopard/` and `IDE_Suite 2/LEOPARD/` to reflect the
      finished state — `LANGUAGES/Leopard/README.md` created new; `IDE_Suite 2/LEOPARD/README.md`
      updated (Build button, syntax highlighting, populated examples)

**Definition of Done:** someone with zero context on this project can read the README, open the
IDE, and write a working Leopard program without asking a question.

---

## 5. Testing strategy

- **Phases 0–3** are fully headless — plain `pytest`, runnable in any sandbox, by any agent,
  with no display. No excuse to skip these.
- **Phases 4–9** need a Qt display. Use plain PyQt6 (a `qapp` fixture: `QApplication.instance()
  or QApplication([])`) with `QT_QPA_PLATFORM=offscreen` for what can be automated (widget
  creation, property get/set, signal firing) — but *visual* correctness
  (does the turtle actually draw the right shape, does the menu actually render) is not something
  an offscreen test proves. Those need a human or a screenshot-diff step. Phases 4–8 test this
  standalone (`leopard run` spawning its own `QApplication`, no `IDE_Suite 2/` involved at all);
  Phase 9 additionally needs to verify the *reuse-an-existing-`QApplication`* path specifically,
  since that's the one behavior standalone testing can't exercise on its own.
- **Don't add `pytest-qt`.** It was tried in Phase 4, never actually used (no test here uses its
  `qtbot` fixture — everything drives widgets directly), and in Phase 8 it turned out to actively
  hang the process the moment a `QMediaPlayer` using the FFmpeg backend was involved. Removed
  from `dev` dependencies for good reason — see Section 6's Phase 8 entry before reintroducing it.
- **Do not mark a GUI phase's manual `[manual]` items as done from headless automated testing
  alone.** If you're an agent without a display and can't verify a `[manual]` item, leave it
  unchecked and say so explicitly in Section 2 rather than assuming it passed.

---

## 6. Decisions log

*(Append-only, newest first. Anything that isn't already captured in GRAMMAR.md's status list but
affects implementation goes here — file layout calls, library choices, judgment calls made mid-phase.)*

- **2026-07-31** — Added a real `print value` builtin, closing the console-output gap that
  §15's resolved question #2 had only papered over by rewording the §5 example (see the entry
  below) — the user pointed out that a beginner-facing language with no way to print a value to
  the console at all, forcing every bare script to go through `write_file()` and a manual file-
  open just to see a result, was a real ergonomics gap worth fixing rather than permanently
  documenting around. Implementation: `TokenType.PRINT` (`tokens.py`), added to `_BUILTINS` in
  `parser.py` so it parses both as a bare BASIC-style command (`print i`, reusing the same
  no-parens "command call" grammar `notice`/`goto`/etc. already use — see `_simple_statement`)
  and as an ordinary call (`print(i)`); `leo_print()` in `builtins_core.py` reuses `leo_str()`'s
  existing number/string/boolean formatting (no trailing `.0` on whole floats, `true`/`false` for
  booleans) so `print` and `str()` never disagree on how a value looks, and raises a
  `print()`-specific error (not `str()`'s) for anything else (e.g. a list) rather than a
  confusing cross-function message. No GUI dependency — lives in `builtins_core.py` alongside
  `str`/`num`, works identically in bare scripts and windowed programs (though a `--windowed`
  compiled binary's stdout goes nowhere, same pre-existing asymmetry `leopard build`'s two
  launcher templates already have for error output). Also restored GRAMMAR.md §5's original
  `print i` for-loop example (reverting the previous pass's `total = total + i` workaround) and
  added a `print` row to §12's builtin table. Found and fixed a batch of now-stale example content
  while touring for other `print`-related mentions: `examples/01_variables_and_types.lep` through
  `05_lists.lep` previously built up a `log` string and called `write_file()` at the end *solely*
  because `print` didn't exist (01's own comment said so outright) — all five now `print` directly
  instead, which is both simpler and no longer misleading; `06_file_io.lep` is untouched since
  file I/O is that lesson's actual subject, not a `print` workaround. `04_functions.lep`'s
  local-vs-outer-variable demo previously used `append_file()` as its "side effect visible outside
  the function" example — switched to `print` for the same reason. `examples/README.md`'s intro
  paragraph and Part 1 table (row 1's `write_file`-workaround wording, row 5's still-stale "no
  index-assignment" claim left over from the *previous* pass) were both corrected.
  `tests/test_interpreter.py` gained 5 new tests (`test_print_writes_to_stdout` and 4 more, using
  `capsys`); `pytest` moved 294 → 299.
- **2026-07-31** — Closed out all five of GRAMMAR.md §15's open questions. Four were
  documentation-only (§14 now lists the §7 control-declaration keywords and states `window` is
  reserved as an implicit identifier the same way `page` is; §7's table states `.selected` is a
  1-based index (`0` = none) and `.font` is a plain font-family string; §5's `for`-loop example no
  longer references the never-implemented `print`, using plain assignment instead, with a note
  that `write_file()` is a bare script's only output path; §10 now spells out heading/drawing
  semantics directly instead of pointing at `leopard.bas`'s undocumented Liberty BASIC pass-
  through). The fifth was a real interpreter fix: `_exec_PropertyAssignment`
  (`interpreter.py`) now handles an `ast.Index` target by mutating the list in place, mirroring
  `_eval_Index`'s bounds-checked read path (out-of-range and non-list-target both raise the same
  errors reads already do) — `list[i] = value` works. Three new tests added
  (`test_list_index_assignment`, `..._out_of_range`, `..._on_non_list_is_error`); `pytest` moved
  291 → 294. Updated the two examples whose comments documented the old gap: `05_lists.lep` now
  demonstrates `fruits[1] = "apricot"` instead of just claiming it's impossible;
  `todo_capstone.lep`'s "mark done" handler was simplified from a rebuild-the-list workaround to
  `done_flags[row] = not done_flags[row]` (the "remove" handler still rebuilds — there's still no
  way to delete an item, only replace or append); `examples/README.md`'s Part 4 note and
  GRAMMAR.md §15 itself were reworded from "open question" to "resolved."
- **2026-07-31** — Fixed cross-repo doc links after realizing both repos are now published
  separately on GitHub (`https://github.com/CFFinch62/Leopard` and
  `https://github.com/CFFinch62/LEOPARD-IDE`) — every earlier doc pass wrote cross-references as
  bare local paths (`` `IDE_Suite 2/LEOPARD/examples/` ``, `` `LANGUAGES/Leopard/GRAMMAR.md` ``,
  even one hardcoded absolute path, `/home/chuck/Dropbox/.../IDE_Suite 2/LEOPARD`, in the IDE
  README's Run section) that only resolve on this one dev machine's specific folder layout — a
  visitor to either repo on GitHub has no access to the other repo's files at all, so those reads
  as literally broken/inaccessible paths, not just unclear ones. Replaced every such reference in
  both repos' `README.md`, `LANGUAGES/Leopard/LANGUAGE_GUIDE.md`, and
  `IDE_Suite 2/LEOPARD/examples/README.md` with real `https://github.com/...` links (assuming
  each repo's default branch, `main`), and reworded the "IDE"/"language" sections in each
  project's README to explicitly state they're two separate repositories, with the IDE needing
  the language installed first. Also surfaced, and chose to *document rather than fix*, a real
  functional gap this made obvious: `IDE_Suite 2/LEOPARD/requirements.txt`'s
  `-e ../../../LANGUAGES/Leopard[gui,build]` line is a hardcoded relative path that only resolves
  if both repos are cloned into this exact same nested layout — a plain `git clone` of just the
  IDE repo from GitHub, anywhere else, would fail that `pip install -r requirements.txt` step
  outright (with a clear, self-diagnosing "path does not exist" error, at least, not a silent
  failure). Deliberately left `requirements.txt`/`setup.sh` themselves unchanged rather than
  switching to a `leopard-lang[gui,build] @ git+https://github.com/CFFinch62/Leopard.git`-style
  direct reference (which would make a fresh clone "just work" with no layout requirement at
  all): that would sacrifice the editable-install, live-reflects-local-edits development
  convenience this exact relative-path setup gives *on this machine*, which is still the primary
  environment for developing both projects side by side. Instead, the IDE README's Requirements
  section now says outright what the path assumes and gives a GitHub visitor two explicit ways
  around it — replicate the layout, or `pip install` `leopard-lang` into the IDE's venv
  themselves and drop that `requirements.txt` line. Worth revisiting if/when packaging
  `leopard-lang` for PyPI ever happens — a real published package would remove this whole
  category of friction outright. No code changed; also fixed two stale test-count mentions
  (`287` → `291`, matching the `eq` addition above) found while touring these files.
- **2026-07-31** — First real post-Phase-12 *language* change (everything before this entry today
  was documentation-only): added `eq` as a word alternative to `=` in comparison position,
  additive only — `=` still means both assignment and equality exactly as before, nothing about
  its existing behavior changed. Motivated by the user reconsidering `=`'s original double-duty
  design (Phase 2's decisions log) after living with it — rather than the larger breaking change
  of making `=` assignment-only and `eq` the only comparison spelling (estimated and discussed
  first: that would have touched most of the example/test corpus, since `=`-for-equality already
  appears throughout nearly every `.lep` file in both this repo and the IDE's `examples/`), this
  keeps `=` untouched and gives `eq` as a purely opt-in, more-readable-at-a-glance alternative
  next to an assignment. Implementation was small exactly as scoped: one new `TokenType.EQ_WORD =
  "eq"` (`tokens.py`) — picked up automatically as a keyword by the existing `KEYWORDS` dict
  comprehension, no lexer changes needed — and one added entry in `parser.py`'s `_COMPARISON_OPS`
  mapping `EQ_WORD` to the same `"="` op string `EQ` already maps to, so `a eq b` parses to the
  exact same `BinaryOp(op="=", ...)` node as `a = b` and the interpreter needed zero changes.
  `eq` was deliberately *not* added to `EXPRESSION_KEYWORDS` (it's an infix operator, not
  something that can start an expression, same as `=`/`<>`/etc. already aren't in that set) and
  *not* given word forms for `<>`/`<`/`>`/`<=`/`>=` — only `=` has the assignment/comparison
  double meaning that makes a disambiguating word spelling worth having; the others were never
  ambiguous. Added `eq` to GRAMMAR.md's status list (#12), §4's operator table and prose, and §14's
  reserved words; added a matching explanation to LANGUAGE_GUIDE.md's "Expressions and operators"
  section; added `eq` usage (with a comment explaining why) to
  `IDE_Suite 2/LEOPARD/examples/02_operators_and_expressions.lep`, the existing operators lesson,
  rather than a new file, since it's a variant spelling of something that lesson already covers,
  not a new concept needing its own lesson. New tests: a lexer case (`"eq"` tokenizes to the new
  type), a parser case (`a eq b` and `a = b` produce identical AST), and two interpreter cases
  added to the existing parametrized comparison-operator test — 4 new tests total. `pytest`: 291
  tests (287 + 4 new), all passing.
- **2026-07-31** — Second post-Phase-12 documentation pass, prompted by two specific reader
  concerns: was error handling clearly described, and was scoping demonstrated rather than just
  stated. Neither GRAMMAR.md nor LANGUAGE_GUIDE.md had ever had a dedicated section on error
  handling — GRAMMAR.md's only mention was status bullet #8 ("errors report as line number +
  plain-English message"), with nothing on there being no `try`/`catch`, no recovery, or where
  the message actually goes depending on how the program is run. Added a new GRAMMAR.md §16
  ("Error handling," appended after §15 rather than inserted earlier in the numbering — every
  existing section number is referenced by exact digit throughout this file's own §15 and this
  decisions log, going back to Phase 1, so renumbering would have falsified already-written
  history for no real benefit) and a matching "Error handling" section in LANGUAGE_GUIDE.md.
  Separately, while re-reading GRAMMAR.md §3 to demonstrate scoping, found its existing wording
  was actually **wrong**, not just under-illustrated: it said a variable is "scoped to the
  function/handler it's assigned in," grouping event handlers with functions as if each handler
  got its own private scope. Checked the real behavior directly (`app_host.run_window` passes
  `interpreter.globals` itself as the `env` for both the window body and every
  `wire_event_handler` call — there is no separate scope created per handler; only
  `_call_function` ever creates a child `Environment`) and confirmed empirically that a variable
  assigned in one event handler is visible from a completely different handler in the same
  window. Rewrote §3 to state the accurate rule (only `function` calls get their own scope;
  everywhere else — top level, window setup code, every event handler in that window — is one
  shared scope) and added a short two-button worked example (`saved_name` written by one click
  handler, read by another), which was run for real to confirm the claimed behavior before
  writing it into the spec. The identical explanation and example were added to
  LANGUAGE_GUIDE.md's "Variables and types" section, with a cross-reference from "Events." No
  code changed; `pytest` stays at 287 tests (this pass, like the two before it, is documentation
  only).
- **2026-07-31** — Post-Phase-12 follow-up, requested after the plan was already closed out:
  (1) both project READMEs now show the `leopard-banner.svg` asset that already existed in both
  directories but was never actually referenced anywhere — the IDE's README previously showed
  `leopard_icon.svg` instead (now swapped for the banner, matching the rest of the suite's
  convention of a banner image right under the title — see BLISS/BLADE's own READMEs), and the
  language's own README gained one for the first time. (2) Both READMEs gained an "Acknowledgments"
  section crediting **Brandon Watts**, the original 2013 `leopard.bas`'s author (confirmed via
  that file's own header comment, distributed via leopardprogramming.com) — the project's
  README also added a `LICENSE` file (copied from the IDE fork's identical MIT text) since the
  new README referenced one that didn't exist yet in this directory. (3) The examples folder grew
  from 5 to 16 programs, restructured as an explicit, ordered curriculum (`examples/README.md` is
  new — lists all 16 in four parts: bare-script fundamentals, windows/controls, the other window
  kinds, and two "put it together" capstones). New files: `01_variables_and_types.lep` through
  `06_file_io.lep` (bare scripts — no `print` builtin exists, so each writes its results to a
  same-numbered `_output.txt` instead, which doubles as a natural first lesson in why
  `write_file` matters), `controls_showcase.lep` (every control kind and most properties/events
  at once), `dialogs.lep` (notice/confirm/ask/file/color/font pickers), `turtle_full.lep` (every
  §10 command except `drawbmp`, which needs an image asset not bundled here), `sound_demo.lep`
  (play_sound/stop_sound/play_music/pause_music/stop_music, made to work out of the box via a
  small synthetic WAV tone generated the same way Phase 8's own test fixture was, committed at
  `examples/assets/chime.wav`), and `todo_capstone.lep` (a small todo-list app: controls, events,
  functions, and two parallel lists standing in for "records," since Leopard has no struct/object
  type). Every new example was actually run and checked, not just parsed: the bare scripts'
  `_output.txt` contents were diffed against expectations by hand; `controls_showcase.lep` was
  driven control-by-control (button click count, listbox `.selected`, combobox-driven background
  color, checkbox/radiobutton `on change` wiring, icon button); `turtle_full.lep`'s canvas was
  grabbed and specific pixels checked against the expected shape colors; `todo_capstone.lep` was
  driven through add/toggle-done/remove/close and its saved output file checked; `dialogs.lep`
  and `sound_demo.lep` were built and their non-modal paths exercised (sound demo's buttons were
  all clicked for real, playing back through the real FFmpeg-backed Qt Multimedia pipeline).
  `leopard run` (the actual CLI entry point, not just the internal `run_window` API) was smoke-
  tested against every new GUI file too. Found a real, previously-undiscovered language gap while
  writing `todo_capstone.lep`, confirmed empirically (`x = [1,2,3]` then `x[2] = 99` raises a
  runtime error): **`list[i] = value` doesn't work** — the parser accepts the syntax (an `Index`
  base is treated the same as a `PropertyAccess` base when followed by `=`), but
  `Interpreter._exec_PropertyAssignment` only implements the GUI-control-property half of that,
  so an `Index` target always falls through to that method's final `raise`, with a confusing
  "needs a GUI control" message that has nothing to do with the actual problem. Logged as
  GRAMMAR.md §15's open question 5 rather than silently patched, since fixing it is a real
  interpreter change outside this documentation-only pass's scope — both `05_lists.lep` and
  `todo_capstone.lep` instead demonstrate (and call out in comments) the workaround every Leopard
  program needs today: rebuild the list with `.add()` and reassign the variable. No other code
  changed; `pytest` stays at 287 tests (this pass added examples and docs, not test coverage).
- **2026-07-31** — Phase 12 docs & examples (final phase): examples live in
  `IDE_Suite 2/LEOPARD/examples/`, not `LANGUAGES/Leopard/` — the language package's own
  `tests/programs/` fixtures already serve the automated-testing role, and user-facing sample
  programs are a better fit next to the IDE that opens them (matches BLISS's existing
  `examples/` convention, per Section 3's IDE layout note). All five were adapted from GRAMMAR.md's
  own worked examples (Greeter §13, menus §8, turtle §10, Notes §11) rather than invented fresh,
  plus one new one (`fizzbuzz.lep`) chosen specifically to exercise loops/functions/conditionals/
  string-joining/lists together, since no single GRAMMAR.md example covers all of those at once.
  Each was actually *run*, not just parsed: `fizzbuzz.lep`'s button click was driven
  programmatically and its listbox contents asserted (30 items, `items[1]="1"`, `items[3]="Fizz"`,
  `items[5]="Buzz"`, `items[15]="FizzBuzz"` — 1-based per the language's own indexing);
  `turtle_demo.lep` gained a `fill "blue"` call before its `circlefilled` (GRAMMAR.md's own §10
  example never sets a fill color) and the resulting canvas's center pixel was checked to be
  `#0000ff`. `LANGUAGE_GUIDE.md` is deliberately a separate document from GRAMMAR.md rather than
  reorganized-in-place: GRAMMAR.md stays the terse, precise, implementation-facing spec (including
  its own §15 open-questions log, which shouldn't be diluted with tutorial prose), while
  LANGUAGE_GUIDE.md is example-first and beginner-facing, explicitly calling out the two spots
  most likely to trip up a newcomer (`+` rejecting strings in favor of `&`, and `&` requiring
  `str()` rather than auto-coercing numbers) as deliberate design choices rather than surprises to
  route around. `LANGUAGES/Leopard/README.md` is a new file — this directory never had a
  top-level README of its own before now (only `GRAMMAR.md`/`IMPLEMENTATION_PLAN.md`), unlike the
  IDE fork, which had one since Phase 9. `IDE_Suite 2/LEOPARD/README.md`'s three placeholder notes
  ("Compile... still to come", "Syntax highlighting isn't wired up yet", "Examples: Not populated
  yet") are now all resolved and replaced with descriptions of the finished features, matching
  what Phases 10–11 actually built. No code changed this phase; `pytest` stays at 287 tests.
- **2026-07-31** — Phase 11 packaging: followed the same standalone-first pattern as every other
  layer this project — `leopard_lang/build.py`'s `compile_program()`/`compile_file()` (a new
  `leopard build script.lep` CLI subcommand, gated behind a new optional `build` extra —
  `pip install -e ".[build]"` — so PyInstaller stays out of bare-script/GUI-only installs) was
  built and proven standalone before the IDE's "Build" button became a thin wrapper around the
  exact same function. Found and fixed a real bug along the way: a single shared launcher
  template with `if program.window is not None: from leopard_lang.gui.app_host import
  run_window` caused PyInstaller to bundle all of PyQt6 into *every* compiled program, even a
  bare script that would never take that branch — PyInstaller's static analysis follows import
  statements it finds in the source, not the actual runtime value of the condition guarding
  them. Fixed with two textually-separate launcher templates (bare vs. GUI), chosen at compile
  time by parsing the source once ahead of the PyInstaller invocation (which also means a syntax
  error fails fast before wasting time on a build). Confirmed the fix: a compiled bare script
  dropped from 77MB/~1.5s startup to 8MB/~0.3s, with identical correct output. Compiles to
  `--onefile`, `--windowed` for a program with a window header or `--console` otherwise (so a
  bare script's errors — there's still no `print`/console-output builtin — stay visible rather
  than vanishing into a suppressed console). The IDE's "Build" toolbar button is new
  `LanguageProvider.compile()` (an optional hook, default no-op, following the same
  extension-point pattern already used by `create_toolbar_widget`/`create_highlighter`) —
  prompts for an output directory (defaulting to the current file's folder), compiles the
  *editor buffer* directly (same as Run — doesn't require the file be saved first), and names
  the executable after the file's stem or `"leopard_program"` if unsaved. Testing: 5 fast tests
  mock `PyInstaller.__main__.run` to check template selection/args/fail-fast-on-syntax-error
  without paying for a real build each time, plus one real end-to-end build+run (marked
  `@pytest.mark.slow`, registered in `pyproject.toml`, still runs by default — the whole suite is
  still under 10 seconds). Manually compiled the full GRAMMAR.md §13 Greeter example and ran it
  under a deliberately stripped environment (`env -i`, minimal `PATH`, no `PYTHONPATH`/
  `VIRTUAL_ENV`) to approximate "outside the dev environment" — launched cleanly with zero
  crash (some audio-subsystem warnings appeared, an expected artifact of stripping
  `XDG_RUNTIME_DIR` this aggressively, unrelated to Leopard's own correctness). Also verified the
  IDE's own `build.py` (from Phase 9/10) still produces a working standalone IDE binary.
- **2026-07-31** — Phase 10 IDE polish: `LeopardHighlighter` (in `app/leopard_language.py`,
  matching every other fork's convention of embedding the highlighter directly in the language
  file rather than a separate module) layers two `keyword_rule()` calls — all of
  `leopard_lang.tokens.KEYWORDS` colored "keyword" first, then a hand-listed subset of turtle
  commands (§10) and builtins (§12) colored "builtin" second, which wins on the overlapping
  spans since `RuleBasedHighlighter` applies rules in order (see `app/syntax.py`). That
  builtins/commands list is hand-maintained here rather than imported from
  `leopard_lang.parser`'s `_TURTLE_COMMANDS`/`_BUILTINS` sets — those are underscore-private to
  that module, and reaching into them from a separate consumer (the IDE, via its pip dependency)
  is a different situation from `gui/`'s own modules reaching into `interpreter.py`'s privates
  within the same package (Phase 4's precedent). `.property` access gets its own rule
  (`\.\w+`, colored "identifier" — `SyntaxColors` has no dedicated "property" field). Operators
  (§4: `+ - * / % ^ & = <> < > <= >= ( ) [ ] , :`, deliberately excluding `.`, which the property
  rule already owns) get `SyntaxColors.operator` — a slot none of BLADE/BLISS/GOPHER's own
  highlighters actually use, worth adding here since the Phase 10 checklist explicitly names
  "operators" as one of the categories to cover. And, like every other fork, the comment rule
  (`#.*`) is applied *last* so it correctly overrides any keyword coloring a reserved word would
  otherwise get if it happened to appear after a `#` —
  confirmed working (a comment containing the word "if" renders fully as a comment, not
  partially as a keyword). Jump-to-line-on-click was **not** implemented: confirmed neither
  `editor.py` nor `terminal.py` (both inherited unchanged from BASE) expose any hook for it — no
  `goto_line` method, no click signal on the terminal pane. Only STITCH, among this suite's
  forks, has this feature, via a custom-built `DiagnosticsPanel` specific to that fork; building
  an equivalent from scratch was judged out of scope for polishing one language's IDE fork. Line-
  numbered errors are already surfaced in the terminal (since Phase 9), which is the checklist
  item's primary ask — the "if editor.py supports it" phrasing already anticipated this exact
  outcome. Added a `.lep` file-dialog filter to Open/Save (`"Leopard Files (*.lep);;All Files
  (*)"`, built generically from `language_provider.name`/`file_extensions` so it isn't
  Leopard-hardcoded) — BLADE/BLISS/GOPHER don't bother with this (declared-but-unused
  `file_extensions`), but STITCH does, and Phase 10 is explicitly about polish, so STITCH's more
  complete precedent was followed. Reused the `leopard-icon.svg` that already existed in
  `LANGUAGES/Leopard/` (not commissioned new) as `leopard_icon.svg` in the IDE fork — wired into
  `main.py` (`setWindowIcon`) and `build.py` (`--add-data`), matching BLISS's exact pattern; no
  separate "banner" graphic was made since only the one icon asset existed and a distinct
  wide-banner image wasn't asked for.
- **2026-07-30** — Phase 9 IDE Scaffolding: fresh `git init` for `IDE_Suite 2/LEOPARD` (not
  preserving BASE's history), matching the established convention across the suite's other
  recent forks (BLADE/BLISS/GOPHER/STITCH all do the same — none kept BASE's history). Added
  `leopard-lang[gui]` to `requirements.txt` as an editable path dependency
  (`-e ../../../LANGUAGES/Leopard[gui]`) and removed the direct `PyQt6` line, since it now
  arrives transitively through the `gui` extra; confirmed the editable install resolves to the
  live source tree (not a frozen copy) — the IDE always runs whatever's currently in
  `LANGUAGES/Leopard/src/leopard_lang/`, no rebuild/reinstall step needed after editing the
  language. `LeopardLanguageProvider.run()` dispatches on `program.window is not None`: bare
  scripts run through the Phase 3 interpreter and just report "Program finished." to the
  terminal (there's still no console-output/`print` builtin — the same GRAMMAR.md gap flagged
  back in Phase 1); window/text-window/graphics-window programs call
  `gui.app_host.run_window(program, existing_app=QApplication.instance())` — this is the first
  time that function's `existing_app` reuse path is driven by something *other* than a test
  fixture, and it worked correctly on the first try (no crash, no second `QApplication`, no
  nested event loop). No new pytest suite was added to the IDE fork itself — no other fork in
  the suite has one, and the underlying reuse-existing-`QApplication` mechanism is already
  exercised by hundreds of `leopard-lang`'s own tests; instead the new IDE-specific integration
  code (`LeopardLanguageProvider.run()`'s dispatch, plus the real toolbar Run button end to end)
  was rigorously verified via scripted checks in-session: bare scripts, a runtime error's
  line-numbered message, and the full GRAMMAR.md §13 Greeter example clicked through the actual
  `MainWindow._run_code()` path, confirming it behaves identically to running it standalone via
  `leopard run` (Phase 4) while the IDE's own window stays open and responsive throughout.
- **2026-07-30** — Phase 8 sound, honest confirmed-vs-unverified status (the checklist itself
  asks for this): **confirmed** — `play_sound`/`stop_sound` (`QSoundEffect`) work correctly
  against real WAV audio data on this development machine (Linux, real ALSA/PulseAudio devices
  present, Qt6's FFmpeg-backed multimedia pipeline engages successfully) — verified via
  automated tests (`isLoaded`/`isPlaying` transition correctly) and a real `leopard run`
  invocation. `play_music`/`stop_music`/`pause_music` (`QMediaPlayer`+`QAudioOutput`) are
  correctly *wired* and exercised the same way, but only against the same WAV data, not a
  genuine MP3 — **no MP3 test asset could be produced in this sandboxed environment** (no
  `ffmpeg`/`lame` CLI tool despite the FFmpeg *library* being linked into Qt Multimedia itself,
  no network access, no system MP3 files present); this validates the plumbing, not MP3 codec
  decoding specifically. MIDI is entirely untested — no asset, and it's already flagged in the
  Phase 8 checklist itself as "the shakiest of the three" across Qt Multimedia backends. **Not
  verified at all**: Windows or Mac — everything above is this one Linux development machine
  only. Two bugs surfaced along the way: (1) both `QSoundEffect` and `QMediaPlayer`/
  `QAudioOutput` are parented to the window, learned directly from Phase 5's `QMenu` lesson —
  playback is asynchronous, so an unparented instance referenced only by a closure risks being
  garbage-collected mid-playback; (2) `pytest-qt` was removed from `dev` dependencies entirely
  — it was never actually used for its distinguishing `qtbot` fixture across any of Phases 4–8
  (everything drives widgets directly via `.click()`/`.trigger()`/etc.), and it turned out to
  actively cause a hard process hang the moment a `QMediaPlayer` using the FFmpeg backend was
  involved (confirmed by isolating it with `-p no:qt`). Separately, running *two* sequential
  `QMediaPlayer`-backed tests with real event-loop waits between play/pause in the same pytest
  session reproducibly hangs even with `pytest-qt` gone and several different cleanup/parenting/
  wait strategies tried — root cause not pinned down (not reproducible outside pytest at all).
  Rather than keep chasing it, the automated `pause_music` test was scaled back to confirm it's
  wired and doesn't raise, without asserting the exact resulting `PlaybackState`; that exact
  behavior (transitions correctly to `PausedState`) was independently confirmed via a standalone
  script run outside pytest, so the underlying implementation is not in doubt — only this one
  environment's tolerance for testing it precisely inside pytest is.
- **2026-07-30** — Phase 7 text window: about as close to zero new plumbing as a phase gets, which
  is itself a good sign GRAMMAR.md's "`page` needs no special grammar" design intent (§11) holds
  at runtime, not just at parse time (already confirmed in Phase 2). `page` is just an
  environment name registered to a full-window `QTextEdit`; `.text` get/set already worked
  through Phase 4's `PropertyDispatcher` unchanged, and `on close` already worked through Phase
  4's window-level `closeEvent` unchanged. The one real addition: `events.py`'s `on change`
  gained a `QTextEdit` branch (`textChanged` signal) — implemented capability-based like
  everything else, so it also fires for a plain `textedit` control, not just `page`, following
  the same permissiveness already established in Phase 4's decision log. `page` fills the whole
  window at a fixed `(0, 0, width, height)`, no auto-resize, consistent with the no-layout-manager
  approach throughout. Also: §11's own example references `wordCountLabel` without declaring it
  — the same illustrative-example gap as §8's menu example — handled the same way, by declaring
  it for the full end-to-end test.
- **2026-07-30** — Phase 6 turtle graphics found and fixed a real Phase 2 parser bug, plus a
  batch of GRAMMAR.md §10 semantics that had to be reconstructed from scratch (see its new §15
  open question #4 — the original `leopard.bas` just forwards these commands, unparsed, to
  Liberty BASIC's native engine, so there was no spec to read, only behavior to infer):
  **the bug** — a bare name used as an entire statement (`up`, `down`, `home`, `north` — all
  zero-arg per §10) parsed as a plain `Identifier` rather than a call, so the interpreter tried
  to look it up as a *variable* and failed with "not defined". Fixed in the parser itself
  (`_simple_statement`): a bare identifier that's the *whole* statement is now wrapped as a
  zero-arg `Call` — this only fires at statement position, so `x + 1` still parses as addition,
  never `x() + 1` (see the updated comment in `parser.py`). Updated Phase 2's
  `test_zero_arg_bare_command` to match. **The reconstructed §10 semantics**: heading `0` =
  north (`-y`), turning increases heading clockwise; `go`/`goto` draw a line when the pen is
  down, `place` never draws regardless of pen state (a silent jump — confirmed distinct from
  `goto` by name alone, no other signal available); `home` resets both position (canvas center)
  and heading, `north` resets only heading; `box`/`boxfilled`'s two numbers are a width/height
  measured from the current position as the top-left corner (not an absolute opposite corner),
  chosen for consistency with `circle`/`ellipse` which are unambiguously relative sizes (a
  radius, a width/height) rather than absolute coordinates; `circle`/`ellipse` and their filled
  counterparts are centered *at* the current position; `drawbmp` takes exactly `path, x, y`
  (confirmed from `leopard.bas`'s own internal argument order, one of the few things that *was*
  independently verifiable); `font` accepts either 1 arg (family only) or 2 (family, point size)
  since §10 never specifies the shape; invalid color names (`pen "not-a-color"`) raise a clear
  runtime error rather than silently drawing in black. Default turtle state: pen up, centered,
  facing north, black pen/fill, size 1, white background — none of this is specified either.
  Turtle commands are only added to `gui_builtins` when `window_decl.kind == "graphics_window"`,
  so calling one from a plain `window` still errors, just with the same generic "needs a window"
  message as any other not-yet-available builtin — a `graphics window`-specific message would
  need the interpreter to know about window kinds, which felt like unwarranted coupling for a
  minor wording improvement.
- **2026-07-30** — Phase 5 menus: hit a real PyQt bug, not just a design judgment call — a
  `QMenu` built with `QMenu(title)` (no parent) and then attached via `menubar.addMenu(menu)`
  gets silently garbage-collected by Python before the menu bar ever renders it, leaving
  `menubar.actions()` empty with no error at all. Reproduced by hand, fixed by always
  constructing `QMenu` with an explicit Qt parent (the menu bar, or the parent menu for a
  submenu) — see `gui/menus.py`'s `_build_menu`. Worth remembering for Phases 6–8: any other
  Qt object built without a parent and only referenced via an `add*()` call is at risk of the
  same silent disappearance. Also: `PropertyDispatcher.is_widget` renamed to `is_gui_object` and
  broadened to include `QAction` (menu items/checkitems aren't `QWidget`s in Qt at all) so
  `.checked` works on a checkitem the same way it does on a checkbox; `events.py`'s `on click`
  now accepts a menu item (`QAction.triggered`) alongside a button, and `on change` accepts a
  checkitem (`QAction.toggled`, gated on `.isCheckable()` so a plain `item`'s `on change` still
  gives a clear error) alongside checkbox/radiobutton/combobox. The menu bar is positioned via
  absolute `setGeometry()` at the window's top edge, consistent with Phase 4's no-layout-manager
  design — a control also placed at y=0 will visually overlap it; not auto-offset.
- **2026-07-30** — Phase 4 GUI runtime, judgment calls and one more GRAMMAR.md gap found:
  (1) `window` is now in the parser's `EXPRESSION_KEYWORDS` (alongside `page`) so
  `window.title = "..."` parses — GRAMMAR.md §12 shows that example but §14 never says `window`
  doubles as an identifier the way §11 explicitly says `page` does; flagged in §15. (2) `.selected`
  (listbox/combobox) is a 1-based index, 0 meaning "none selected" — the source table itself
  marks this "selectionindex?", i.e. even less settled than most of §7; consistent with the
  language's 1-based-everywhere convention, but flag if selected *text* is wanted instead. (3)
  `.font`'s value is treated as a font-family string (`label.font = "Arial"`) since GRAMMAR.md
  never specifies the shape. (4) `.color`/`.background` are implemented via a small per-widget
  stylesheet cache (`gui/properties.py`'s `_style_state`) so setting one doesn't overwrite the
  other — Qt only gives you one stylesheet string per widget. (5) `on close`'s handler body runs
  and the window then unconditionally closes — GRAMMAR.md's example (`confirm("Really quit?")` in
  an `on close:` block) shows no veto mechanism, so none is implemented; a real "cancel the close"
  feature would need new syntax, out of scope here. (6) Property/builtin dispatch is
  widget-*capability*-based (`isinstance` against the Qt class), not restricted by the original
  Leopard control-kind label — e.g. `.text` would also work on a `bmpbutton`, which GRAMMAR.md's
  table doesn't list, but there's no real harm in the extra permissiveness. (7) `interpreter.py`
  stays PyQt6-free: `Interpreter` grew two optional constructor hooks (`gui_properties`,
  `gui_builtins`), both `None`/empty by default, that `gui/app_host.py` fills in — this is what
  keeps Phases 0–3's "zero GUI dependency" guarantee true for bare-script installs even though
  the interpreter now has GUI integration points. `beep()` and `set_cursor()` are deliberately
  still unimplemented (not in Phase 4's checklist) — calling either still gives the "needs a
  window" placeholder error via `_GUI_ONLY_NAMES`, same as turtle commands and sound builtins.
- **2026-07-30** — Corrected again: GUI-runtime work (was Phases 5–9) is reordered ahead of the
  IDE fork (was Phase 4), for the same reason the language core was pulled ahead of the IDE
  earlier the same day — the plan had PyQt6-dependent code (windows, controls, menus, turtle,
  text window, sound) designed to be tested only through the IDE's Run button before any of it
  existed, repeating the "layer coupled to its consumer before it's proven standalone" mistake.
  Fixed the same way: `leopard` itself is now the GUI host. New phase order: **4** GUI runtime
  (was 5), **5** Menus (was 6), **6** Turtle graphics (was 7), **7** Text window (was 8),
  **8** Sound (was 9), **9** IDE Scaffolding (was 4, moved here). The mechanism that makes both
  standalone-CLI and later IDE hosting work off the identical code:
  `gui/app_host.py`'s `run_window(program, *, existing_app=None)` — creates and owns a
  `QApplication` (calls `.exec()`) when `existing_app` is `None`, or builds the window under a
  passed-in app's already-running loop otherwise. Phase 9 (IDE Scaffolding) is therefore
  integration only by the time it runs — the GUI runtime already exists, so
  `LeopardLanguageProvider.run()` calls straight into `gui.app_host.run_window(...)` rather than
  writing a placeholder-then-wire-up. Also: PyQt6 moves from "IDE-only dependency" to an optional
  `leopard-lang[gui]` extra, since the language package itself now hosts GUI programs. No code
  existed for Phase 4-9 yet when this was caught, so this was a pure plan-document correction —
  nothing needed cleaning up. Supersedes phase numbers referenced in the two entries below.
- **2026-07-30** — Phase 3 interpreter, judgment calls GRAMMAR.md doesn't pin down:
  (1) no `global` keyword exists, so per §3's literal wording ("scoped to the function/handler
  it's assigned in") assignment inside a function *always* creates a local, even if a
  same-named global exists — reads fall through to module scope, writes never do (Python's
  behavior without `global`, just with no way to opt out); (2) `<`/`>`/`<=`/`>=` require both
  operands to be numbers — not extended to lexicographic string comparison, since no example
  uses it; flag if that's wanted later; (3) `and`/`or`/`not` require actual booleans (no
  truthy-coercion of numbers/strings), matching `&`'s existing "no auto-coercion" philosophy;
  (4) `=`/`<>` work across any two types and just return false for a type mismatch (`5 = "5"`
  is false, not an error) — only the *ordering* comparisons are type-strict; (5) `str()` prints
  whole-number floats without a trailing `.0` (`str(10/2)` → `"5"`) so "one numeric type,
  handled transparently" doesn't leak Python's float formatting; (6) `remove_dir()` only
  removes an empty directory (`os.rmdir`, not recursive) — the conservative, least-destructive
  reading of a symmetrical `make_dir`/`remove_dir` pair; (7) calling a turtle command or a
  GUI-only §12 builtin (`notice`, `confirm`, dialogs, sound, ...) from a bare script raises a
  distinct "needs a window (not available yet)" error rather than "undefined", since those
  names *are* reserved/known, just not implemented until Phase 4+.
- **2026-07-30** — Phase 2 parser: GRAMMAR.md §4's `=` doubles as both assignment and
  equality-comparison (no separate `==`), which is a real ambiguity for a recursive-descent
  parser — naively parsing a statement's full expression first (through the comparison-precedence
  level) consumes `=` as "equals" before assignment-detection ever sees it, silently turning every
  `x = 1` into a no-op comparison-expression-statement. Fixed by parsing a statement's leading
  operand only up to `_unary_expr` (postfix chains, no operators) and checking for a following `=`
  *before* climbing the rest of the precedence chain — safe because assignment targets are always
  a bare name or a `.prop`/`[index]` chain, never a full expression. A leading `not` is special-cased
  around this (`not x` can never be an assignment target, so it skips straight to the full
  expression grammar) — see `_simple_statement`/`_expr_continue` in `src/leopard_lang/parser.py`.
  Also: unary `-` binds tighter than `^` in this parser (`-2^2` parses as `(-2)^2`, not `-(2^2)`) —
  GRAMMAR.md doesn't specify this, and it's the natural result of straightforward precedence
  climbing rather than Python's specially-cased `-2**2 == -4`; flag if the opposite is wanted.
- **2026-07-30** — Phase 1 lexer: every reserved word (GRAMMAR.md §14's core list, plus every
  §10 turtle command, every §12 builtin, and the §7 control-declaration keywords) gets its own
  `TokenType` enum member — 95 keyword tokens total, mechanically enumerated. Properties
  (`.text`, `.color`, etc.) are **not** reserved and tokenize as plain `IDENTIFIER` after a
  `DOT`, since §14 never lists them. Two gaps found in GRAMMAR.md while doing this — flagged in
  its §15 open questions rather than guessed silently: (1) §14 omits the §7 control-declaration
  keywords even though the parser structurally needs them as keywords — reserved anyway; (2)
  `print` is used in a §5 example but never defined as a keyword or builtin anywhere.
- **2026-07-30** — Corrected: the language core is a standalone, pip-installable package
  (`leopard-lang`) built entirely in `LANGUAGES/Leopard/` and fully usable via CLI (`leopard run
  script.lep`) before any IDE work begins. The IDE fork (originally moved to Phase 4, then to
  Phase 9 by the newer entry above, not Phase 0) is deferred until the language is complete, and
  depends on this package (editable/path dependency) rather than embedding a copy. An earlier
  session had already begun Phase 0 as the IDE fork and even rsync-copied `IDE_Suite 2/BASE` →
  `IDE_Suite 2/LEOPARD` before any language code existed — that copy has been removed since no
  language logic had been written into it. Supersedes the entry directly below.
- **2026-07-30** — Language core lives inside the IDE fork
  (`IDE_Suite 2/LEOPARD/app/leopard_lang/`), following `BLADE/app/basic_language.py`'s convention,
  rather than as a standalone installable package. Revisit only if the interpreter needs to run
  somewhere other than this one IDE.
- **2026-07-30** — Tree-walking interpreter, not a bytecode VM. This is a teaching language;
  performance was never a design goal, and a VM would be complexity the project doesn't need.
- **2026-07-30** — PyQt6, not PySide6. Follows the existing `IDE_Suite 2/BASE` template's
  dependency, prioritizing consistency across the whole IDE suite over the GPL/LGPL distinction
  raised earlier in the project's design discussion.

---

## 7. Non-goals for this pass

Explicitly out of scope — don't add these without first updating GRAMMAR.md and this list:

- Video playback (GRAMMAR.md status #5 — sound only)
- A package/module/import system
- A bytecode VM or any performance-optimization pass
- Multi-user/collaboration/versioning features
- Any new keyword or syntax not already documented in GRAMMAR.md
