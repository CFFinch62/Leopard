"""AST node dataclasses produced by parser.py from a Token stream.

Every node carries the source `line` it started on, so Phase 3's runtime errors can
report line numbers the same way Phase 1/2's syntax errors do (GRAMMAR.md status #8).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


class Stmt:
    """Marker base class for statement nodes."""


class Expr:
    """Marker base class for expression nodes."""


# ---------------------------------------------------------------------------
# Program / window shape (GRAMMAR.md §2)
# ---------------------------------------------------------------------------


@dataclass
class WindowDecl:
    title: str
    width: object
    height: object
    body: list[Stmt]
    line: int


@dataclass
class Program:
    window: Optional[WindowDecl]
    body: list[Stmt]  # populated only for bare (no-window) scripts


# ---------------------------------------------------------------------------
# Controls (GRAMMAR.md §7)
# ---------------------------------------------------------------------------


@dataclass
class ControlDecl(Stmt):
    kind: str  # e.g. "button", "textbox", "graphics", ...
    caption: Optional[str]
    name: str
    x: Expr
    y: Expr
    w: Expr
    h: Expr
    line: int


# ---------------------------------------------------------------------------
# Menus (GRAMMAR.md §8)
# ---------------------------------------------------------------------------

MenuItem = Union["ItemDecl", "CheckItemDecl", "SubmenuDecl", "Separator"]


@dataclass
class ItemDecl(Stmt):
    title: str
    name: str
    line: int


@dataclass
class CheckItemDecl(Stmt):
    title: str
    name: str
    line: int


@dataclass
class SubmenuDecl(Stmt):
    title: str
    name: str
    body: list[MenuItem]
    line: int


@dataclass
class Separator(Stmt):
    line: int


@dataclass
class MenuDecl(Stmt):
    title: str
    name: str
    body: list[MenuItem]
    line: int


# ---------------------------------------------------------------------------
# Events (GRAMMAR.md §9)
# ---------------------------------------------------------------------------


@dataclass
class EventHandler(Stmt):
    event: str  # "click" | "change" | "select" | "close" | "mousemove"
    target: Optional[str]  # None for window-level `on close:`
    body: list[Stmt]
    line: int


# ---------------------------------------------------------------------------
# Functions (GRAMMAR.md §6)
# ---------------------------------------------------------------------------


@dataclass
class FunctionDecl(Stmt):
    name: str
    params: list[str]
    body: list[Stmt]
    line: int


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------


@dataclass
class Assignment(Stmt):
    target: str  # a plain variable name
    value: Expr
    line: int


@dataclass
class PropertyAssignment(Stmt):
    target: Expr  # a PropertyAccess or Index expression
    value: Expr
    line: int


# ---------------------------------------------------------------------------
# Control flow (GRAMMAR.md §5)
# ---------------------------------------------------------------------------


@dataclass
class If(Stmt):
    condition: Expr
    then_body: list[Stmt]
    elseif_clauses: list[tuple[Expr, list[Stmt]]]
    else_body: Optional[list[Stmt]]
    line: int


@dataclass
class While(Stmt):
    condition: Expr
    body: list[Stmt]
    line: int


@dataclass
class For(Stmt):
    var: str
    start: Expr
    end: Expr
    step: Optional[Expr]
    body: list[Stmt]
    line: int


@dataclass
class Break(Stmt):
    line: int


@dataclass
class Continue(Stmt):
    line: int


@dataclass
class Return(Stmt):
    value: Optional[Expr]
    line: int


@dataclass
class ExprStatement(Stmt):
    expr: Expr
    line: int


# ---------------------------------------------------------------------------
# Expressions (GRAMMAR.md §4)
# ---------------------------------------------------------------------------


@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str
    right: Expr
    line: int


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr
    line: int


@dataclass
class Call(Expr):
    callee: Expr
    args: list[Expr]
    line: int


@dataclass
class Identifier(Expr):
    name: str
    line: int


@dataclass
class Literal(Expr):
    value: object
    line: int


@dataclass
class ListLiteral(Expr):
    elements: list[Expr]
    line: int


@dataclass
class Index(Expr):
    obj: Expr
    index: Expr
    line: int


@dataclass
class PropertyAccess(Expr):
    obj: Expr
    name: str
    line: int
