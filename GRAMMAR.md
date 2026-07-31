<!-- title: Leopard Language — Grammar & Vocabulary (Draft v0.3) -->

# Leopard — Grammar & Keyword Vocabulary
### Draft v0.3 — working document, revised as we go

For build status, phase checklists, and where implementation currently stands, see
`IMPLEMENTATION_PLAN.md` in this same directory.

**Status:** decisions locked in so far:
1. Blocks use **Python-style colon + indentation** (no `end if` / `end click` markers).
2. `on click` and friends are **real code blocks**, not fixed 3-line action tuples.
3. Controls are **user-named and unlimited** (`button "Save" as btnSave`), not `button1..button5`.
4. Lists/arrays are **1-based** (`fruits[1]` is the first element) — avoids off-by-one errors for beginners.
5. Sound only, no video, for this pass.
6. **Full menu support**: submenus, checkable items, accelerators — and available in every window type, not just `window`.
7. `text window` mode is a **fully editable** text area, not a read-only scrollback.
8. Errors report as **line number + plain-English message**.
9. Modulo is **`%`**, not `mod`. `else if` is **`elseif`**, one word. String concatenation is **`&`**, not `+` — `+` is numeric-only.
10. `&` requires **explicit conversion** — no auto-stringifying numbers/booleans. Deliberate friction so beginners learn strings and numbers are different types.
11. `page` (the implicit text-area target in `text window` blocks) is a **reserved word**, not usable as a variable/function/control name anywhere in a program.

Everything below builds on those calls. Nothing here is final — flag anything that should change.

---

## 1. Lexical basics

| Thing | Rule |
|---|---|
| Comments | `# like this`, to end of line |
| Strings | double-quoted: `"hello"` |
| Numbers | `42`, `3.14` — one numeric type, int/float handled transparently |
| Booleans | `true`, `false` |
| Identifiers | letters, digits, `_`; case-sensitive |
| Blocks | a line ending in `:` opens a block; the next line's indentation defines the block; dedent closes it |
| Statement separator | newline (no `;`) |

No line numbers, no `Line Input`-per-argument parsing — this is a real tokenizer/parser, not the original's read-one-line-per-field scheme.

---

## 2. Program shape

Leopard originally forced every program to declare `window` / `text window` / `graphics window` / `no window` up front. That's kept, with one simplification: **a plain script with no window header *is* "no window" mode** — the explicit keyword is dropped as redundant.

```
window "My App", 500, 400:
    ...controls, menus, event handlers...

text window "Log Viewer", 600, 400:
    ...

graphics window "Turtle Demo", 640, 480:
    ...turtle commands...
```

`title, width, height` collapses the original's separate `window title` / `window size` sub-blocks into one header line.

---

## 3. Variables & types

No more `varone$`…`varfive$`. Any name is a variable, created on first assignment.

```
score = 0
name = "Chuck"
found = false
fruits = ["apple", "banana", "cherry"]   # list literal
first = fruits[1]                        # 1-based: "apple"
```

Lists are **1-based** throughout — `fruits[1]` is the first element, `fruits[fruits.length]` is the last.

**Scoping — only `function` calls get their own scope.** A `function` call (§6) gets a private
scope: assignments made inside it never affect a same-named variable outside it, even one that
already exists. Everywhere else — the top level of a program, a window's own setup code, and
**every `on ...:` event handler in that window** — shares exactly one scope. An event handler is
*not* a function-like scope of its own, so a variable assigned in one handler is visible (and
stays assigned) in every other handler in the same window:

```
window "Shared state", 300, 150:

    textbox as nameBox at 10, 10, 200, 24
    button "Save name" as saveButton at 10, 44, 100, 24
    button "Greet" as greetButton at 120, 44, 100, 24
    label "" as resultLabel at 10, 78, 260, 24

    saved_name = ""

    on click saveButton:
        saved_name = nameBox.text

    on click greetButton:
        resultLabel.text = "Hello, " & saved_name & "!"
```

Clicking "Greet" sees whatever "Save name" most recently stored in `saved_name` — two separate
event handlers, reading and writing the same shared variable. This is the opposite of what
happens with a `function` call (§6), where an assignment never escapes that one call — worth
knowing up front, since it's the reverse of what a beginner coming from a language with
per-function/per-block scoping everywhere would expect from something that *looks* like a
function body.

---

## 4. Expressions & operators

| Category | Operators | Notes |
|---|---|---|
| Arithmetic | `+  -  *  /  %  ^` | `%` = modulo, `^` = power |
| String concatenation | `&` | dedicated operator — `"Score: " & str(score)` |
| Comparison | `=  <>  <  >  <=  >=` | `=` doubles as equality (BASIC-style, no separate `==`) |
| Logical | `and  or  not` | English words, not `&&`/`\|\|` — matches BASIC/beginner spirit |
| Grouping | `( )` | standard precedence |

`+` is numeric-only now that `&` owns concatenation — using `+` on two strings is a runtime error that suggests `&` (a beginner writing `"a" + "b"` gets pointed at the right operator instead of silently getting `"ab"` and being confused later when `+` behaves differently on numbers-as-strings).

`&` requires both sides to already be strings — `"Score: " & 5` is also a runtime error, pointing at `str()`. No auto-coercion, on either side. It's a small amount of friction in exchange for beginners internalizing early that `5` (number) and `"5"` (string) aren't the same thing — the original's `""; x$` idiom papered over that distinction, and it's exactly the kind of thing that becomes a confusing surprise later once a beginner moves on to a language that isn't so forgiving.

```
"Score: " & str(score)      # correct
"Score: " & score           # runtime error: cannot & a string and a number — use str(score)
```

---

## 5. Control flow

All new — the original interpreter had `if/then` internally but never exposed it to Leopard programs.

```
if score > 10:
    notice "You win!"
elseif score > 0:
    notice "Keep going."
else:
    notice "Try again."

while count < 5:
    count = count + 1

for i = 1 to 10 step 2:
    print i

break
continue
```

`for var = start to end [step n]` chosen over a `range()`-style builtin — closer to the original's turtle-ish, spelled-out BASIC feel.

---

## 6. Functions

One keyword, not separate `sub`/`function` — a function that never `return`s is just a procedure. Keeps the vocabulary smaller.

```
function greet(who):
    return "Hello, " & who

function log(message):
    outputBox.text = outputBox.text & message & "\n"
```

---

## 7. Controls & properties

This is the biggest structural change. Leopard had ~15 separate keywords just to get text in and out of controls (`print textbox`, `textbox color`, `change text`, `print textboxtwo`, …) because it had no assignment. Real assignment collapses nearly all of them into **`control.property = value`**.

**Declaration** (`as <name>` replaces the numbered slot; `at x, y, w, h` replaces the positional args the original already passed):

| Original keyword | New declaration |
|---|---|
| `textbox` | `textbox as name at x, y, w, h` |
| `textedit` | `textedit as name at x, y, w, h` |
| `text` (static label) | `label as name at x, y, w, h` |
| `button` | `button "Caption" as name at x, y, w, h` |
| `bmpbutton` | `bmpbutton "file.bmp" as name at x, y, w, h` |
| `listbox` | `listbox as name at x, y, w, h` |
| `combobox` | `combobox as name at x, y, w, h` |
| `radiobutton` | `radiobutton "Caption" as name at x, y, w, h` |
| `checkbox` | `checkbox "Caption" as name at x, y, w, h` |
| `groupbox` | `groupbox "Caption" as name at x, y, w, h` |

(`menu` moves to its own section below — full menu support outgrew a one-line table entry.)

**Reading/writing state** (was: `print textbox`, `textbox color`, `print textedit`, `change text`, `textbox file`, `textedit color`, …):

| Property | Applies to | Old equivalent(s) |
|---|---|---|
| `.text` | textbox, textedit, label, button | `print textbox`, `print textedit`, `change text` |
| `.color` | textbox, textedit, listbox, combobox, label | `textbox color`, `textedit color`, `combobox color`, `listbox color`, `text color` |
| `.background` | any control / window | `background color` |
| `.font` | any control / window | `font` |
| `.checked` | checkbox, radiobutton | (was implicit in onclick tuple) |
| `.items` | listbox, combobox | `print listbox`…`print listboxfive` (5-slot ceiling gone — `.items = [...]`, `.items.add(x)`) |
| `.selected` | listbox, combobox | `selectionindex?` |
| `.visible`, `.enabled` | any control | *(new — original had neither)* |

```
nameBox.text = "placeholder"
outputArea.color = "darkblue"
fruitList.items = ["Apple", "Banana", "Cherry"]
fruitList.items.add("Date")
first = fruitList.items[1]   # 1-based, same as list literals
```

---

## 8. Menus (full support)

The original had one menu bar, one level deep, with accelerators (`&`) and separators (`|`) but no submenus and no checkable items:
`menu #main, "&File", "&New...", [BmpButton1], |, "&Open...", [OpenFile], ...`

Full support now — arbitrary submenu depth, checkable items, same `&`-accelerator convention (Qt honors it natively). Unlike the original (menu bar only made sense in its one `window` mode), `menu` blocks are legal in **any** program shape — `window`, `text window`, or `graphics window` — so a turtle-graphics program can have a "File > Save Drawing" menu, a text-editor-style `text window` program can have a full "File/Edit" menu bar, and so on:

```
window "Editor", 500, 400:

    menu "&File" as fileMenu:
        item "&New..." as mnuNew
        item "&Open..." as mnuOpen
        separator
        submenu "Open &Recent" as mnuRecent:
            item "report.lep" as mnuRecent1
        separator
        item "E&xit" as mnuExit

    menu "&View" as viewMenu:
        checkitem "Show &Toolbar" as mnuToolbar

    on click mnuNew:
        editorBox.text = ""

    on click mnuExit:
        close_window()

    on change mnuToolbar:
        toolbar.visible = mnuToolbar.checked
```

| Piece | Meaning | Old equivalent |
|---|---|---|
| `menu "&Label" as name:` | top-level menu-bar entry | `menu #main, "&File", ...` |
| `item "&Label" as name` | clickable entry, fires `on click name` | one `"&New...", [Handler]` pair |
| `checkitem "&Label" as name` | toggle entry with `.checked`, fires `on change name` | *(new — original had none)* |
| `submenu "&Label" as name:` | nested menu, any depth | one level only, via re-declaring `menu #main, "Recent", ...` |
| `separator` | divider line | `\|` |

---

## 9. Events

Replaces the fixed `boce$/boct$/bocw$` action-tuple entirely. `on <event> <control>:` opens a block of ordinary statements. Menu items use the same mechanism (see Section 8).

```
button "Greet" as btnGreet at 220, 10, 80, 24

on click btnGreet:
    if nameBox.text = "":
        notice "Type your name first."
    else:
        notice "Hello, " & nameBox.text
```

| Event | Applies to | Old equivalent |
|---|---|---|
| `on click` | button, bmpbutton, menu item | `button onclick`, `bmpbutton onclick`, menu handler |
| `on change` | checkbox, radiobutton, combobox, checkitem, text window | `checkbox onclick`, `radiobutton onclick`, `combobox onclick` |
| `on select` | listbox, combobox | `listbox onclick` (double-click), `combobox onclick` |
| `on close` | window | `trapclose` |

---

## 10. Turtle graphics (graphics window)

Leopard's turtle vocabulary was already clean — kept almost verbatim as statements valid inside a `graphics window:` block:

```
graphics window "Turtle Demo", 640, 480:
    pen "red"
    size 3
    down
    go 100
    turn 90
    go 100
    up
    goto 300, 300
    circlefilled 40
```

`up down home go goto place turn north fill pen size font text backcolor box boxfilled circle circlefilled ellipse ellipsefilled drawbmp` — all carried over unchanged in name and meaning.

---

## 11. Text window (fully editable)

Original's `text window` type was a read-only scrollback the program could `print text` into or load a file with `open file`. Making it fully editable means treating the whole content area as **one implicit textedit control**, reusing the property/event vocabulary from Sections 7 and 9 instead of inventing new keywords — the same pattern turtle graphics already uses (an implicit target, no `as name` needed):

```
text window "Notes", 600, 400:

    page.text = "Start typing..."

    on change page:
        wordCountLabel.text = "Editing..."

    on close:
        write_file("notes.txt", page.text)
```

`page` is the reserved name for the text area inside a `text window` block. It's a genuine reserved word — `page` can't be used as a variable, function, or control name *anywhere* in a Leopard program, not just inside a `text window` block, so there's never ambiguity about what `page` refers to when reading someone else's code. The old `print text` / `open file` actions become `page.text = page.text & "..."` and `page.text = read_file(path)` — no special-cased keywords required.

---

## 12. Builtin actions

The original's ~40 fixed onclick-action keywords become ordinary builtin functions/statements, callable anywhere (not just inside a click handler) — another side effect of making handlers real code.

| Old keyword | New builtin |
|---|---|
| *(new — required by `&`'s no-coercion rule)* | `str(value)` → string, `num(text)` → number |
| `notice` | `notice "text"` |
| `confirm` | `confirm("Really quit?")` → boolean |
| `varN prompt` | `ask("Enter name:")` → string |
| `beep` | `beep()` |
| `date` | `date()` |
| `time` | `time()` |
| `write file` / `append file` | `write_file(path, text)` / `append_file(path, text)` |
| `read file textedit` | `read_file(path)` → string |
| `delete` | `delete_file(path)` |
| `makedir` / `removedir` | `make_dir(path)` / `remove_dir(path)` |
| `file check` | `file_exists(path)` → boolean |
| `filedialog` | `open_file_dialog()` / `save_file_dialog()` |
| `colordialog` | `color_dialog()` |
| `fontdialog` | `font_dialog()` |
| `printerdialog` / `print` (to printer) | deferred — niche even in 2013 |
| `internet` | `open_url(url)` |
| `email` | `open_email(address)` |
| `run` / `run text` | `run_program(cmd)` |
| `ascii` | `ascii(char)` |
| `cursor` | `set_cursor(style)` |
| `close window` | `close_window()` |
| `maximize` / `minimize` | `maximize_window()` / `minimize_window()` |
| `change window title` | `window.title = "..."` (property, not a call) |
| `playwav` / `stopwav` | `play_sound(path)` / `stop_sound()` |
| `play mp3` / `play midi` / `stop music` / `pause music` | `play_music(path)` / `stop_music()` / `pause_music()` — via Qt Multimedia, cross-platform |
| `download file` | `download_file(url, path)` |

**Confirmed dropped, sound-only scope** (no cross-platform equivalent proposed, video explicitly out of scope for this pass): `cd open`/`cd close` (CD-tray door), `swap mouse`/`swap mouse back`, `restart` (Windows shutdown API), `play avi`/`play avi fullscreen`, `play mpeg`/`play mpeg fullscreen`/`pause video`/`stop video`.

---

## 13. Worked example

Pulls together window, controls, an event handler, and a function — none of which could coexist in a single original Leopard program (no functions existed at all):

```
window "Greeter", 360, 160:

    label "Your name:" as nameLabel at 10, 10, 100, 24
    textbox as nameBox at 120, 10, 200, 24
    button "Greet" as btnGreet at 120, 44, 80, 24
    label "" as resultLabel at 10, 84, 320, 24

    function greeting_for(who):
        if who = "":
            return "Please enter a name."
        else:
            return "Hello, " & who & "!"

    on click btnGreet:
        resultLabel.text = greeting_for(nameBox.text)

    on close:
        confirm("Really quit?")
```

---

## 14. Reserved words

Consolidated list of everything that can't be used as a variable, function, or control name, now that the vocabulary has grown past the point of keeping this in your head:

`window`, `text window`, `graphics window`, `as`, `at`, `true`, `false`, `and`, `or`, `not`, `if`, `elseif`, `else`, `while`, `for`, `to`, `step`, `break`, `continue`, `function`, `return`, `menu`, `item`, `checkitem`, `submenu`, `separator`, `on`, `click`, `change`, `select`, `close`, `page`

Plus every turtle-graphics command from Section 10 (`up`, `down`, `home`, `go`, `goto`, `place`, `turn`, `north`, `fill`, `pen`, `size`, `font`, `text`, `backcolor`, `box`, `boxfilled`, `circle`, `circlefilled`, `ellipse`, `ellipsefilled`, `drawbmp`) and every builtin from Section 12.

---

## 15. Open questions for the next pass

Everything from v0.1 and v0.2 is resolved. Five gaps have surfaced since, while implementing and
exercising the language (see IMPLEMENTATION_PLAN.md for the phase each was found in):

1. **§14's reserved-word list omits the §7 control-declaration keywords** (`textbox`,
   `textedit`, `label`, `button`, `bmpbutton`, `listbox`, `combobox`, `radiobutton`,
   `checkbox`, `groupbox`). They're unambiguously needed as keywords for the parser to
   recognize declarations, so the lexer reserves them regardless (see IMPLEMENTATION_PLAN.md's
   decisions log) — §14 should be updated to list them explicitly.
2. **`print` is used in §5's `for` loop example** (`for i = 1 to 10 step 2: print i`) but is
   never defined anywhere as a keyword or builtin — §12's builtin table has no `print` entry.
   Either add it to §12 (what does it do — write to a console pane? only meaningful in a
   `text window`/graphics context?) or replace the example with an already-defined builtin.
3. **§12's `window.title = "..."` example implies `window` doubles as an identifier** referring
   to the current window (the same way §11 explicitly reserves `page` for the text-area target
   inside a `text window`), but §14's reserved-word list and §11 never actually say this for
   `window`. Phase 4 treats it as true for all three window kinds (not just plain `window`
   headers) since there's no other sensible reading of that example — §11/§14 should say so
   explicitly. Also unresolved: `.selected` is marked "selectionindex?" in §7's own table, and
   `.font`'s value shape (family name? size? both?) is never specified.
4. **§10's turtle commands have no documented pixel semantics at all** — GRAMMAR.md only says
   they're "carried over unchanged in name and meaning" from `leopard.bas`, but that file just
   forwards each one, verbatim and unparsed, straight through to Liberty BASIC's native
   graphics-window engine (confirmed by reading it — e.g. `pen` literally becomes LB's `color`
   command). So §10 has no real spec of its own: heading convention (0 = north? clockwise?),
   what `box`/`ellipse`'s two numbers measure (a corner? a width/height from current position?),
   whether `goto`/`place` differ only in whether they draw, what `home` resets besides position.
   Phase 6 reconstructs a best-effort, internally-consistent set of answers to all of this —
   see IMPLEMENTATION_PLAN.md's Phase 6 decisions-log entry for the specifics — but none of it
   is verified against a real Liberty BASIC install; §10 should eventually spell these out
   directly instead of pointing at an undocumented dependency.
5. **List index assignment (`list[i] = value`) is not implemented**, discovered while writing
   Phase 12's `todo_capstone.lep` example. The parser accepts it — `_simple_statement` treats
   any `ast.Index` base the same as `ast.PropertyAccess` and produces a `PropertyAssignment`
   node either way (GRAMMAR.md never distinguishes the two as assignment targets) — but
   `Interpreter._exec_PropertyAssignment` only ever handles a `PropertyAccess` target (a GUI
   control's `.property`); an `Index` target falls through to that method's final `raise` and
   fails with a confusing "property assignment needs a GUI control (not available yet)" error,
   even in a program with no window at all. Confirmed empirically: `x = [1, 2, 3]` then
   `x[2] = 99` raises that exact error. Only reading (`x[2]`) and appending (`.add()`) actually
   work; there's no way to replace or remove an existing element in place — every example that
   needs to do so (Phase 12's `todo_capstone.lep`, `05_lists.lep`) works around it by building a
   whole new list with `.add()` and reassigning the variable to it. Worth deciding either way:
   implement `list[i] = value` for real (straightforward — mirror `_eval_Index`'s bounds-checked
   read path), or keep lists add-only/rebuild-only and document that as an intentional design
   choice in §3/§7 rather than a silent gap.

---

## 16. Error handling

There is no `try`/`catch`/`on error` construct anywhere in Leopard, and no way to write one —
this is a deliberate omission (status #8 above), not a gap. **Every error stops the program
immediately**, at the exact statement that caused it. A Leopard program cannot recover from an
error, catch one, or continue past one; the only way to avoid one is to check for the risky
condition *before* it happens.

Two categories, both reported the same way — `Line N: message` (status #8):

- **Syntax errors** are caught while parsing, before a single statement has run. E.g.
  `Line 12: expected ':' after 'if' condition`.
- **Runtime errors** happen partway through an already-running program — e.g. `+` between two
  strings, `&` with a non-string operand (§4), a list index out of range or not a whole number
  (§3), calling `num()` on text that isn't a valid number, calling something that isn't defined,
  or calling a turtle command/GUI builtin (§12) from a program with no window. Whatever ran
  before the error already took effect (a file already written, a window already shown); nothing
  after it does.

Where the message ends up depends on how the program is running, but the format is identical in
all three:

| Running via | Message goes to |
|---|---|
| `leopard run script.lep` | stderr; the process exits with a non-zero status |
| The Leopard IDE's Run button | the terminal/console pane |
| A `leopard build`-compiled executable | stderr, same as `leopard run` — the generated launcher calls the identical pipeline |

Because there's no way to recover once an error happens, the normal Leopard style is to check for
a risky condition first rather than let the error happen and try to handle it after — e.g.
`if answer = "":` before doing anything with user-entered text, or `if selected = 0:` before
indexing a listbox's current selection. `dialogs.lep` and `todo_capstone.lep` in the examples
folder both follow this pattern throughout.
