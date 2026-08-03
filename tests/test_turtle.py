import pathlib

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
from PyQt6.QtWidgets import QApplication  # noqa: E402

from leopard_lang.errors import LeopardRuntimeError  # noqa: E402
from leopard_lang.gui.app_host import run_window  # noqa: E402
from leopard_lang.gui.turtle_canvas import TurtleCanvas  # noqa: E402
from leopard_lang.lexer import tokenize  # noqa: E402
from leopard_lang.parser import parse  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def build(qapp, body: str, width=640, height=480):
    source = (
        f'window "T", {width}, {height}:\n'
        f'    graphics as canvas1 at 0, 0, {width}, {height}\n{body}'
    )
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    return window, window.findChild(TurtleCanvas)


def pixel(canvas: TurtleCanvas, x: int, y: int) -> str:
    return canvas._pixmap.toImage().pixelColor(x, y).name()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_initial_state_is_centered_facing_north_pen_up(qapp):
    _window, canvas = build(qapp, "    canvas1.up()\n", width=640, height=480)
    assert (canvas.x, canvas.y) == (320, 240)
    assert canvas.heading == 0.0
    assert canvas.pen_is_down is False


# ---------------------------------------------------------------------------
# Pen state, movement, heading
# ---------------------------------------------------------------------------


def test_down_then_up(qapp):
    _window, canvas = build(qapp, "    canvas1.down()\n    canvas1.up()\n")
    # down sets True, then up sets False again — confirms both actually run
    assert canvas.pen_is_down is False


def test_go_moves_north_by_default_heading(qapp):
    _window, canvas = build(qapp, "    canvas1.down()\n    canvas1.go(100)\n")
    assert canvas.x == pytest.approx(320)
    assert canvas.y == pytest.approx(140)
    assert pixel(canvas, 320, 200) == "#000000"  # default black pen, drawn


def test_go_does_not_draw_with_pen_up(qapp):
    _window, canvas = build(qapp, "    canvas1.go(100)\n")
    assert pixel(canvas, 320, 200) == "#ffffff"


def test_turn_changes_heading_and_go_direction(qapp):
    _window, canvas = build(qapp, "    canvas1.turn(90)\n    canvas1.down()\n    canvas1.go(100)\n")
    assert canvas.heading == 90.0
    assert canvas.x == pytest.approx(420)
    assert canvas.y == pytest.approx(240)


def test_turn_wraps_at_360(qapp):
    _window, canvas = build(qapp, "    canvas1.turn(350)\n    canvas1.turn(20)\n")
    assert canvas.heading == pytest.approx(10.0)


def test_goto_moves_and_draws_when_pen_down(qapp):
    _window, canvas = build(qapp, "    canvas1.down()\n    canvas1.goto(100, 100)\n")
    assert (canvas.x, canvas.y) == (100, 100)
    # on the line from (320,240) to (100,100); +/- a couple px for rasterization
    assert any(pixel(canvas, 200, y) == "#000000" for y in range(160, 167))


def test_place_moves_without_drawing_even_with_pen_down(qapp):
    _window, canvas = build(qapp, "    canvas1.down()\n    canvas1.place(100, 100)\n")
    assert (canvas.x, canvas.y) == (100, 100)
    # a straight line from (320,240) to (100,100) would cross roughly (210, 170)
    assert pixel(canvas, 210, 170) == "#ffffff"


def test_home_resets_position_and_heading(qapp):
    _window, canvas = build(qapp, "    canvas1.turn(45)\n    canvas1.goto(10, 10)\n    canvas1.home()\n")
    assert (canvas.x, canvas.y) == (320, 240)
    assert canvas.heading == 0.0


def test_north_resets_heading_without_moving(qapp):
    _window, canvas = build(qapp, "    canvas1.turn(45)\n    canvas1.goto(10, 10)\n    canvas1.north()\n")
    assert (canvas.x, canvas.y) == (10, 10)
    assert canvas.heading == 0.0


# ---------------------------------------------------------------------------
# Colors, size, font
# ---------------------------------------------------------------------------


def test_pen_sets_line_color(qapp):
    _window, canvas = build(qapp, '    canvas1.pen("blue")\n    canvas1.down()\n    canvas1.go(50)\n')
    assert canvas.pen_color.name() == "#0000ff"
    assert pixel(canvas, 320, 220) == "#0000ff"


def test_fill_sets_shape_fill_color(qapp):
    _window, canvas = build(qapp, '    canvas1.fill("green")\n    canvas1.circlefilled(20)\n')
    assert canvas.fill_color.name() == "#008000"
    assert pixel(canvas, 320, 240) == "#008000"


def test_invalid_color_name_is_clear_error(qapp):
    with pytest.raises(LeopardRuntimeError, match="not a recognized color"):
        build(qapp, '    canvas1.pen("not-a-real-color")\n')


def test_size_sets_pen_width(qapp):
    _window, canvas = build(qapp, "    canvas1.size(5)\n")
    assert canvas.pen_size == 5


def test_backcolor_fills_background(qapp):
    _window, canvas = build(qapp, '    canvas1.backcolor("yellow")\n')
    assert pixel(canvas, 5, 5) == "#ffff00"


# ---------------------------------------------------------------------------
# Shapes
# ---------------------------------------------------------------------------


def test_circle_is_outline_only(qapp):
    _window, canvas = build(qapp, "    canvas1.circle(30)\n")
    assert pixel(canvas, 320, 240) == "#ffffff"  # center untouched
    assert pixel(canvas, 320, 210) == "#000000"  # top edge of the circle


def test_circlefilled_fills_center(qapp):
    _window, canvas = build(qapp, "    canvas1.circlefilled(30)\n")
    assert pixel(canvas, 320, 240) == "#000000"


def test_box_is_outline_only(qapp):
    _window, canvas = build(qapp, "    canvas1.box(60, 40)\n")
    assert pixel(canvas, 350, 260) == "#ffffff"  # interior untouched
    assert pixel(canvas, 320, 240) == "#000000"  # top-left corner is on the outline


def test_boxfilled_fills_interior(qapp):
    _window, canvas = build(qapp, "    canvas1.boxfilled(60, 40)\n")
    assert pixel(canvas, 350, 260) == "#000000"


def test_ellipse_and_ellipsefilled(qapp):
    _window, canvas = build(qapp, "    canvas1.ellipsefilled(80, 40)\n")
    assert pixel(canvas, 320, 240) == "#000000"


def test_text_draws_something(qapp):
    _window, canvas = build(qapp, '    canvas1.text("Hi")\n')
    img = canvas._pixmap.toImage()
    box = img.copy(300, 220, 60, 30)
    assert any(
        box.pixelColor(x, y).name() != "#ffffff"
        for x in range(box.width())
        for y in range(box.height())
    )


def test_drawbmp_missing_file_is_clear_error(qapp):
    with pytest.raises(LeopardRuntimeError, match="could not be loaded"):
        build(qapp, '    canvas1.drawbmp("/nonexistent/path/x.bmp", 0, 0)\n')


# ---------------------------------------------------------------------------
# Turtle methods only exist on a `graphics` control
# ---------------------------------------------------------------------------


def test_turtle_method_unavailable_on_non_graphics_control(qapp):
    program = parse(tokenize(
        'window "W", 100, 100:\n'
        '    button "Go" as mybutton at 0, 0, 50, 20\n'
        '    mybutton.pen("red")\n'
    ))
    with pytest.raises(LeopardRuntimeError, match="needs a GUI control"):
        run_window(program, existing_app=qapp)


def test_bare_turtle_command_without_receiver_is_a_syntax_error(qapp):
    from leopard_lang.errors import LeopardSyntaxError

    with pytest.raises(LeopardSyntaxError):
        parse(tokenize('window "W", 100, 100:\n    graphics as canvas1 at 0, 0, 100, 100\n    pen "red"\n'))


# ---------------------------------------------------------------------------
# Multiple named `graphics` controls have independent turtle state
# ---------------------------------------------------------------------------


def test_two_graphics_controls_have_independent_turtle_state(qapp):
    source = (
        'window "W", 300, 150:\n'
        "    graphics as canvas1 at 0, 0, 150, 150\n"
        "    graphics as canvas2 at 150, 0, 150, 150\n"
        "    canvas1.turn(90)\n"
        "    canvas1.down()\n"
        "    canvas1.go(50)\n"
        "    canvas2.down()\n"
        "    canvas2.go(50)\n"
    )
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    canvases = window.findChildren(TurtleCanvas)
    assert len(canvases) == 2
    canvas1 = next(c for c in canvases if c.pos().x() == 0)
    canvas2 = next(c for c in canvases if c.pos().x() == 150)

    assert canvas1.heading == 90.0
    assert (canvas1.x, canvas1.y) == pytest.approx((125, 75))

    assert canvas2.heading == 0.0
    assert (canvas2.x, canvas2.y) == pytest.approx((75, 25))


# ---------------------------------------------------------------------------
# Full GRAMMAR.md §10 example, standalone (no IDE)
# ---------------------------------------------------------------------------


def test_grammar_section_10_example_end_to_end(qapp):
    source = (pathlib.Path(__file__).parent / "programs" / "turtle_graphics.lep").read_text()
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    canvas = window.findChild(TurtleCanvas)

    assert (canvas.x, canvas.y) == (300, 300)
    assert canvas.heading == 90.0
    assert canvas.pen_is_down is False
    assert canvas.pen_color.name() == "#ff0000"
    assert canvas.pen_size == 3

    # the up-then-right "L" path, drawn in red
    assert pixel(canvas, 320, 190) == "#ff0000"
    assert pixel(canvas, 370, 140) == "#ff0000"
    # the filled circle at (300, 300), radius 40, default (black) fill
    assert pixel(canvas, 300, 300) == "#000000"
    assert pixel(canvas, 300, 200) == "#ffffff"
