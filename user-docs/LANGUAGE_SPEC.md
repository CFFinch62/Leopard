<!-- title: The Leopard Language Specification -->

# The Leopard Language — Complete Specification

**Version covered:** 0.4.0 (matches `src/leopard_lang`, verified against source — not just
`../dev-docs/GRAMMAR.md`/`LANGUAGE_GUIDE.md` — as of 2026-08-06).

This is the single reference for *everything* Leopard can do: every operator, every statement
form, every control/property/event, and — the point of this document — every built-in function,
grouped by category, in one place. `../dev-docs/GRAMMAR.md` is the incremental design/decision log
(why things are the way they are); `LANGUAGE_GUIDE.md` is the tutorial; this document is the flat,
complete catalog. Where this spec and those two disagree, this one wins — it was built by reading
the interpreter, lexer, parser, and GUI runtime source directly, not by trusting prior docs.

> **One confirmed doc/implementation gap, found while writing this spec:** `beep()` and
> `set_cursor(style)` are reserved words and are listed in `../dev-docs/GRAMMAR.md` §12, but neither has any
> implementation anywhere in the codebase (`gui/dialogs.py`, `gui/sound.py`, `gui/app_host.py`).
> Calling either always raises `'beep' needs a window (not available yet)` / `'set_cursor' needs a
> window (not available yet)` — even from inside a window program. They're listed below, marked
> **not implemented**, for completeness. Every other builtin in this document was checked directly
> against its implementation and confirmed working.

---

## Table of contents

1. [Lexical basics](#1-lexical-basics)
2. [Program shape](#2-program-shape)
3. [Types & variables](#3-types--variables)
4. [Operators & expressions](#4-operators--expressions)
5. [Control flow](#5-control-flow)
6. [Functions](#6-functions)
7. [Lists](#7-lists)
8. [Strings](#8-strings)
9. [Built-in functions — complete catalog](#9-built-in-functions--complete-catalog)
10. [Windows & controls](#10-windows--controls)
11. [Menus](#11-menus)
12. [Events](#12-events)
13. [Turtle graphics (`graphics` control)](#13-turtle-graphics-graphics-control)
14. [Error handling](#14-error-handling)
15. [Reserved words](#15-reserved-words)
16. [Command-line interface](#16-command-line-interface)

---

## 1. Lexical basics

| Thing | Rule |
|---|---|
| Comments | `# to end of line` |
| Strings | double-quoted only: `"hello"` |
| Numbers | `42`, `3.14` — one numeric type, int/float handled transparently |
| Booleans | `true`, `false` (lowercase) |
| Identifiers | letters, digits, `_`; case-sensitive |
| Blocks | a line ending in `:` opens a block; the next line's indentation defines it; a dedent closes it (Python-style) |
| Statement separator | newline — no `;` |

No line numbers. This is a real tokenizer/recursive-descent parser.

---

## 2. Program shape

Exactly two shapes exist:

```
window "My App", 500, 400:
    ...controls, menus, event handlers, and ordinary code...
```

or a plain script with **no window header at all** ("no window" mode — bare script, console/file
I/O only, no GUI builtins available). A program either has a `window` block or it doesn't; there's
no other variant (no `text window`/`graphics window` modes — those were folded into ordinary
`textedit`/`graphics` controls).

`title, width, height` are the window's header arguments, in that order.

---

## 3. Types & variables

Four value types. A variable is created on first assignment — no declaration step.

| Kind | Examples | Notes |
|---|---|---|
| number | `42`, `3.14` | one numeric type; int/float handled transparently |
| string | `"hello"` | always double-quoted |
| boolean | `true`, `false` | a genuinely separate type from numbers |
| list | `["apple", "banana", "cherry"]` | **1-based** — `list[1]` is the first element |

```
score = 0
name = "Chuck"
found = false
fruits = ["apple", "banana", "cherry"]
first = fruits[1]        # "apple" — 1-based indexing throughout
```

### Scoping

**Only a `function` call gets a private scope.** Everywhere else — the top level of a program, a
window's own setup code, and *every* `on ...:` event handler in that window — shares exactly one
scope. A variable assigned in one event handler stays assigned and is visible in every other event
handler in the same window. This is the reverse of what a `function` call does: an assignment made
inside a function call never escapes that call, even if a same-named variable already exists
outside it.

```
window "Shared state", 300, 150:
    textbox as nameBox at 10, 10, 200, 24
    button "Save" as saveButton at 10, 44, 100, 24
    button "Greet" as greetButton at 120, 44, 100, 24
    label "" as resultLabel at 10, 78, 260, 24

    saved_name = ""

    on click saveButton:
        saved_name = nameBox.text

    on click greetButton:
        resultLabel.text = "Hello, " & saved_name & "!"   # sees saveButton's handler's write
```

---

## 4. Operators & expressions

| Category | Operators | Notes |
|---|---|---|
| Arithmetic | `+  -  *  /  %  ^` | `%` = modulo, `^` = power |
| String concatenation | `&` | dedicated operator; **both operands must already be strings** |
| Comparison | `=  <>  <  >  <=  >=`, and word-form `eq` | `=` doubles as assignment *and* equality (context decides); `eq` is a comparison-only alternate spelling of `=`, identical behavior, purely for readability |
| Logical | `and  or  not` | English words, not `&&`/`\|\|` |
| Grouping | `( )` | standard precedence override |
| Indexing | `expr[index]` | 1-based, works on lists and strings |
| Property/method access | `expr.name`, `expr.name(args)` | dotted access on GUI controls, `.length`, `.add()` |

**`+` is numeric-only.** `"a" + "b"` is a runtime error suggesting `&`.

**`&` requires both sides to already be strings** — no auto-coercion in either direction.
`"Score: " & 5` is a runtime error pointing at `str()`.

```
"Score: " & str(score)      # correct
"Score: " & score           # runtime error — score is a number, use str(score)
```

**`eq`** parses to the exact same AST node as `=` in comparison position — no behavioral
difference, only readability. There is no word-form for `<>`/`<`/`>`/`<=`/`>=`.

### Precedence (loosest to tightest)

```
or  >  and  >  not  >  comparison (= <> < > <= >= eq)  >  concat (&)
  >  additive (+ -)  >  multiplicative (* / %)  >  power (^)
  >  unary (-)  >  postfix (. [ ] ( ))  >  primary
```

### Bare "command" call syntax

Any identifier — a builtin, a user function, or a zero-arg turtle-style command — can be called as
a statement two ways: with parentheses (`notice("hi")`, an ordinary call expression usable anywhere
including inside larger expressions), or, at **statement position only**, with no parentheses at
all — the identifier followed directly by its arguments, comma-separated:

```
notice "hi"                 # same as notice("hi")
print "Score:", score       # bare-command form also accepts multiple comma-separated args
up                           # a bare identifier alone at statement position is a zero-arg call
```

This only applies where a statement begins with a bare identifier — `x + 1` is still addition, not
`x() + 1`, inside a larger expression.

---

## 5. Control flow

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

for fruit in fruits:
    print fruit

do:
    print "at least once"
until score > 10

switch grade:
    case "A":
        notice "Excellent!"
    case "B":
        notice "Good."
    default:
        notice "Keep working."

break
continue
```

`for var = start to end [step n]`: `step` defaults to `1` if omitted, can be negative to count
down. `break` exits the nearest loop; `continue` skips to the next iteration.

**`for var in list:`** (for-each) iterates a list's elements directly, assigning each to `var` in
turn — no manual index variable needed. It only accepts a list (`for c in "hello":` is a runtime
error — strings aren't iterable this way). The loop iterates a snapshot taken before the first
pass: appending to the same list from inside the body (`list.add(...)`) does not extend or affect
the iteration already in progress.

**`do: ... until condition`** (post-test loop) always runs its body at least once, then repeats
until `condition` becomes `true` — the inverse framing of `while`, which checks first and may never
run the body at all. `break`/`continue` work inside a `do` block exactly as they do in `while`/`for`.

**`switch value: case v1: ... case v2: ... default: ...`** (multi-way branch) evaluates `value`
once, then runs the body of the first `case` whose value equals it (same equality as `=`) — no
fallthrough to the next case. `default` (optional, at most one) runs if no `case` matches. A
`switch` needs at least one `case`. A `switch` is not itself a loop: `break`/`continue` inside a
`case`/`default` body pass through to whatever loop encloses the `switch`, and are a runtime error
if nothing does.

---

## 6. Functions

One keyword covers both "function" and "procedure" — a `function` that never `return`s is just a
callable block:

```
function greet(who):
    return "Hello, " & who

function log_message(message):
    outputBox.text = outputBox.text & message & "\n"
```

Calling a function that falls off the end without a `return` yields no usable value. Every call
site — `greet("Chuck")` — gets its own private scope (see [§3](#3-types--variables)).

---

## 7. Lists

- **1-based**: `list[1]` is the first element, `list[list.length]` is the last.
- `.length` — element count (read-only property, works like `.length` on GUI list-backed
  properties too).
- `.add(value)` — appends one item in place, returns nothing. Works on any plain list, including a
  control's live `.items` list (appending there also updates the widget — see
  [§10](#10-windows--controls)).
- `list[i] = value` — in-place index assignment (mutates the list; bounds-checked the same as
  reads).
- Indexing out of range, or with a non-whole-number index, is a runtime error.
- `.add()` remains the only *method*, and the only thing that mutates a list in place — "rebuild,
  don't remove" is still the idiom for `.add()` itself. But there is now a set of list
  **functions** (§9.4) that build and return a *new* list rather than mutating: `sort(list)`,
  `reverse(list)`, `remove_at(list, index)`, and `shuffle(list)` all leave their argument
  untouched and hand back a fresh list — consistent with "rebuild, don't remove," since each one
  literally rebuilds. `contains(list, value)`, `index_of(list, value)`, `sum(list)`,
  `min(list)`, `max(list)`, and `choice(list)` inspect a list without changing it at all.

```
fruits = ["apple", "banana", "cherry"]
first = fruits[1]              # "apple"
last = fruits[fruits.length]   # "cherry"
fruits.add("date")             # appends "date", in place
fruits[1] = "avocado"          # in-place replace

scores = [40, 90, 10, 70]
ranked = sort(scores)          # [10, 40, 70, 90] — a new list; scores is untouched
total = sum(scores)            # 210
best = max(scores)             # 90
without_first = remove_at(scores, 1)   # [90, 10, 70] — a new list
pick = choice(scores)          # one random element of scores
```

---

## 8. Strings

Strings support the same `[ ]`/`.length` vocabulary as lists, **read-only** — a string's `[ ]`
can't be assigned to (`name[1] = "H"` is a runtime error); strings are immutable, so building a new
one means reassigning the whole variable.

```
name = "Chuck"
first_letter = name[1]      # "C"
name_length = name.length   # 5
```

Beyond indexing and `.length`, the string-manipulation builtins are `upper`, `lower`, `trim`,
`contains`, `index_of`, `replace`, `starts_with`, `ends_with`, `substring`, `left`, `right`,
`reverse`, and `chr` — see [§9.4](#94-string--list-helpers) for the complete signatures. `contains`,
`index_of`, and `reverse` are shared vocabulary with lists (§7): call them with a string and they
work on characters, with a list and they work on elements.

```
name = "  Chuck  "
clean = trim(name)                        # "Chuck"
loud = upper(clean)                       # "CHUCK"
first_three = left(clean, 3)              # "Chu"
greeting = replace("Hi, NAME!", "NAME", clean)   # "Hi, Chuck!"
```

`split`/`join` remain the tools for delimited text specifically:

```
fields = split("Chuck,32,wizard", ",")   # ["Chuck", "32", "wizard"]
row = join(fields, " | ")                # "Chuck | 32 | wizard"
```

---

## 9. Built-in functions — complete catalog

Every entry below was checked directly against the Python source that implements it. "Bare
script OK" means the function works with no `window` declared; "**GUI only**" means calling it
from a bare script (no window) raises `'name' needs a window (not available yet)`.

### 9.1 Type conversion

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `str` | `str(value)` | string | number → string (`3.0` → `"3"`), boolean → `"true"`/`"false"`. Errors on anything else (e.g. a list). |
| `num` | `num(text)` | number | string → number; tries int first, then float. Errors if `text` isn't a valid number. |
| `is_number` / `is_string` / `is_list` | `is_number(value)` etc. | boolean | type checks — never error, work on any value |
| `type_of` | `type_of(value)` | string | `"number"`, `"string"`, `"boolean"`, `"list"`, or `"nothing"` (a function call that fell off the end without a `return`) |

With no `try`/`catch` (§14), these are the only defensive tool a program has against a type error —
check first, since there's no catching the error after the fact:

```
function safe_num(value):
    if is_number(value):
        return value
    if is_string(value):
        return num(value)
    return 0
```

### 9.2 Math

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `abs` | `abs(n)` | number | absolute value |
| `sqrt` | `sqrt(n)` | number | square root; errors if `n` is negative |
| `round` | `round(n)` / `round(n, digits)` | number | rounds to the nearest whole number, or to `digits` decimal places; uses Python's round-half-to-even rule (`round(2.5)` is `2`, not `3`) |
| `floor` | `floor(n)` | number | rounds down |
| `ceil` | `ceil(n)` | number | rounds up |
| `min` | `min(a, b)` or `min(list)` | number | smaller of two numbers, or the smallest in a list; errors on an empty list |
| `max` | `max(a, b)` or `max(list)` | number | larger of two numbers, or the largest in a list; errors on an empty list |
| `sin` / `cos` / `tan` | `sin(n)` etc. | number | trig functions; **`n` is in degrees**, matching the turtle graphics control's `turn()`/heading convention — not radians |
| `log` | `log(n)` | number | natural log; errors if `n` isn't greater than `0` |
| `exp` | `exp(n)` | number | `e^n` |
| `pi` | `pi` | number | the constant `3.14159...` — a bare identifier, **not** a function call (no `pi()`) |

```
d = sqrt((x2 - x1) ^ 2 + (y2 - y1) ^ 2)   # distance formula
area = pi * r ^ 2
biggest = max(scores)                     # scores is a list
```

### 9.3 Randomness

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `random` | `random()` | number | a float, `0 <= n < 1` |
| `random_int` | `random_int(min, max)` | number | a whole number, `min <= n <= max` inclusive; both arguments must be whole numbers, and `min` must not exceed `max` |

```
roll = random_int(1, 6)              # a six-sided die
coinflip = random() < 0.5
```

### 9.4 String & list helpers

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `split` | `split(text, sep)` | list of strings | `sep` must be a non-empty string |
| `join` | `join(list, sep)` | string | every item in `list` must already be a string — `str()` numbers first |
| `ascii` | `ascii(char)` | number | character code of a single-character string; errors if `char` isn't exactly one character |
| `chr` | `chr(code)` | string | the inverse of `ascii` — the single character for a character code |
| `upper` / `lower` | `upper(s)` / `lower(s)` | string | case conversion |
| `trim` | `trim(s)` | string | strips leading/trailing whitespace |
| `replace` | `replace(s, old, new)` | string | replaces every occurrence of `old` with `new`; `old` must be non-empty |
| `starts_with` / `ends_with` | `starts_with(s, prefix)` / `ends_with(s, suffix)` | boolean | prefix/suffix test |
| `substring` | `substring(s, start, end)` | string | characters from `start` to `end`, **inclusive, both 1-based** — errors if the range is out of bounds |
| `left` / `right` | `left(s, n)` / `right(s, n)` | string | first/last `n` characters; `n` larger than the string's length just returns the whole string |
| `contains` | `contains(collection, value)` | boolean | **shared with lists (§7)** — substring test on a string, membership test on a list |
| `index_of` | `index_of(collection, value)` | number | **shared with lists** — 1-based position of `value`, or `0` if not found (`0` is the same "no match" sentinel a listbox's `.selected` uses) |
| `reverse` | `reverse(collection)` | string or list | **shared with lists** — reverses a string's characters or a list's elements; returns a new value, doesn't mutate a list in place |
| `sort` | `sort(list)` | list | ascending order; the list must be all numbers or all strings — returns a new list, doesn't mutate the argument |
| `remove_at` | `remove_at(list, index)` | list | a new list with the item at 1-based `index` removed; errors if `index` is out of range |
| `sum` | `sum(list)` | number | total of a numeric list; `0` for an empty list |
| `shuffle` | `shuffle(list)` | list | a new list with elements in random order; doesn't mutate the argument |
| `choice` | `choice(list)` | any | one random element; errors on an empty list |

`min`/`max` also work as list aggregates (§9.2): `min(list)` / `max(list)`.

(`.length`, `[ ]`, and `.add()` are covered as list/string vocabulary in [§7](#7-lists)/[§8](#8-strings), not standalone functions.)

### 9.5 Console I/O

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `print` | `print(value)` | nothing | writes a number, string, or `true`/`false` to stdout, with a trailing newline. Errors on lists. |
| `input` | `input()` / `input(prompt)` | string | reads one line from stdin (trailing newline stripped); if given, `prompt` is written to stdout first with no trailing newline. Errors if there's no more input to read (stdin at EOF). Leopard's `try`/`catch`-free way of reading a line back — the bare-script counterpart to `ask()` (§9.9), which needs a window. |
| `get_env` | `get_env(name)` | string | the OS environment variable `name`, or `""` if it isn't set — same "empty string means absent" convention as a cancelled `ask()`/dialog |
| `command_line_args` | `command_line_args()` | list of strings | extra arguments passed after the script's own filename on `leopard run script.lep arg1 arg2` (§16), or after a `leopard build`-compiled executable's own name; `[]` if none were given. Only meaningful for a bare (no-window) program — a windowed program's `command_line_args()` is always `[]`. |

### 9.6 Date & time

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `date` | `date()` | string | today's date, ISO 8601 (`"2026-08-06"`) |
| `time` | `time()` | string | current local time, `HH:MM:SS` |

### 9.7 File I/O

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `write_file` | `write_file(path, text)` | nothing | overwrites `path` with `text` (UTF-8) |
| `append_file` | `append_file(path, text)` | nothing | appends `text` to `path` (UTF-8), creating it if needed |
| `read_file` | `read_file(path)` | string | errors if `path` doesn't exist |
| `delete_file` | `delete_file(path)` | nothing | errors if `path` doesn't exist |
| `make_dir` | `make_dir(path)` | nothing | creates `path`, including parents; no error if it already exists |
| `remove_dir` | `remove_dir(path)` | nothing | errors if `path` doesn't exist or isn't empty |
| `file_exists` | `file_exists(path)` | boolean | true only for an existing regular file |
| `download_file` | `download_file(url, path)` | nothing | fetches `url` and saves it to `path` |

### 9.8 System / OS

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `run_program` | `run_program(command)` | number | runs `command` via the shell, returns its exit code |
| `open_url` | `open_url(url)` | nothing | opens `url` in the system default browser |
| `open_email` | `open_email(address)` | nothing | opens the system default mail client with a `mailto:` link |

### 9.9 Dialogs — **GUI only**

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `notice` | `notice(message)` | nothing | modal message box, OK only |
| `confirm` | `confirm(message)` | boolean | modal Yes/No dialog; `true` for Yes |
| `ask` | `ask(prompt)` | string | modal text-entry dialog; `""` if cancelled |
| `open_file_dialog` | `open_file_dialog()` | string | native "open file" picker; `""` if cancelled |
| `save_file_dialog` | `save_file_dialog()` | string | native "save file" picker; `""` if cancelled |
| `color_dialog` | `color_dialog()` | string | native color picker → hex string (`"#ff0000"`); `""` if cancelled |
| `font_dialog` | `font_dialog()` | string | native font picker → font family name; `""` if cancelled |

### 9.10 Window control — **GUI only**

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `close_window` | `close_window()` | nothing | closes the program's one window |
| `maximize_window` | `maximize_window()` | nothing | |
| `minimize_window` | `minimize_window()` | nothing | |

(Changing the title is a property, not a call: `window.title = "New Title"` — see
[§10](#10-windows--controls).)

### 9.11 Sound — **GUI only**

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `play_sound` | `play_sound(path)` | nothing | plays a WAV file once, via `QSoundEffect`. Errors if `path` doesn't exist. |
| `stop_sound` | `stop_sound()` | nothing | |
| `play_music` | `play_music(path)` | nothing | plays MP3/MIDI, via Qt Multimedia; can be paused/resumed. Errors if `path` doesn't exist. |
| `stop_music` | `stop_music()` | nothing | |
| `pause_music` | `pause_music()` | nothing | |

### 9.12 Reserved but **not implemented**

| Word | Documented signature (per `../dev-docs/GRAMMAR.md`) | Actual behavior |
|---|---|---|
| `beep` | `beep()` | Always raises `'beep' needs a window (not available yet)`, even inside a window program — no code anywhere implements it. |
| `set_cursor` | `set_cursor(style)` | Same — always raises `'set_cursor' needs a window (not available yet)`. |

Both words are reserved (can't be used as a variable/function/control name) and are valid in
expression/statement position syntactically, but calling either is always a runtime error today.

---

## 10. Windows & controls

**Declaration** — `as <name>` names the control, `at x, y, w, h` positions it (measured from the
workspace below the menu bar, if any):

| Keyword | Creates | Takes a caption? |
|---|---|---|
| `textbox` | single-line text field | no |
| `textedit` | multi-line, fully-editable text area | no |
| `label` | static text label | yes |
| `button` | clickable button | yes |
| `bmpbutton` | button showing an image file | yes (an image path) |
| `listbox` | scrollable single-select list | no |
| `combobox` | dropdown | no |
| `radiobutton` | radio button | yes |
| `checkbox` | checkbox | yes |
| `groupbox` | labeled grouping box | yes |
| `graphics` | turtle-graphics canvas (see [§13](#13-turtle-graphics-graphics-control)) | no |

```
textbox as nameBox at 10, 10, 200, 24
button "Save" as btnSave at 10, 44, 100, 24
```

**Properties** — `control.property = value` to set, `control.property` to read:

| Property | Applies to | Type | Read-only? |
|---|---|---|---|
| `.text` | textbox, textedit, label, button | string | no |
| `.color` | textbox, textedit, listbox, combobox, label | string (color name/hex) | no |
| `.background` | any control, or `window` | string (color name/hex) | no |
| `.font` | any control, or `window` | string (font family name — not a "family, size" pair) | no |
| `.checked` | checkbox, radiobutton, checkitem | boolean | no |
| `.items` | listbox, combobox | list of strings (supports `.add()`, `.length`, `[i]`) | no |
| `.selected` | listbox, combobox | number — 1-based index of selection, `0` if none | no |
| `.visible` | any control | boolean | no |
| `.enabled` | any control | boolean | no |
| `.title` | `window` | string | no |
| `.mouse_x` / `.mouse_y` | `graphics` control | number | **yes** — only real mouse movement updates these |

```
nameBox.text = "placeholder"
outputArea.color = "darkblue"
fruitList.items = ["Apple", "Banana", "Cherry"]
fruitList.items.add("Date")
first = fruitList.items[1]
window.title = "Renamed"
```

Setting a wrong-typed value (a number into a `.text` slot, a string into `.checked`, etc.) is a
runtime error. Accessing an unrecognized property name on a control is also a runtime error, as is
accessing any `.property` on a plain value with no window declared.

---

## 11. Menus

Arbitrary submenu depth, checkable items, `&`-accelerator convention. A `menu` block claims its own
horizontal strip at the top of the window regardless of where it's written in the window body —
every other control's `at x, y, w, h` is measured from the workspace below it.

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

| Keyword | Meaning |
|---|---|
| `menu "&Label" as name:` | top-level menu-bar entry |
| `item "&Label" as name` | clickable entry — fires `on click name` |
| `checkitem "&Label" as name` | toggleable entry with `.checked` — fires `on change name` |
| `submenu "&Label" as name:` | nested menu, any depth |
| `separator` | divider line |

---

## 12. Events

`on <event> <control>:` opens a block of ordinary statements that runs when the event fires.

| Event | Applies to |
|---|---|
| `on click` | button, bmpbutton, menu `item`, menu `checkitem` (fires on toggle) |
| `on change` | checkbox, radiobutton, combobox, checkitem, textedit (fires on text change) |
| `on select` | listbox, combobox (selection changed) |
| `on close` | the window (no control name — `on close:`) |
| `on mousemove` | a `graphics` control — fires on every mouse move over it; read position via `.mouse_x`/`.mouse_y`, not as a handler parameter |

All event handlers in a window, plus the window's own setup code, share one scope — see
[§3](#3-types--variables).

---

## 13. Turtle graphics (`graphics` control)

A `graphics` control is a named canvas with its own independent turtle (position, heading, pen
state). A window can hold more than one, each fully independent. Commands are dotted method calls:

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

| Method | Meaning |
|---|---|
| `.up()` / `.down()` | raise/lower the pen — `.go()`/`.goto()` only draw while it's down |
| `.go(n)` | move `n` pixels in the current heading, drawing if the pen is down |
| `.goto(x, y)` | move to absolute coordinates, drawing if the pen is down |
| `.place(x, y)` | jump to absolute coordinates without ever drawing, regardless of pen state |
| `.turn(n)` | increase heading by `n` degrees, clockwise |
| `.north()` | reset heading to `0` (north) without moving |
| `.home()` | reset both position (canvas center) and heading to `0` |
| `.pen("color")` | line/pen color |
| `.fill("color")` | fill color used by `...filled` shapes |
| `.backcolor("color")` | canvas background color |
| `.size(n)` | pen width in pixels |
| `.font("family")` / `.font("family", size)` | font used by `.text()` |
| `.text("string")` | draw a string at the current position |
| `.box(w, h)` / `.boxfilled(w, h)` | rectangle `w`×`h`, current position as top-left corner |
| `.circle(r)` / `.circlefilled(r)` | circle of radius `r`, centered on the current position |
| `.ellipse(w, h)` / `.ellipsefilled(w, h)` | ellipse `w`×`h`, centered on the current position |
| `.polygon(sides, r)` / `.polygonfilled(sides, r)` | regular polygon, `sides` ≥ 3, each corner `r` pixels from the current position (center); first corner sits in the current heading's direction |
| `.drawbmp("file.bmp", x, y)` | draw an image at absolute coordinates |

Read-only, not a method — `.mouse_x`, `.mouse_y` (§10, §12).

Heading `0` is north; turning is clockwise. Default state for a newly-declared `graphics` control:
pen up, position at canvas center, heading `0`, black pen and fill, pen size `1`, white background
— independent per control.

`polygon`/`polygonfilled` are the one command beyond a 1:1 port of the language's BASIC-era turtle
vocabulary; every other command here is a direct carry-over in name and meaning.

---

## 14. Error handling

**There is no `try`/`catch`/`on error` construct, and no way to write one.** Every error stops the
program immediately at the exact statement that caused it — nothing after it runs, and whatever ran
before it already took effect (a file already written, a window already shown).

Two categories, one message format: `Line N: message`.

- **Syntax errors** — caught while parsing, before any statement runs. E.g. `Line 12: expected ':'
  after 'if' condition`.
- **Runtime errors** — happen partway through an already-running program: `+` between two strings,
  `&` with a non-string operand, an out-of-range or non-whole-number list/string index, `num()` on
  invalid text, calling something undefined, calling a GUI-only builtin with no window declared,
  assigning the wrong type to a control property, etc.

| Running via | Message goes to |
|---|---|
| `leopard run script.lep` | stderr; process exits non-zero |
| Leopard IDE's Run button | the terminal/console pane |
| a `leopard build`-compiled executable | stderr, same pipeline as `leopard run` |

Because nothing can be caught, idiomatic Leopard checks a risky condition *before* acting on it
(`if answer = "":` before using typed-in text; `if selected = 0:` before indexing a listbox
selection; `is_number(value)`/`is_string(value)` (§9.1) before a type-sensitive operation) rather
than letting the error happen.

---

## 15. Reserved words

Every one of these is off-limits as a variable, function, or control name.

**Core keywords:** `window`, `as`, `at`, `true`, `false`, `and`, `or`, `not`, `eq`, `if`, `elseif`,
`else`, `while`, `for`, `to`, `step`, `in`, `do`, `until`, `switch`, `case`, `default`, `break`,
`continue`, `function`, `return`, `menu`, `item`, `checkitem`, `submenu`, `separator`, `on`,
`click`, `change`, `select`, `close`, `mousemove`, `text`

**Control-declaration keywords:** `textbox`, `textedit`, `label`, `button`, `bmpbutton`, `listbox`,
`combobox`, `radiobutton`, `checkbox`, `groupbox`, `graphics`

**Turtle-graphics command words** (only meaningful after a dot on a `graphics` control — never
valid bare): `up`, `down`, `home`, `go`, `goto`, `place`, `turn`, `north`, `fill`, `pen`, `size`,
`font`, `backcolor`, `box`, `boxfilled`, `circle`, `circlefilled`, `ellipse`, `ellipsefilled`,
`polygon`, `polygonfilled`, `drawbmp`

**Every builtin from [§9](#9-built-in-functions--complete-catalog):** `str`, `num`, `split`,
`join`, `print`, `notice`, `confirm`, `ask`, `beep`, `date`, `time`, `write_file`, `append_file`,
`read_file`, `delete_file`, `make_dir`, `remove_dir`, `file_exists`, `open_file_dialog`,
`save_file_dialog`, `color_dialog`, `font_dialog`, `open_url`, `open_email`, `run_program`,
`ascii`, `set_cursor`, `close_window`, `maximize_window`, `minimize_window`, `play_sound`,
`stop_sound`, `play_music`, `stop_music`, `pause_music`, `download_file`, `abs`, `sqrt`, `round`,
`floor`, `ceil`, `min`, `max`, `sin`, `cos`, `tan`, `log`, `exp`, `pi`, `random`, `random_int`,
`chr`, `upper`, `lower`, `trim`, `contains`, `index_of`, `reverse`, `replace`, `starts_with`,
`ends_with`, `substring`, `left`, `right`, `sort`, `remove_at`, `sum`, `shuffle`, `choice`,
`input`, `get_env`, `command_line_args`, `is_number`, `is_string`, `is_list`, `type_of`

`window` also doubles as an implicit identifier inside a `window` block, referring to the window
itself (`window.title = "..."`).

---

## 16. Command-line interface

```bash
leopard run script.lep                  # run a program
leopard run script.lep arg1 arg2        # extra args, readable via command_line_args()
leopard build script.lep                # compile to a standalone executable
leopard build script.lep -o dist/ -n app  # -o: output dir (default .), -n: exe name (default script's filename)
```

Anything after the script's own filename on `leopard run` is passed straight through to the
program, unparsed — `leopard run script.lep -o dist/` gives the script `["-o", "dist/"]`, not `-o`
interpreted as a `leopard` flag. Read it back with `command_line_args()` (§9.5).

`leopard run` changes the working directory to the script's own directory before running, so
relative paths in `read_file`/`play_sound`/image paths/etc. resolve against the script's location,
not the shell's cwd. `leopard build` needs the `build` extra (`pip install -e '.[build]'`); running
a program with a `window` block needs the `gui` extra (`pip install -e '.[gui]'`).

---

## Sources checked

This spec was built by reading, not by trusting prior docs: `lexer.py`, `tokens.py`, `parser.py`,
`ast_nodes.py`, `interpreter.py`, `environment.py`, `errors.py`, `builtins_core.py`,
`builtins_files.py`, `cli.py`, `build.py`, and every file under `gui/` (`app_host.py`, `dialogs.py`,
`events.py`, `menus.py`, `methods.py`, `properties.py`, `sound.py`, `turtle_canvas.py`,
`window_builder.py`), cross-referenced against `../dev-docs/GRAMMAR.md`, `LANGUAGE_GUIDE.md`, and
`../dev-docs/IMPLEMENTATION_PLAN.md`'s phase log (through Phase 16, v0.4.0).
