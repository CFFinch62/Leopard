import os
import pathlib

import pytest

# GUI tests (Phase 4+) run headless by default — set before any Qt import happens.
# Override by setting QT_QPA_PLATFORM yourself before running pytest if you want to
# watch them on a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROGRAMS_DIR = pathlib.Path(__file__).parent / "programs"


@pytest.fixture
def programs_dir() -> pathlib.Path:
    return PROGRAMS_DIR
