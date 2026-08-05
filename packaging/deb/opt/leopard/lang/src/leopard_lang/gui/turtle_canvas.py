"""Turtle graphics canvas + every §10 command (GRAMMAR.md §10, a `graphics` control).

GRAMMAR.md only says these commands are "carried over unchanged in name and meaning"
from the original `leopard.bas`, which itself just forwarded each one, verbatim and
unparsed, straight through to Liberty BASIC's native graphics-window turtle engine —
so the exact pixel semantics below are a best-effort, documented recreation of that
engine's conventions, not something GRAMMAR.md (or the original source) spells out
directly. See IMPLEMENTATION_PLAN.md's Phase 6 decisions-log entry for the specifics
(heading convention, what `box`/`ellipse` measure from, pen state defaults, etc.).

Drawing happens directly onto a persistent `QPixmap` buffer (each command paints onto
it immediately); `paintEvent` just blits that buffer, so nothing needs to be replayed.

`polygon`/`polygonfilled` (Phase 15) are not from the original `leopard.bas` — a genuine
vocabulary addition, not a recreation. See IMPLEMENTATION_PLAN.md's Phase 15 entry.

Mouse tracking (Phase 16) is likewise new, not a recreation: `mouse_x`/`mouse_y` plus the
`mouseMoved` signal back a `.mouse_x`/`.mouse_y` read-only property pair and an `on mousemove`
event (GRAMMAR.md §9/§10) — the original had no mouse support of any kind.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen, QPixmap, QPolygonF
from PyQt6.QtWidgets import QWidget


def _parse_color(name: str) -> QColor:
    if not isinstance(name, str):
        raise TypeError(f"expected a color name, not {name!r}")
    color = QColor(name)
    if not color.isValid():
        raise ValueError(f"'{name}' is not a recognized color")
    return color


def _require_number(value, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{where} needs a number")
    return value


class TurtleCanvas(QWidget):
    """Turtle state: position, heading (0 = north, clockwise), pen up/down/color/size,
    fill color, font. Heading 0 points up (-y); turning clockwise increases heading."""

    mouseMoved = pyqtSignal()

    def __init__(self, width: int, height: int, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._pixmap = QPixmap(width, height)
        self._pixmap.fill(QColor("white"))

        self.x = width / 2
        self.y = height / 2
        self.heading = 0.0
        self.pen_is_down = False
        self.pen_color = QColor("black")
        self.pen_size = 1
        self.fill_color = QColor("black")
        self.font = QFont()

        self.mouse_x = 0
        self.mouse_y = 0
        self.setMouseTracking(True)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 (Qt's naming)
        QPainter(self).drawPixmap(0, 0, self._pixmap)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt's naming)
        pos = event.position()
        self.mouse_x = int(pos.x())
        self.mouse_y = int(pos.y())
        self.mouseMoved.emit()
        super().mouseMoveEvent(event)

    def _painter(self) -> QPainter:
        painter = QPainter(self._pixmap)
        pen = QPen(self.pen_color)
        pen.setWidth(self.pen_size)
        painter.setPen(pen)
        painter.setBrush(self.fill_color)
        painter.setFont(self.font)
        return painter

    def _finish(self, painter: QPainter) -> None:
        painter.end()
        self.update()

    def _move_to(self, new_x: float, new_y: float, draw: bool) -> None:
        if draw:
            painter = self._painter()
            painter.drawLine(QPointF(self.x, self.y), QPointF(new_x, new_y))
            self._finish(painter)
        self.x = new_x
        self.y = new_y

    # -- §10 commands ---------------------------------------------------------

    def up(self) -> None:
        self.pen_is_down = False

    def down(self) -> None:
        self.pen_is_down = True

    def home(self) -> None:
        self.x = self.width() / 2
        self.y = self.height() / 2
        self.heading = 0.0

    def go(self, distance) -> None:
        distance = _require_number(distance, "go")
        radians = math.radians(self.heading)
        self._move_to(
            self.x + distance * math.sin(radians),
            self.y - distance * math.cos(radians),
            draw=self.pen_is_down,
        )

    def goto(self, x, y) -> None:
        x, y = _require_number(x, "goto"), _require_number(y, "goto")
        self._move_to(x, y, draw=self.pen_is_down)

    def place(self, x, y) -> None:
        x, y = _require_number(x, "place"), _require_number(y, "place")
        self._move_to(x, y, draw=False)

    def turn(self, degrees) -> None:
        degrees = _require_number(degrees, "turn")
        self.heading = (self.heading + degrees) % 360

    def north(self) -> None:
        self.heading = 0.0

    def fill(self, color: str) -> None:
        self.fill_color = _parse_color(color)

    def pen(self, color: str) -> None:
        self.pen_color = _parse_color(color)

    def size(self, pixels) -> None:
        pixels = _require_number(pixels, "size")
        self.pen_size = max(0, int(pixels))

    def font_(self, family: str, point_size=None) -> None:
        if not isinstance(family, str):
            raise TypeError("font needs a font name")
        self.font = QFont(family, int(point_size)) if point_size is not None else QFont(family)

    def text(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("text needs a string")
        painter = self._painter()
        painter.drawText(QPointF(self.x, self.y), message)
        self._finish(painter)

    def backcolor(self, color: str) -> None:
        self._pixmap.fill(_parse_color(color))
        self.update()

    def box(self, w, h) -> None:
        w, h = _require_number(w, "box"), _require_number(h, "box")
        painter = self._painter()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(self.x, self.y, w, h))
        self._finish(painter)

    def boxfilled(self, w, h) -> None:
        w, h = _require_number(w, "boxfilled"), _require_number(h, "boxfilled")
        painter = self._painter()
        painter.drawRect(QRectF(self.x, self.y, w, h))
        self._finish(painter)

    def circle(self, radius) -> None:
        radius = _require_number(radius, "circle")
        painter = self._painter()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(self.x, self.y), radius, radius)
        self._finish(painter)

    def circlefilled(self, radius) -> None:
        radius = _require_number(radius, "circlefilled")
        painter = self._painter()
        painter.drawEllipse(QPointF(self.x, self.y), radius, radius)
        self._finish(painter)

    def ellipse(self, w, h) -> None:
        w, h = _require_number(w, "ellipse"), _require_number(h, "ellipse")
        painter = self._painter()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(self.x, self.y), w / 2, h / 2)
        self._finish(painter)

    def ellipsefilled(self, w, h) -> None:
        w, h = _require_number(w, "ellipsefilled"), _require_number(h, "ellipsefilled")
        painter = self._painter()
        painter.drawEllipse(QPointF(self.x, self.y), w / 2, h / 2)
        self._finish(painter)

    def _polygon_vertices(self, sides: int, radius: float) -> QPolygonF:
        points = []
        for i in range(sides):
            angle = math.radians(self.heading + i * (360.0 / sides))
            points.append(QPointF(self.x + radius * math.sin(angle), self.y - radius * math.cos(angle)))
        return QPolygonF(points)

    def polygon(self, sides, radius) -> None:
        sides, radius = int(_require_number(sides, "polygon")), _require_number(radius, "polygon")
        if sides < 3:
            raise ValueError("polygon needs at least 3 sides")
        painter = self._painter()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(self._polygon_vertices(sides, radius))
        self._finish(painter)

    def polygonfilled(self, sides, radius) -> None:
        sides, radius = int(_require_number(sides, "polygonfilled")), _require_number(radius, "polygonfilled")
        if sides < 3:
            raise ValueError("polygonfilled needs at least 3 sides")
        painter = self._painter()
        painter.drawPolygon(self._polygon_vertices(sides, radius))
        self._finish(painter)

    def drawbmp(self, path: str, x, y) -> None:
        if not isinstance(path, str):
            raise TypeError("drawbmp needs a file path")
        x, y = _require_number(x, "drawbmp"), _require_number(y, "drawbmp")
        image = QPixmap(path)
        if image.isNull():
            raise ValueError(f"'{path}' could not be loaded as an image")
        painter = QPainter(self._pixmap)
        painter.drawPixmap(int(x), int(y), image)
        self._finish(painter)


def build_turtle_builtins(canvas: TurtleCanvas) -> dict:
    return {
        "up": canvas.up,
        "down": canvas.down,
        "home": canvas.home,
        "go": canvas.go,
        "goto": canvas.goto,
        "place": canvas.place,
        "turn": canvas.turn,
        "north": canvas.north,
        "fill": canvas.fill,
        "pen": canvas.pen,
        "size": canvas.size,
        "font": canvas.font_,
        "text": canvas.text,
        "backcolor": canvas.backcolor,
        "box": canvas.box,
        "boxfilled": canvas.boxfilled,
        "circle": canvas.circle,
        "circlefilled": canvas.circlefilled,
        "ellipse": canvas.ellipse,
        "ellipsefilled": canvas.ellipsefilled,
        "polygon": canvas.polygon,
        "polygonfilled": canvas.polygonfilled,
        "drawbmp": canvas.drawbmp,
    }
