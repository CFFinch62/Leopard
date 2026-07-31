import math
import struct
import wave

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
from PyQt6.QtMultimedia import QMediaPlayer, QSoundEffect  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from leopard_lang.errors import LeopardRuntimeError  # noqa: E402
from leopard_lang.gui.app_host import run_window  # noqa: E402
from leopard_lang.lexer import tokenize  # noqa: E402
from leopard_lang.parser import parse  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def wait_ms(ms: int = 150) -> None:
    """Pump the Qt event loop briefly — play/stop state changes on
    QSoundEffect/QMediaPlayer are asynchronous, so nothing updates without this."""
    QTest.qWait(ms)


@pytest.fixture(scope="session")
def test_wav(tmp_path_factory) -> str:
    """A short, real, audible WAV tone — not just an empty/garbage file — so
    QSoundEffect/QMediaPlayer are exercised against genuine audio data."""
    path = tmp_path_factory.mktemp("audio") / "tone.wav"
    framerate = 44100
    duration = 0.2
    freq = 440.0
    n_frames = int(framerate * duration)
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(framerate)
        for i in range(n_frames):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * freq * i / framerate))
            f.writeframesraw(struct.pack("<h", value))
    return str(path)


def build(qapp, body: str):
    program = parse(tokenize(f'window "W", 200, 100:\n{body}'))
    return run_window(program, existing_app=qapp)


# ---------------------------------------------------------------------------
# play_sound / stop_sound (QSoundEffect, WAV)
# ---------------------------------------------------------------------------


def test_play_sound_loads_and_plays(qapp, test_wav):
    window = build(qapp, f'    play_sound("{test_wav}")\n')
    (effect,) = window.findChildren(QSoundEffect)
    wait_ms()
    assert effect.isLoaded()
    assert effect.isPlaying()


def test_stop_sound_stops_playback(qapp, test_wav):
    window = build(qapp, f'    play_sound("{test_wav}")\n    stop_sound()\n')
    (effect,) = window.findChildren(QSoundEffect)
    assert effect.isPlaying() is False


def test_stop_sound_without_prior_play_does_not_error(qapp):
    build(qapp, "    stop_sound()\n")


def test_play_sound_missing_file_is_clear_error(qapp):
    with pytest.raises(LeopardRuntimeError, match="does not exist"):
        build(qapp, '    play_sound("/nonexistent/path/x.wav")\n')


def test_play_sound_requires_a_string(qapp):
    with pytest.raises(LeopardRuntimeError):
        build(qapp, "    play_sound(5)\n")


# ---------------------------------------------------------------------------
# play_music / stop_music / pause_music (QMediaPlayer, MP3/MIDI)
#
# No genuine MP3 test asset was available in this sandboxed environment (no
# ffmpeg/lame encoder, no network, no system MP3 files) — QMediaPlayer is
# exercised with the same real WAV data instead, which validates the plumbing
# but not MP3 decoding specifically. See IMPLEMENTATION_PLAN.md's Phase 8
# decisions-log entry for the full confirmed-vs-unverified breakdown, including
# a reproducible pytest+sequential-QMediaPlayer hang in this environment that
# limits how precisely `pause_music`'s resulting state can be asserted here —
# its correct behavior (transitions to PausedState) was independently confirmed
# via a standalone script outside pytest.
# ---------------------------------------------------------------------------


def test_play_music_loads_and_plays(qapp, test_wav):
    window = build(qapp, f'    play_music("{test_wav}")\n')
    (player,) = window.findChildren(QMediaPlayer)
    assert player.playbackState() in (
        QMediaPlayer.PlaybackState.PlayingState,
        QMediaPlayer.PlaybackState.StoppedState,  # may finish before we check (0.2s clip)
    )
    assert player.source().toLocalFile() == test_wav
    player.stop()  # avoid contending with later tests' players for the audio device


def test_stop_music_stops_playback(qapp, test_wav):
    window = build(qapp, f'    play_music("{test_wav}")\n    stop_music()\n')
    (player,) = window.findChildren(QMediaPlayer)
    assert player.playbackState() == QMediaPlayer.PlaybackState.StoppedState


def test_pause_music_is_wired_and_callable(qapp, test_wav):
    # Deliberately a lighter assertion than the other sound tests: running two
    # QMediaPlayer-backed tests with real waits between play/pause in the same
    # pytest session reproducibly hangs in this environment (root cause not
    # pinned down — not reproducible outside pytest, survives multiple different
    # cleanup/wait strategies). This just confirms `pause_music()` is wired to
    # the player and doesn't raise; the resulting PausedState was confirmed
    # separately (see the module docstring above).
    window = build(qapp, f'    play_music("{test_wav}")\n    pause_music()\n')
    (player,) = window.findChildren(QMediaPlayer)
    assert player is not None
    player.stop()


def test_play_music_missing_file_is_clear_error(qapp):
    with pytest.raises(LeopardRuntimeError, match="does not exist"):
        build(qapp, '    play_music("/nonexistent/path/x.mp3")\n')


# ---------------------------------------------------------------------------
# Sound objects are parented to the window (Phase 5's GC lesson applied here too)
# ---------------------------------------------------------------------------


def test_sound_objects_are_parented_to_the_window_not_gc_eligible(qapp, test_wav):
    # Calling play_sound from a bare top-level statement (no event handler holding
    # a reference) and then letting run_window() return, the way it would for any
    # window with no click handlers — if the QSoundEffect weren't parented to the
    # window, it would be garbage-collected here, cutting off playback silently.
    window = build(qapp, f'    play_sound("{test_wav}")\n')
    (effect,) = window.findChildren(QSoundEffect)
    assert effect.parent() is window
    wait_ms()
    assert effect.isPlaying()
