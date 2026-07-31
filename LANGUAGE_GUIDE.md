<!-- title: The Leopard Language Guide -->

# The Leopard Language Guide

A friendly introduction to Leopard for people who haven't programmed much before —
or who have, and just want to see how Leopard does things. If you already know the
language and want the precise, complete rules, see `GRAMMAR.md` instead; this guide
is the "learn by reading and trying things" companion to that spec.

---

## Getting started

Leopard programs are plain text files ending in `.lep`. You can write and run them
two ways:

**From the command line**, once Leopard is installed:
```bash
leopard run myprogram.lep
```

**From the Leopard IDE** — open a `.lep` file (or start a new one), click **Run**.

Every example in this guide also lives in the IDE's `examples/` folder, ready to
open and run.

---

## Your first program

Leopard programs that don't open a window run silently in the background — they're
for things like file processing, not for showing you something on screen. So the
most satisfying first program is one with a window. Here's the smallest useful one:

```
window "Hello", 300, 100:
    label "Hello, world!" as greeting at 10, 10, 200, 24
```

Run it, and a small window appears with your greeting. Three things happened here:

- `window "Hello", 300, 100:` declares a window titled "Hello", 300 pixels wide and
  100 tall. The colon starts a block, the same way it will for `if`, `while`,
  `function`, and everything else in Leopard.
- Everything indented under it belongs to that window.
- `label "Hello, world!" as greeting at 10, 10, 200, 24` places a text label at
  position (10, 10), sized 200×24 pixels, and gives it the name `greeting` so you
  can refer to it later.

---

## Variables and types

A variable is created the moment you assign it — no separate declaration step:

```
score = 0
name = "Chuck"
found = false
fruits = ["apple", "banana", "cherry"]
```

Leopard has four kinds of values:

| Kind | Examples | Notes |
|---|---|---|
| number | `42`, `3.14` | One numeric type — you don't need to think about int vs. float |
| string | `"hello"` | Always double-quoted |
| boolean | `true`, `false` | Lowercase, and a genuinely separate type from numbers/strings |
| list | `["apple", "banana", "cherry"]` | **1-based** — `fruits[1]` is `"apple"`, not `fruits[0]` |

**Scoping — only `function` calls get their own scope.** A `function` call gets a
private scope of its own: assigning to a variable inside one never affects a
same-named variable outside it, even if one already exists (see
[Functions](#functions) below). Everywhere else — the top level of your program,
a window's own setup code, and **every event handler in that window** — shares one
single scope. This matters because an `on click`/`on change`/etc. block *looks*
like it might be its own private scope the way a function is, but it isn't: a
variable assigned in one event handler is visible — and stays assigned — in every
other event handler in the same window.

That's genuinely useful (it's how a running total, a saved value, or anything else
that needs to persist between clicks works at all), but it also means state can
leak between handlers you didn't expect to be connected. A short example, since
this is the single most common surprise for anyone used to a language where
functions/handlers are more strictly isolated from each other:

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

Clicking "Greet" sees whatever "Save name" most recently stored in `saved_name` —
two separate event handlers, sharing one variable declared up in the window's
setup code. Compare that to a `function` call below, where an assignment never
escapes the one call it happened in.

---

## Expressions and operators

| Category | Operators | Notes |
|---|---|---|
| Arithmetic | `+  -  *  /  %  ^` | `%` is modulo (remainder), `^` is power |
| Joining text | `&` | `"Score: " & str(score)` |
| Comparison | `=  <>  <  >  <=  >=` | `=` means "equal to" — there's no separate `==` |
| Logic | `and  or  not` | Plain English words, not `&&`/`||` |
| Grouping | `( )` | Normal precedence rules apply |

Two things are worth calling out because they're deliberately different from most
other languages:

**`+` only works on numbers.** If you write `"a" + "b"` expecting `"ab"`, Leopard
stops you with an error suggesting `&` instead. Use `&` to join text:

```
"Score: " & str(score)      # correct — & joins strings
"Score: " & score            # error: score is a number, not a string — wrap it in str()
```

**`&` only works on strings — on both sides.** It won't silently convert a number
to text for you; you do that yourself with `str()`. This is a small amount of
friction on purpose: once you've internalized that `5` (a number) and `"5"` (a
string) are genuinely different things, this kind of bug stops happening — in
Leopard and in every other language you go on to learn.

---

## Control flow

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
    x = i

break
continue
```

`for var = start to end step n` counts from `start` to `end`, moving by `n` each
time (`step` defaults to `1` if you leave it out, and can be negative to count
down). `break` exits a loop immediately; `continue` skips to the next iteration.

---

## Functions

One keyword covers both what other languages call "functions" and "procedures" —
if you never `return` anything, it's just a block of code you can call by name:

```
function greet(who):
    return "Hello, " & who

function log(message):
    outputBox.text = outputBox.text & message & "\n"
```

Call a function the same way anywhere: `greet("Chuck")`.

---

## Lists

Lists are 1-based — the first element is `list[1]`, not `list[0]`:

```
fruits = ["apple", "banana", "cherry"]
first = fruits[1]              # "apple"
last = fruits[fruits.length]   # "cherry" — .length gives you the count
fruits.add("date")             # appends "date" to the end
```

---

## Windows and controls

A window's body can declare named controls, each placed with `at x, y, width,
height`:

| Keyword | Creates | Has a caption? |
|---|---|---|
| `textbox` | a single-line text field | no |
| `textedit` | a multi-line text area | no |
| `label` | a plain text label | yes |
| `button` | a clickable button | yes |
| `bmpbutton` | a button showing an image file | yes (an image path) |
| `listbox` | a scrollable list | no |
| `combobox` | a dropdown | no |
| `radiobutton` | a radio button | yes |
| `checkbox` | a checkbox | yes |
| `groupbox` | a labeled grouping box | yes |

Once declared, you read and write a control's state through **properties** —
`control.property = value` to set, `control.property` to read:

```
nameBox.text = "placeholder"
outputArea.color = "darkblue"
fruitList.items = ["Apple", "Banana", "Cherry"]
fruitList.items.add("Date")
first = fruitList.items[1]
```

| Property | Applies to | Meaning |
|---|---|---|
| `.text` | textbox, textedit, label, button | the displayed/entered text |
| `.color` | textbox, textedit, listbox, combobox, label | text color |
| `.background` | any control / window | background color |
| `.font` | any control / window | font family |
| `.checked` | checkbox, radiobutton, checkitem | on/off state |
| `.items` | listbox, combobox | the list of entries (also supports `.add()`) |
| `.selected` | listbox, combobox | the 1-based index of the current selection |
| `.visible`, `.enabled` | any control | show/hide, enable/disable |

See `examples/greeter.lep` for a small complete program using several of these
together, and `examples/fizzbuzz.lep` for a window that combines a loop, a
function, and a list-backed control.

---

## Events

`on <event> <control>:` opens a block of ordinary Leopard code that runs whenever
that event happens:

```
button "Greet" as btnGreet at 220, 10, 80, 24

on click btnGreet:
    if nameBox.text = "":
        notice "Type your name first."
    else:
        notice "Hello, " & nameBox.text
```

| Event | Fires on |
|---|---|
| `on click` | a button, `bmpbutton`, or menu item |
| `on change` | a checkbox, radiobutton, combobox, checkitem, or the text window's `page` |
| `on select` | a listbox or combobox selection changing |
| `on close` | the window closing (no control name needed) |

Every event handler in a window shares one scope with the window's own setup code
and with each other — see [Variables and types](#variables-and-types) above for
what that means in practice and a short example.

---

## Menus

Menus work in every window type, with full submenu and checkable-item support:

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

The `&` before a letter (`&File`, `E&xit`) marks that letter as a keyboard shortcut
within the menu — it's not part of the visible text otherwise. See
`examples/menus.lep` for the complete, runnable version of this program.

---

## Turtle graphics

A `graphics window` gives you a turtle: a cursor with a position, a heading, and a
pen you can raise or lower.

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
    fill "blue"
    circlefilled 40
```

| Command | Does |
|---|---|
| `up` / `down` | raise / lower the pen (raised = moving doesn't draw) |
| `home` | jump to the center, facing north |
| `go n` | move forward `n` pixels in the current direction |
| `goto x, y` | move to an absolute position (draws if the pen is down) |
| `place x, y` | move to an absolute position *without* drawing, pen state or not |
| `turn n` | rotate `n` degrees clockwise |
| `north` | face north without moving |
| `pen "color"` | set the line color |
| `fill "color"` | set the fill color used by the `...filled` shapes |
| `size n` | set the line thickness |
| `font "name"` | set the font used by `text` |
| `text "string"` | draw text at the current position |
| `backcolor "color"` | set the canvas background color |
| `box w, h` / `boxfilled w, h` | rectangle from the current position |
| `circle r` / `circlefilled r` | circle centered on the current position |
| `ellipse w, h` / `ellipsefilled w, h` | ellipse centered on the current position |
| `drawbmp "path", x, y` | draw an image file at a position |

See `examples/turtle_demo.lep` to try this yourself.

---

## Text windows

A `text window` treats its whole content area as one big, fully editable text box,
bound to the reserved name `page`:

```
text window "Notes", 600, 400:

    page.text = "Start typing..."

    on change page:
        wordCountLabel.text = "Editing..."

    on close:
        write_file("notes.txt", page.text)
```

`page` works exactly like any other control — `.text` to read or write its
contents, `on change`/`on close` to react to it — it's just always there,
filling the window, instead of something you declare yourself. See
`examples/notes.lep` for the full version.

---

## Sound

```
play_sound("chime.wav")     # play a WAV once
stop_sound()

play_music("theme.mp3")     # play music (MP3/MIDI) — can be paused/resumed
pause_music()
stop_music()
```

---

## Builtin functions, quick reference

Beyond the operators and control flow above, Leopard ships a set of builtin
functions for everything from type conversion to file I/O:

| Function | Does |
|---|---|
| `str(value)` | convert a number or boolean to a string |
| `num(text)` | convert a string to a number |
| `ascii(char)` | a single character's character code |
| `date()` / `time()` | today's date / the current time, as a string |
| `notice("text")` | show a message box |
| `confirm("question")` → boolean | show a yes/no dialog |
| `ask("prompt")` → string | show a text-entry dialog |
| `write_file(path, text)` / `append_file(path, text)` | write/append a text file |
| `read_file(path)` → string | read a text file |
| `delete_file(path)` | delete a file |
| `make_dir(path)` / `remove_dir(path)` | create/remove a directory |
| `file_exists(path)` → boolean | check whether a file exists |
| `open_file_dialog()` / `save_file_dialog()` | show a file picker |
| `color_dialog()` / `font_dialog()` | show a color/font picker |
| `open_url(url)` | open a URL in the default browser |
| `open_email(address)` | open the default mail client |
| `run_program(command)` | run a shell command |
| `download_file(url, path)` | download a URL to a file |
| `close_window()` / `maximize_window()` / `minimize_window()` | control the current window |

---

## Error handling

There is no `try`/`catch`, no `on error`, and no way to write one — Leopard has
no error-recovery construct at all. **Any error stops the program immediately**,
right at the statement that caused it. Whatever ran before the error already took
effect (a file already written, a window already shown); nothing after it does,
and there's no way to catch the error and keep going.

Errors come in two flavors, both reported the same way — `Line N: message`:

- **Syntax errors** are caught before your program runs at all, e.g.
  `Line 12: expected ':' after 'if' condition`.
- **Runtime errors** happen partway through an already-running program — the two
  you'll hit most often are `+` between two strings and `&` with a non-string
  operand (see [Expressions and operators](#expressions-and-operators) above),
  but calling `num()` on text that isn't a number, indexing a list out of range,
  or calling something that isn't defined all raise one too.

Where the message shows up depends on how you're running the program: `leopard run`
prints it to the terminal and exits with an error status; the IDE writes it to the
console pane; a `leopard build`-compiled program behaves like `leopard run`, since
it's running the same code.

Because there's no way to recover once something goes wrong, the normal style in
Leopard is to check for a risky condition *before* it happens rather than let the
error occur and try to handle it afterward:

```
answer = ask("How old are you?")
if answer = "":
    notice "Please enter your age."
else:
    age = num(answer)
    notice "Next year you'll be " & str(age + 1)
```

`dialogs.lep` and `todo_capstone.lep` in the examples folder both lean on this
pattern throughout — checking `= ""` before using typed-in text, and checking
`selected = 0` before reading a listbox's current selection.

---

## Compiling your program

Once your program works, you can turn it into a standalone app that runs on a
machine with no Python or Leopard installed at all:

```bash
leopard build myprogram.lep
```

This produces a single executable file (in `./dist/` by default — pass `-o` for a
different folder, `-n` for a different name). From the IDE, the same thing happens
with one click: the **Build** toolbar button.

---

## Where to go next

- `GRAMMAR.md` — the complete, precise language spec (every operator, every
  keyword, every builtin, with the exact rules).
- `examples/` (in the IDE's folder) — five complete programs, one for each major
  area covered above.
- `IMPLEMENTATION_PLAN.md` — if you're curious how Leopard itself was built, or
  want to contribute.
