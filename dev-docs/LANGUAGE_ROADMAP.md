<!-- title: Leopard language roadmap — standard features not yet present -->

# Leopard language roadmap — standard features not yet present

**Purpose:** a second backlog-review document, complementary to `FEATURE_PARITY_REVIEW.md`. That
document compares Leopard against what the *original* `leopard.bas` could do. This one is
different: it compares Leopard against what a general-purpose language — BASIC dialects
especially, but really any language a beginner graduates to next — is normally expected to have,
regardless of whether the 2013 original ever had it. The original Leopard was a thin GUI-action
scripting layer with no real expressions of its own; this rewrite already gave it real arithmetic,
`if`/`while`/`for`, and functions (`GRAMMAR.md` status notes), which is *more* than the original
had. This document is about the next step past that: the everyday stdlib functions and control-flow
forms that "a language like BASIC" — and every mainstream language since — ships with, that
Leopard still doesn't.

Every claim below was verified against source (`builtins_core.py`, `tokens.py`, `parser.py`,
`interpreter.py`), not assumed. Nothing here is a recommendation to add it — it's the map to choose
from.

---

## 1. Math functions — **entirely absent**

Leopard has `+ - * / % ^` as operators and nothing else numeric. There is no math library exposed
to Leopard programs at all — not even the classic BASIC set (`SQR`, `ABS`, `INT`, `SGN`, `SIN`,
`COS`, `TAN`, `LOG`, `EXP`, `RND`). Confirmed: Python's `math` module is imported only inside
`gui/turtle_canvas.py` for internal heading math — nothing from it is reachable from a Leopard
program.

| Missing | What it'd do | Why it matters |
|---|---|---|
| `abs(n)` | absolute value | extremely common, not currently writable at all without a manual `if n < 0: n = 0 - n` |
| `sqrt(n)` | square root | needed for any distance/geometry math |
| `round(n)` / `round(n, digits)` | round to nearest whole number / to N decimal places | needed to display computed numbers cleanly — right now a computed `7/3` prints all of Python's float repr |
| `floor(n)` / `ceil(n)` | round down / up | common in grid/pixel math, especially alongside turtle graphics |
| `min(a, b)` / `max(a, b)` | smaller/larger of two numbers | one of the most-reached-for functions in any language; today requires a 3-line `if` every time |
| `sign(n)` | -1 / 0 / 1 | occasional but classic BASIC (`SGN`) |
| `sin(n)` / `cos(n)` / `tan(n)` | trig, degrees or radians | classic BASIC set; also natural pairing with the turtle graphics control's heading math, which already computes these internally per-command |
| `log(n)` / `exp(n)` | natural log / e^n | classic BASIC set (`LOG`, `EXP`), lower priority than the above |
| `pi` | the constant `3.14159...` | needed for any manual circle/angle math a program does outside the turtle control |
| `random()` / `random(min, max)` | random float 0–1, or random integer in a range | **the single biggest gap in this whole document** — see §2 |

`^` already covers `pow()`-style exponentiation as an operator, so a dedicated `pow()` function
would be pure redundancy — not listed as a gap.

---

## 2. Randomness — **entirely absent, worth calling out on its own**

There is no random-number source anywhere in Leopard — no `random`, `rnd`, `randint`, nothing.
Grepped the full interpreter and builtins; zero hits. This is worth flagging separately from the
math table above because of how much it forecloses: **no dice game, no card shuffle, no random
turtle art, no "pick a random encouragement message," no procedurally varied anything** is
currently writable in Leopard at all. For a language whose worked examples lean toward small
teaching programs and games (`fizzbuzz.lep`, `todo_capstone.lep`, turtle art), this is arguably
the highest-value single addition on this whole list.

A minimal version needs just two functions:

| Function | Returns |
|---|---|
| `random()` | a float, `0 <= n < 1` |
| `random_int(min, max)` | a whole number, `min <= n <= max` inclusive |

(`shuffle(list)` and `choice(list)` — see §4 — build naturally on top of these once they exist.)

---

## 3. String functions — thin today

`../user-docs/LANGUAGE_SPEC.md` §8 already documents Leopard's current string toolkit in full:
`s[i]` indexing, `.length`, `split()`, `join()`, `ascii()`, `str()`, `num()`. That's genuinely all
of it. Compared to BASIC's classic string set (`UCASE$`, `LCASE$`, `MID$`, `LEFT$`, `RIGHT$`,
`INSTR`, `TRIM$`) or any modern language's `str` methods, here's what's not there:

| Missing | What it'd do | BASIC's name for it |
|---|---|---|
| `upper(s)` / `lower(s)` | case conversion | `UCASE$` / `LCASE$` |
| `trim(s)` | strip leading/trailing whitespace | `TRIM$` |
| `contains(s, sub)` | substring test → boolean | (via `INSTR` > 0) |
| `index_of(s, sub)` | position of a substring, or a not-found sentinel | `INSTR` |
| `replace(s, old, new)` | substring replacement | (no direct BASIC equivalent, but universal elsewhere) |
| `starts_with(s, prefix)` / `ends_with(s, suffix)` | prefix/suffix test → boolean | (via `LEFT$`/`RIGHT$` + `=`) |
| `substring(s, start, end)` (or `mid(s, start, len)`, BASIC-style) | extract a range of characters | `MID$` |
| `left(s, n)` / `right(s, n)` | first/last N characters | `LEFT$` / `RIGHT$` |
| `reverse(s)` | reverse a string | — |
| `chr(code)` | character for a character code | `CHR$` — **notably, this is the missing inverse of `ascii()`, which already exists.** Leopard can go char→code but not code→char. |

`chr(code)` stands out because it's not a new category, just an asymmetry — `ascii()` exists,
its inverse doesn't.

---

## 4. List functions — beyond `.add()`

`../user-docs/LANGUAGE_SPEC.md` §7 already documents that `.add()` is deliberately the *only* list method today
("rebuild, don't remove" is the stated idiom). That's a real design stance, not an oversight — but
worth listing what it currently forecloses, in case any of these are worth an exception:

| Missing | What it'd do |
|---|---|
| `sort(list)` | sort a list of numbers or strings |
| `reverse(list)` | reverse element order |
| `contains(list, value)` | membership test → boolean |
| `index_of(list, value)` | position of a value, or a not-found sentinel |
| `remove_at(list, index)` | remove one element by position |
| `sum(list)` / `min(list)` / `max(list)` | aggregate over a numeric list |
| `shuffle(list)` | randomize order (depends on §2's randomness first) |
| `choice(list)` | pick one random element (depends on §2's randomness first) |

**Not a gap, confirmed working:** nested lists (`[[1, 2], [3, 4]]`) already work fine — list
literals evaluate each element generically, so a list-of-lists (a 2D grid, common in small games)
is already writable and indexable today (`grid[1][2]`) with zero new features needed.

---

## 5. Control-flow forms BASIC/most languages have that Leopard doesn't

| Missing | What it looks like elsewhere | Leopard today |
|---|---|---|
| Post-test loop (`do...while` / BASIC's `DO...LOOP UNTIL`) | body always runs once before the condition is checked | only pre-test `while` — a "run at least once" loop needs an awkward manual duplication of the first iteration |
| Multi-way branch (`switch`/BASIC's `SELECT CASE`) | dispatch on one value against several cases without a repeated `if x = ... elseif x = ...` chain | only `if`/`elseif`/`else` — works, just verbose past 3-4 branches |
| `for item in list:` (for-each) | iterate a list's elements directly | only numeric `for i = start to end [step n]` — iterating a list today means `for i = 1 to fruits.length: fruit = fruits[i]`, an extra line and an extra variable every time |

All three are convenience/ergonomics, not missing capability — everything they'd do is already
possible via `while` + manual indexing. Listed because "control flow BASIC has" was explicitly
part of what you asked about, and for-each in particular is the one of these three that shows up
constantly once list use grows past toy examples.

---

## 6. Console input — bare (no-window) scripts are output-only

A no-window Leopard script can `print()` but has **no way to read anything back** — no `input()`,
no stdin-reading builtin of any kind. `ask()` exists but is GUI-only (raises `'ask' needs a window
(not available yet)` with no window declared — confirmed in `interpreter.py`'s `_GUI_ONLY_NAMES`).
Every one of BASIC's dialects had a console `INPUT` statement precisely because "ask the user a
question, get an answer" is the most basic form of interactivity a language can offer, and today
Leopard can only do it inside a GUI program.

| Missing | What it'd do |
|---|---|
| `input()` (or `console_input(prompt)`) | read one line of text from stdin, for a bare script |

Related, lower-priority gaps in the same "a bare script can't get external data in" family:

| Missing | What it'd do |
|---|---|
| Command-line arguments | a bare script currently has no way to see any arguments passed after its own filename on `leopard run script.lep ...` |
| Environment variables | `get_env(name)` — reading OS environment variables |

---

## 7. Type introspection — notable given there's no `try`/`catch`

`GRAMMAR.md` §16 documents that Leopard deliberately has no `try`/`catch`/`on error` — any error
just stops the program. That's a stated, settled design choice, not listed here as a gap. But it
does make one thing sharper: **the only defensive tool a Leopard program has against a type error
is checking first**, and today it can't, because there's no way to ask "what type is this value?"
from inside a program.

| Missing | What it'd do |
|---|---|
| `is_number(value)` | boolean type check |
| `is_string(value)` | boolean type check |
| `is_list(value)` | boolean type check |
| `type_of(value)` | returns a string name (`"number"`/`"string"`/`"boolean"`/`"list"`) for cases needing more than a single yes/no check |

The closest thing today is `num()` itself throwing on bad input — which, with no `try`/`catch`,
means a program can't attempt a conversion and recover; it can only crash. `is_number("abc")` (or
similarly, a non-throwing "can this string become a number" check) would let a program validate
*before* calling `num()`, which is exactly the "check the risky condition first" style
`../user-docs/LANGUAGE_SPEC.md` §14 already says is idiomatic Leopard — the language just doesn't yet give a
program the tool to do that check for types the way it already can for e.g. `if selected = 0:`.

---

## Summary table

| Category | Status | Suggested priority |
|---|---|---|
| Randomness (`random()`, `random_int()`) | Absent | **High** — forecloses an entire class of programs (games, procedural art) that the language's own examples lean toward |
| Math functions (`abs`, `sqrt`, `round`, `floor`/`ceil`, `min`/`max`, trig, `pi`) | Absent | High — `round`/`min`/`max` especially are reached for constantly; trig pairs naturally with turtle graphics |
| String functions (`upper`/`lower`, `trim`, `replace`, `contains`, `substring`/`left`/`right`, `chr`) | Thin (only `split`/`join`/`.length`/`[i]`) | High — this is the exact category that prompted this whole review |
| `for item in list:` (for-each) | Absent (numeric range only) | Medium — pure ergonomics, but list use is common and the manual-index workaround is verbose every single time |
| List functions (`sort`, `contains`, `index_of`, `remove_at`, `sum`/`min`/`max`) | Absent beyond `.add()` | Medium — weigh against the deliberate "rebuild, don't remove" stance already on record |
| Console `input()` for bare scripts | Absent | Medium — currently the only interactivity a no-window script can offer is none at all |
| `switch`/`select case` | Absent | Low — convenience only, `elseif` chains already cover it |
| `do...while` / post-test loop | Absent | Low — convenience only |
| Type introspection (`is_number`, `type_of`) | Absent | Low-Medium — most useful specifically *because* there's no `try`/`catch`, as the one available defensive tool |
| Command-line args / env vars for bare scripts | Absent | Low — niche outside script-automation use cases |
