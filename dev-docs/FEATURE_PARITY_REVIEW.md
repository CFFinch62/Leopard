<!-- title: Leopard vs. the original leopard.bas — feature parity review -->

# Leopard vs. the original `leopard.bas` — feature parity review

**Purpose:** a backlog-review document, not a spec. Everything below is something the original
Liberty BASIC `leopard.bas` (`original -source/leopard.bas`, Brandon Watts) could do that today's
Leopard (`src/leopard_lang`, v0.4.0) cannot — found by reading the whole 2,501-line source file and
cross-referencing its two command-dispatch tables (`textbp$`/`[TextBL]`, the window-body parser;
`boce$`/`[OnclickEvents]`, the runtime action-verb parser) against every builtin currently in
`../user-docs/LANGUAGE_SPEC.md`. Nothing here is a recommendation to implement — it's the raw list
to decide against.

**Explicitly out of scope, per your instructions:**
- The original's `window` / `text window` / `graphics window` split — Leopard's unified
  `graphics`/`textedit` controls are a deliberate, already-settled redesign, not a gap.
- `beep()` and `set_cursor()` — already tracked as a known gap in `../user-docs/LANGUAGE_SPEC.md` §9.12, not
  repeated here in detail.
- The original's fixed five-slot control naming (`textboxtwo`..`textboxfive`,
  `varone`..`varfive`, etc.) — deliberately replaced by unlimited user-named controls
  (`GRAMMAR.md` status #3). Not a gap, a redesign.

---

## 1. Printing to a physical printer — **entirely absent**

The original had a full print pipeline; Leopard has none at all, on any control or window.

| Original command | What it did |
|---|---|
| `print` (button-onclick action) | `lprint` the click event text, then `dump` (screenshot the window to the printer) |
| `printer textbox` / `...two`/`...three`/`...four`/`...five` | send a specific textbox's contents to the printer |
| `printer textedit` / `...two`/`...three`/`...four`/`...five` | send a specific textedit's contents to the printer |
| `printerdialog` | show the OS printer-selection/setup dialog |

**Note:** this isn't a new discovery — `GRAMMAR.md` §12 already lists `printerdialog`/`print (to
printer)` as "deferred — niche even in 2013." Including it here for completeness since it's a
whole missing category, not a one-off.

**To consider:** Qt has `QPrinter`/`QPrintDialog` for this if you ever want it — cross-platform,
not a Windows-only DLL call like most of the rest of this document. Of everything in this file,
this is the one category built on infrastructure that would actually port cleanly.

---

## 2. Multimedia — video playback: **entirely absent**

The original drove video through Windows' MCI (`mciSendString`) — all Windows-only, all gone in
Leopard, and Leopard's sound support (`play_sound`/`play_music`, Qt Multimedia) has no video
counterpart at all.

| Original command | What it did |
|---|---|
| `play avi` | play an AVI file in a window |
| `play avi fullscreen` | play an AVI file fullscreen |
| `play mpeg` | play an MPEG file in a popup window |
| `play mpeg fullscreen` | play an MPEG file fullscreen, sized to the display |
| `pause video` | pause whichever video is playing |
| `stop video` | stop/close whichever video is playing |

**To consider:** Qt Multimedia (already a Leopard dependency for `play_music`) has
`QVideoWidget`/`QMediaPlayer` for exactly this — if this is wanted, it'd slot in next to
`gui/sound.py` fairly naturally as a `gui/video.py`, exposed as something like
`play_video(path)` / `play_video_fullscreen(path)` / `pause_video()` / `stop_video()`. Real
implementation work, not a stub, but not exotic either.

---

## 3. Multimedia — MIDI playback: **uncertain, worth testing**

| Original command | What it did |
|---|---|
| `play midi` | opens the file as an MCI "sequencer" device and plays it — a separate code path from `play mp3`'s "MpegVideo" device type |

Leopard's `play_music(path)` is generic — it hands any path to Qt Multimedia's `QMediaPlayer` — so
a `.mid` file *might* just work today, or might silently fail depending on the platform's installed
codecs (MIDI playback support in Qt Multimedia is backend-dependent, unlike MP3). This isn't a
confirmed gap, just an untested edge: worth a five-minute manual check with a real `.mid` file
before deciding whether it needs its own code path.

---

## 4. Dialog builtins — capability reductions

Leopard has these three, but each lost arguments the original had:

| Dialog | Original signature | Leopard today | What's lost |
|---|---|---|---|
| `filedialog` | `filedialog "Open Program...", "*.lep", fileName$` — title + file-extension filter, result into a variable | `open_file_dialog()` / `save_file_dialog()` — no arguments | Can't set a dialog title or restrict the file-type filter; every file dialog looks the same regardless of what the program is picking a file for |
| `fontdialog` | `fontdialog "courier_new 10 bold italic", newFontSpec$` — takes a starting spec, returns full spec (family + size + bold/italic) | `font_dialog()` — no arguments, returns family name only | Can't preset a starting font; can't get back size or bold/italic, only the family name |
| `colordialog` | `colordialog boct$, r$` — takes a starting color | `color_dialog()` — no arguments | Can't preset a starting color |

None of these are missing outright — they all work — but a Leopard program can't do anything today
that depends on presetting the dialog's starting state, a custom title, or getting back more than
one piece of information (font family only, no size/weight).

---

## 5. System / OS integration

| Original command | What it did | Notes |
|---|---|---|
| `drives` | `notice Drives$` — shows a list of available disk drives | Windows-drive-letter concept (`C:\`, `D:\`, ...); doesn't map cleanly to Linux/macOS mount points. Cross-platform equivalent would need real thought about what it should even mean today. |
| `restart` | calls the Windows shutdown API to restart the machine | **Not recommended for porting** — a language builtin that reboots the user's computer is a large blast-radius, easy-to-fire-by-accident footgun, and every modern OS gates this behind privilege prompts anyway. Flagging for completeness, not advocating for it. |
| `swap mouse` / `swap mouse back` | swaps the left/right mouse buttons (accessibility toggle) and reverses it | Windows-specific `SwapMouseButton` API call. Modern OSes handle this at the system-settings level, not per-app — a program-controlled global mouse-button swap is unusual functionality for an app-level language to own. |

---

## 6. Minor behavioral divergence, not a missing feature

| Original | Leopard | 
|---|---|
| `time` action → `notice amPmTime$(time$())`, a 12-hour `H:MM AM/PM` string | `time()` → 24-hour `HH:MM:SS` | 

Not a gap — `time()` works, just formats differently. Flagging only in case the 12-hour display
format itself (not the underlying capability) is something you want to match.

---

## 7. Checked and confirmed *not* gaps

These original commands looked like standalone features at first grep, but each is just the
original's shorthand for something Leopard already does by composing two existing builtins —
listing them so you don't waste backlog time re-adding them as if they were missing:

| Original command | What it did | Leopard equivalent today |
|---|---|---|
| `read file textedit` (and `...two`..`...five`) | load a file straight into a textedit control | `myTextedit.text = read_file(path)` |
| `textedit file` (and `...two`..`...five`) | dump a textedit control's contents to a file | `append_file(path, myTextedit.text)` |
| `textbox file` (and `...two`..`...five`) | dump a textbox control's contents to a file | `append_file(path, myTextbox.text)` |
| `run text` | `run "notepad "; boct$` — always launches Notepad on a file | `run_program("notepad " & path)` (or any other command) — Leopard's `run_program` is already fully general, the original's was hardcoded to one app |
| `cd open` / `cd close` | open/close the CD-ROM tray | Hardware that doesn't meaningfully exist on the machines Leopard programs run on today — not "missing," just obsolete |

---

## 8. One dead end found in the original itself (trivia, not a gap)

While tracing every `gosub` target, `spritebcheck$` is set to `"stop"` and checked
(`if spritebcheck$ = "continue" then gosub [SpriteBC]`) but is **never** set to `"continue"`
anywhere in the file, and the `[SpriteBC]` label it would jump to is never defined at all. This
looks like a sprite/animation feature the original author started wiring up and abandoned before
it ever worked — it's not something Leopard is missing relative to a working original feature,
since it never worked in `leopard.bas` either. Mentioned only because it surfaced during the
source read and might explain "sprites" if that rings a bell from the original project's history.

---

## Summary table

| Category | Status | Suggested priority if you want it |
|---|---|---|
| Printer support (`print`, `printer textbox/textedit`, `printerdialog`) | Absent | Low — niche even by the original's own era, but the one item here with clean cross-platform infra available (`QPrinter`) |
| Video playback (avi/mpeg, play/pause/stop/fullscreen) | Absent | Medium — real capability gap in "multimedia," Qt Multimedia already a dependency |
| MIDI via `play_music` | Untested | Trivial — just try a `.mid` file before doing anything |
| `filedialog`/`fontdialog`/`colordialog` args (title, filter, starting value, full font spec) | Reduced | Low-Medium — small, contained additions to existing builtins, not new features |
| `drives` | Absent | Low — unclear what it should even mean cross-platform |
| `restart` | Absent | Skip — recommend not porting |
| `swap mouse`/`swap mouse back` | Absent | Skip — belongs at the OS level, not the language level |
| 12-hour `time()` format | Divergent, not missing | Skip unless you specifically want to match the old format |
