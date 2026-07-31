"""`play_sound`/`stop_sound` (WAV, via `QSoundEffect`) and `play_music`/`stop_music`/
`pause_music` (MP3/MIDI, via `QMediaPlayer`) — GRAMMAR.md §12.

Both the `QSoundEffect` and `QMediaPlayer`/`QAudioOutput` are parented to the window
rather than left as bare locals in this closure — an unparented Qt object referenced
only by a Python closure can be garbage-collected mid-flight (playback is
asynchronous: `.play()` returns immediately), the same class of bug Phase 5 hit with
`QMenu` — see IMPLEMENTATION_PLAN.md's decisions log.
"""

from __future__ import annotations

import os

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer, QSoundEffect
from PyQt6.QtWidgets import QWidget

from ..errors import describe_type


def _require_existing_file(path: str, fn_name: str) -> None:
    if not isinstance(path, str):
        raise TypeError(f"{fn_name}() needs a string, not {describe_type(path)}")
    if not os.path.isfile(path):
        raise ValueError(f"file '{path}' does not exist")


def build_sound_builtins(window: QWidget) -> dict:
    effect = QSoundEffect(window)
    player = QMediaPlayer(window)
    audio_output = QAudioOutput(window)
    player.setAudioOutput(audio_output)

    def play_sound(path: str) -> None:
        _require_existing_file(path, "play_sound")
        effect.setSource(QUrl.fromLocalFile(path))
        effect.play()

    def stop_sound() -> None:
        effect.stop()

    def play_music(path: str) -> None:
        _require_existing_file(path, "play_music")
        player.setSource(QUrl.fromLocalFile(path))
        player.play()

    def stop_music() -> None:
        player.stop()

    def pause_music() -> None:
        player.pause()

    return {
        "play_sound": play_sound,
        "stop_sound": stop_sound,
        "play_music": play_music,
        "stop_music": stop_music,
        "pause_music": pause_music,
    }
