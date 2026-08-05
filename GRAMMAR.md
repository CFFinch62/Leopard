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
6. **Full menu support**: submenus, checkable items, accelerators — usable alongside any mix of controls in a window.
7. A `textedit` control is a **fully editable** text area, not a read-only scrollback.
8. Errors report as **line number + plain-English message**.
9. Modulo is **`%`**, not `mod`. `else if` is **`elseif`**, one word. String concatenation is **`&`**, not `+` — `+` is numeric-only.
10. `&` requires **explicit conversion** — no auto-stringifying numbers/booleans. Deliberate friction so beginners learn strings and numbers are different types.
11. **Turtle graphics and text areas are controls, not window modes** (Phase 13): a `graphics` control and a `textedit` control are declared and positioned like any other control, so a single `window` can host graphics, text, and ordinary controls together, including more than one of each. Turtle commands are dotted method calls on a named `graphics` control (`canvas1.go(100)`), not bare statements — no `page`/`text window`/`graphics window` special-casing survives.
12. `eq` is a **word alternative for `=` in comparison position only** — `=` still also means assignment, unchanged; `eq` never does. Added for readability, not to replace `=` (see §4).
13. **Strings support `[ ]` and `.length`, the same as lists** (Phase 14): `name[1]` reads the first character (1-based, same convention as list indexing), `name.length` is the character count. Read-only — `name[1] = "x"` is still a runtime error, since Leopard strings stay immutable; to build a new string you reassign the whole variable, same as the list "rebuild, don't remove" pattern (§3). `split(text, sep)` / `join(list, sep)` (§12) round out basic string handling — `split` turns delimited text (e.g. a `read_file()`'d line) into a list, `join` is its inverse.

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

Leopard originally forced every program to declare `window` / `text window` / `graphics window` / `no window` up front. As of Phase 13, `text window` and `graphics window` are gone — turtle graphics and fully-editable text areas are ordinary controls (`graphics`, `textedit`, §7) declared inside a plain `window`, not exclusive whole-program modes. That leaves exactly two program shapes: a `window`, or a plain script with no window header at all (**"no window" mode** — the explicit keyword is dropped as redundant).

```
window "My App", 500, 400:
    ...controls, menus, event handlers...
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

Strings support the same `[ ]`/`.length` vocabulary, read-only: `"hello"[1]` is `"h"`, `"hello".length` is `5`. Unlike lists, a string's `[ ]` can't be assigned to (`name[1] = "H"` is a runtime error) — strings stay immutable, so building a new one means reassigning the whole variable. `split(text, sep)` and `join(list, sep)` (§12) are the other half of string handling — turning delimited text into a list and back.

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
| Comparison | `=  <>  <  >  <=  >=`, and `eq` | `=` doubles as equality (BASIC-style, no separate `==`); `eq` is an alternate spelling of `=` for equality only — see below |
| Logical | `and  or  not` | English words, not `&&`/`\|\|` — matches BASIC/beginner spirit |
| Grouping | `( )` | standard precedence |

`+` is numeric-only now that `&` owns concatenation — using `+` on two strings is a runtime error that suggests `&` (a beginner writing `"a" + "b"` gets pointed at the right operator instead of silently getting `"ab"` and being confused later when `+` behaves differently on numbers-as-strings).

**`eq` — a word alternative for `=`, comparison-only.** `=` still does double duty (assignment
*and* equality, per status #9) and that isn't changing — `eq` was added alongside it, not instead
of it, for programs where writing out `eq` makes an equality check easier to spot at a glance than
`=` does, especially next to an actual assignment on a nearby line:

```
found = false             # assignment — "="
if fruit eq "apple":      # comparison — "eq", reads unambiguously as a check, not a store
    found = true
```

`a eq b` and `a = b` produce the exact same result — `eq` is parsed into the identical AST node as
`=` in comparison position, so there's no behavioral difference, only a readability one. It's
purely optional: existing code using `=` for comparison needs no changes, and there's no equivalent
word form for `<>`/`<`/`>`/`<=`/`>=` (only equality gets one, since equality is the one case where
`=` is also a completely different operator — assignment — depending on where it appears).

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
| *(new, Phase 13 — was `graphics window`)* | `graphics as name at x, y, w, h` — a turtle-graphics canvas, see §10 |

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
| `.selected` | listbox, combobox | 1-based index of the selected item, `0` if none is selected — same 1-based convention as list literals |
| `.visible`, `.enabled` | any control | *(new — original had neither)* |

`.font`'s value is a font-family name (`label.font = "Arial"`), a plain string, not a struct or a "family, size" pair.

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

Full support now — arbitrary submenu depth, checkable items, same `&`-accelerator convention (Qt honors it natively). Unlike the original (menu bar only made sense in its one `window` mode), a `menu` block is legal alongside **any** mix of controls in a `window` — so a program built around a `graphics` control can have a "File > Save Drawing" menu, a program built around a `textedit` control can have a full "File/Edit" menu bar, and so on:

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
| `on change` | checkbox, radiobutton, combobox, checkitem, textedit | `checkbox onclick`, `radiobutton onclick`, `combobox onclick` |
| `on select` | listbox, combobox | `listbox onclick` (double-click), `combobox onclick` |
| `on close` | window | `trapclose` |

---

## 10. Turtle graphics (a `graphics` control)

Leopard's turtle vocabulary was already clean — as of Phase 13 it's reached as dotted method calls on a named `graphics` control (§7) instead of bare statements inside an exclusive `graphics window`. This means a window can hold more than one `graphics` control at once, each with its own independent turtle, and can mix graphics with ordinary controls and menus:

```
window "Turtle Demo", 640, 480:
    graphics as canvas1 at 0, 0, 640, 480
    canvas1.pen("red")
    canvas1.size(3)
    canvas1.down()
    canvas1.go(100)
    canvas1.turn(90)
    canvas1.go(100)
    canvas1.up()
    canvas1.goto(300, 300)
    canvas1.circlefilled(40)
```

`up down home go goto place turn north fill pen size font text backcolor box boxfilled circle circlefilled ellipse ellipsefilled drawbmp` — every command from the original carried over unchanged in name and meaning, just called as `canvasName.command(args)` rather than a bare `command args` statement.

**Semantics** (`canvas1` below stands for whatever name you declared the `graphics` control under):

| Command | Meaning |
|---|---|
| `.up()` / `.down()` | raise/lower the pen — `.go()`/`.goto()` only draw a line while the pen is down |
| `.go(n)` | move `n` pixels in the current heading, drawing a line if the pen is down |
| `.goto(x, y)` | move to absolute coordinates, drawing a line if the pen is down |
| `.place(x, y)` | jump to absolute coordinates without ever drawing, regardless of pen state |
| `.turn(n)` | increase heading by `n` degrees, clockwise |
| `.north()` | reset heading to `0` (facing north/`-y`) without moving |
| `.home()` | reset both position (canvas center) and heading to `0` |
| `.pen("color")` | set the line/pen color (invalid color names raise a runtime error) |
| `.fill("color")` | set the fill color used by `.boxfilled()`/`.circlefilled()`/`.ellipsefilled()` |
| `.backcolor("color")` | set the canvas background color |
| `.size(n)` | set pen width in pixels |
| `.font("family")` / `.font("family", size)` | set the font used by `.text()`; family alone, or family + point size |
| `.text("string")` | draw a string at the current position |
| `.box(w, h)` / `.boxfilled(w, h)` | draw a rectangle `w` by `h` pixels, current position as the top-left corner |
| `.circle(r)` / `.circlefilled(r)` | draw a circle of radius `r`, centered at the current position |
| `.ellipse(w, h)` / `.ellipsefilled(w, h)` | draw an ellipse `w` by `h` pixels, centered at the current position |
| `.drawbmp("file.bmp", x, y)` | draw an image at absolute coordinates `x, y` |

Heading `0` is north; turning is clockwise (`.turn(90)` faces east). Default turtle state for a newly-declared `graphics` control: pen up, position at canvas center, heading `0` (north), black pen and fill, pen size `1`, white background — independent per control, so two `graphics` controls in the same window never share state.

---

## 11. Text areas (a `textedit` control)

Original's `text window` type was a read-only scrollback the program could `print text` into or load a file with `open file`. As of Phase 13 there's no separate window mode for this at all — a fully editable text area is just an ordinary `textedit` control (§7), reusing the property/event vocabulary from Sections 7 and 9 instead of inventing new keywords:

```
window "Notes", 600, 400:

    textedit as page at 0, 20, 600, 380

    page.text = "Start typing..."

    on change page:
        wordCountLabel.text = "Editing..."

    on close:
        write_file("notes.txt", page.text)
```

`page` here is just a name the program picked — not a reserved word. Nothing stops you from declaring more than one `textedit` control in the same window (`notes`, `scratch`, whatever names you like), each with independent contents; there's no longer a single implicit text area a window is limited to. The old `print text` / `open file` actions become `page.text = page.text & "..."` and `page.text = read_file(path)` — no special-cased keywords required.

---

## 12. Builtin actions

The original's ~40 fixed onclick-action keywords become ordinary builtin functions/statements, callable anywhere (not just inside a click handler) — another side effect of making handlers real code.

| Old keyword | New builtin |
|---|---|
| *(new — required by `&`'s no-coercion rule)* | `str(value)` → string, `num(text)` → number |
| *(new, Phase 14)* | `split(text, sep)` → list of strings, `join(list, sep)` → string |
| *(new — a bare script's only console output)* | `print value` — writes a number, string, or `true`/`false` to the console, followed by a newline |
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

`window`, `as`, `at`, `true`, `false`, `and`, `or`, `not`, `eq`, `if`, `elseif`, `else`, `while`, `for`, `to`, `step`, `break`, `continue`, `function`, `return`, `menu`, `item`, `checkitem`, `submenu`, `separator`, `on`, `click`, `change`, `select`, `close`

Plus the control-declaration keywords from Section 7 (`textbox`, `textedit`, `label`, `button`, `bmpbutton`, `listbox`, `combobox`, `radiobutton`, `checkbox`, `groupbox`, `graphics`), every turtle-graphics command from Section 10 (`up`, `down`, `home`, `go`, `goto`, `place`, `turn`, `north`, `fill`, `pen`, `size`, `font`, `text`, `backcolor`, `box`, `boxfilled`, `circle`, `circlefilled`, `ellipse`, `ellipsefilled`, `drawbmp`), and every builtin from Section 12.

`text window`, `graphics window`, and `page` are gone from this list (Phase 13): there's only one window kind left, and text areas are just ordinary `textedit` controls with whatever name you choose — `page` is not special anymore. The turtle-graphics command words stay reserved (still not usable as a variable/function/control name), but their only remaining role is as a method name after a dot on a `graphics` control (`canvas1.go(100)`) — see Section 10; they're never valid as bare, receiver-less statements now.

`window` is also reserved as an implicit identifier, not just a declaration keyword: inside a `window` block, `window` refers to the current window itself, so `window.title = "..."` works as a property access.

---

## 15. Open questions for the next pass

Everything from v0.1 and v0.2 is resolved. Five gaps surfaced while implementing and exercising
the language (see IMPLEMENTATION_PLAN.md for the phase each was found in) — all five are now
resolved:

1. ~~§14's reserved-word list omitted the §7 control-declaration keywords.~~ **Resolved:** §14 now
   lists `textbox`, `textedit`, `label`, `button`, `bmpbutton`, `listbox`, `combobox`,
   `radiobutton`, `checkbox`, `groupbox` explicitly.
2. ~~`print` was used in §5's `for` loop example but never defined as a keyword or builtin.~~
   **Resolved:** there is no `print`/console-output builtin, deliberately — §5's example now uses
   plain assignment instead, and notes that `write_file()` (§12) is a bare script's way to
   surface output.
3. ~~`window` doubling as an identifier, `.selected`'s shape, and `.font`'s value shape were all
   unstated.~~ **Resolved:** §14 now says `window` is reserved as an implicit identifier for the
   current window in all three window kinds (same pattern as `page`, §11); §7's table now states
   `.selected` is a 1-based index (`0` = none selected) and `.font` is a plain font-family string.
4. ~~§10's turtle commands had no documented pixel semantics.~~ **Resolved:** §10 now spells out
   heading convention, what each drawing command measures, and default turtle state directly,
   rather than pointing at `leopard.bas`'s undocumented pass-through to Liberty BASIC.
5. ~~List index assignment (`list[i] = value`) fell through to a confusing "needs a GUI control"
   error.~~ **Resolved:** `Interpreter._exec_PropertyAssignment` now handles an `Index` target by
   mutating the list in place (same bounds-checking as reads) — `x = [1, 2, 3]` then `x[2] = 99`
   works.

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
  or calling a GUI builtin (§12) from a program with no window. Whatever ran before the error
  already took effect (a file already written, a window already shown); nothing after it does.

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
