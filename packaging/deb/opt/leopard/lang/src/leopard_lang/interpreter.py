"""Tree-walking evaluator over the AST (GRAMMAR.md §3-§6, §12).

Two Python-exception-based signals carry `break`/`continue` out of a loop body and
`return` out of a function body; both are always caught within the same function
(`_exec_While`/`_exec_For`, `_call_function`) so they never escape as real errors.
`break`/`continue`/`return` used outside a loop/function are instead caught directly
via a depth counter and raised as an ordinary LeopardRuntimeError at that point.

Zero GUI dependency by default (Phases 0-3) — `gui_properties`/`gui_builtins`/`gui_methods`
are optional plugin points the GUI runtime (Phase 4+, `gui/app_host.py`) fills in so this
module never has to `import PyQt6` itself. `gui_properties` handles `.property`
get/set for anything that isn't a plain list (e.g. a QWidget); `gui_builtins` is an
extra name->callable dict checked before a name is treated as GUI-only-and-unimplemented.
`gui_methods` (Phase 13) handles `receiver.method(args)` calls for anything that isn't a
plain list (e.g. a turtle-graphics canvas control) — the same shape as `gui_properties`,
just for calls instead of property get/set.
"""

from __future__ import annotations

from typing import Any, Optional

from . import ast_nodes as ast
from . import builtins_core
from . import builtins_files
from .environment import Environment
from .errors import LeopardRuntimeError, describe_type

# Reserved words that name GUI-only builtins (Phase 4+ implements these) — calling
# them from a bare (no-window) script gets a clear "not yet" error rather than a
# confusing "undefined" one. Turtle commands aren't listed here (Phase 13): they're
# never bare identifiers anymore, only methods on a declared `graphics` control
# (`canvas1.go(...)`), so they fall through `_eval_Call`'s `gui_methods` branch instead.
_GUI_ONLY_NAMES = {
    "notice", "confirm", "ask", "beep",
    "open_file_dialog", "save_file_dialog", "color_dialog", "font_dialog",
    "set_cursor", "close_window", "maximize_window", "minimize_window",
    "play_sound", "stop_sound", "play_music", "stop_music", "pause_music",
}


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class Interpreter:
    def __init__(
        self,
        gui_properties: Any = None,
        gui_builtins: Optional[dict] = None,
        gui_methods: Any = None,
    ):
        self.globals = Environment()
        self.functions: dict[str, ast.FunctionDecl] = {}
        self._loop_depth = 0
        self.gui_properties = gui_properties
        self.gui_builtins: dict = gui_builtins or {}
        self.gui_methods = gui_methods

    def run(self, program: ast.Program) -> None:
        if program.window is not None:
            raise LeopardRuntimeError(
                program.window.line,
                "this program declares a window, which needs the GUI runtime (not available yet)",
            )
        for stmt in program.body:
            if isinstance(stmt, ast.FunctionDecl):
                self.functions[stmt.name] = stmt
        for stmt in program.body:
            if isinstance(stmt, ast.FunctionDecl):
                continue
            self._exec(stmt, self.globals)

    # -- statement execution --------------------------------------------------

    def _exec_block(self, stmts: list[ast.Stmt], env: Environment) -> None:
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec(self, stmt: ast.Stmt, env: Environment) -> None:
        method = getattr(self, f"_exec_{type(stmt).__name__}", None)
        if method is None:
            raise LeopardRuntimeError(
                getattr(stmt, "line", 0), f"cannot execute {type(stmt).__name__} yet"
            )
        method(stmt, env)

    def _exec_Assignment(self, stmt: ast.Assignment, env: Environment) -> None:
        env.set(stmt.target, self._eval(stmt.value, env))

    def _exec_PropertyAssignment(self, stmt: ast.PropertyAssignment, env: Environment) -> None:
        target = stmt.target
        if isinstance(target, ast.Index):
            obj = self._eval(target.obj, env)
            index = self._eval(target.index, env)
            if not isinstance(obj, list):
                raise LeopardRuntimeError(
                    target.line, f"cannot index into {describe_type(obj)} — only lists support [ ]"
                )
            if isinstance(index, bool) or not isinstance(index, int):
                raise LeopardRuntimeError(target.line, "a list index must be a whole number")
            if index < 1 or index > len(obj):
                plural = "item" if len(obj) == 1 else "items"
                raise LeopardRuntimeError(
                    target.line, f"list index {index} is out of range (list has {len(obj)} {plural})"
                )
            obj[index - 1] = self._eval(stmt.value, env)
            return
        if self.gui_properties is not None and isinstance(target, ast.PropertyAccess):
            obj = self._eval(target.obj, env)
            if self.gui_properties.is_gui_object(obj):
                value = self._eval(stmt.value, env)
                self.gui_properties.set(obj, target.name, value, stmt.line)
                return
        raise LeopardRuntimeError(stmt.line, "property assignment needs a GUI control (not available yet)")

    def _exec_If(self, stmt: ast.If, env: Environment) -> None:
        if self._require_bool(self._eval(stmt.condition, env), stmt.line, "a condition"):
            self._exec_block(stmt.then_body, env)
            return
        for cond, body in stmt.elseif_clauses:
            if self._require_bool(self._eval(cond, env), stmt.line, "a condition"):
                self._exec_block(body, env)
                return
        if stmt.else_body is not None:
            self._exec_block(stmt.else_body, env)

    def _exec_While(self, stmt: ast.While, env: Environment) -> None:
        self._loop_depth += 1
        try:
            while self._require_bool(self._eval(stmt.condition, env), stmt.line, "a condition"):
                try:
                    self._exec_block(stmt.body, env)
                except _ContinueSignal:
                    continue
                except _BreakSignal:
                    break
        finally:
            self._loop_depth -= 1

    def _exec_For(self, stmt: ast.For, env: Environment) -> None:
        start = self._require_number(self._eval(stmt.start, env), stmt.line, "the 'for' loop's start value")
        end = self._require_number(self._eval(stmt.end, env), stmt.line, "the 'for' loop's end value")
        step = (
            self._require_number(self._eval(stmt.step, env), stmt.line, "the 'for' loop's step value")
            if stmt.step is not None
            else 1
        )
        if step == 0:
            raise LeopardRuntimeError(stmt.line, "a 'for' loop's step cannot be 0")

        self._loop_depth += 1
        try:
            i = start
            while (i <= end) if step > 0 else (i >= end):
                env.set(stmt.var, i)
                try:
                    self._exec_block(stmt.body, env)
                except _ContinueSignal:
                    pass
                except _BreakSignal:
                    break
                i += step
        finally:
            self._loop_depth -= 1

    def _exec_Break(self, stmt: ast.Break, env: Environment) -> None:
        if self._loop_depth == 0:
            raise LeopardRuntimeError(stmt.line, "'break' used outside a loop")
        raise _BreakSignal()

    def _exec_Continue(self, stmt: ast.Continue, env: Environment) -> None:
        if self._loop_depth == 0:
            raise LeopardRuntimeError(stmt.line, "'continue' used outside a loop")
        raise _ContinueSignal()

    def _exec_Return(self, stmt: ast.Return, env: Environment) -> None:
        value = self._eval(stmt.value, env) if stmt.value is not None else None
        raise _ReturnSignal(value)

    def _exec_FunctionDecl(self, stmt: ast.FunctionDecl, env: Environment) -> None:
        pass  # already hoisted in run()

    def _exec_ExprStatement(self, stmt: ast.ExprStatement, env: Environment) -> None:
        self._eval(stmt.expr, env)

    def _exec_ControlDecl(self, stmt: ast.ControlDecl, env: Environment) -> None:
        raise LeopardRuntimeError(stmt.line, "control declarations need a window (not available yet)")

    def _exec_MenuDecl(self, stmt: ast.MenuDecl, env: Environment) -> None:
        raise LeopardRuntimeError(stmt.line, "menus need a window (not available yet)")

    def _exec_EventHandler(self, stmt: ast.EventHandler, env: Environment) -> None:
        raise LeopardRuntimeError(stmt.line, "event handlers need a window (not available yet)")

    # -- expression evaluation --------------------------------------------------

    def _eval(self, expr: ast.Expr, env: Environment) -> Any:
        return getattr(self, f"_eval_{type(expr).__name__}")(expr, env)

    def _eval_Literal(self, expr: ast.Literal, env: Environment) -> Any:
        return expr.value

    def _eval_Identifier(self, expr: ast.Identifier, env: Environment) -> Any:
        return env.get(expr.name, expr.line)

    def _eval_ListLiteral(self, expr: ast.ListLiteral, env: Environment) -> list:
        return [self._eval(e, env) for e in expr.elements]

    def _eval_UnaryOp(self, expr: ast.UnaryOp, env: Environment) -> Any:
        if expr.op == "-":
            return -self._require_number(self._eval(expr.operand, env), expr.line, "the '-' operator")
        if expr.op == "not":
            return not self._require_bool(self._eval(expr.operand, env), expr.line, "'not'")
        raise LeopardRuntimeError(expr.line, f"unknown unary operator '{expr.op}'")

    def _eval_BinaryOp(self, expr: ast.BinaryOp, env: Environment) -> Any:
        op = expr.op

        if op == "and":
            if not self._require_bool(self._eval(expr.left, env), expr.line, "'and'"):
                return False
            return self._require_bool(self._eval(expr.right, env), expr.line, "'and'")
        if op == "or":
            if self._require_bool(self._eval(expr.left, env), expr.line, "'or'"):
                return True
            return self._require_bool(self._eval(expr.right, env), expr.line, "'or'")

        left = self._eval(expr.left, env)
        right = self._eval(expr.right, env)

        if op == "&":
            if not isinstance(left, str):
                raise LeopardRuntimeError(
                    expr.line, f"cannot '&' {describe_type(left)} — use str() to convert it first"
                )
            if not isinstance(right, str):
                raise LeopardRuntimeError(
                    expr.line, f"cannot '&' {describe_type(right)} — use str() to convert it first"
                )
            return left + right

        if op == "+":
            if isinstance(left, str) and isinstance(right, str):
                raise LeopardRuntimeError(expr.line, "cannot use '+' on two strings — use '&' to join text")
            l = self._require_number(left, expr.line, "'+'")
            r = self._require_number(right, expr.line, "'+'")
            return l + r

        if op in ("-", "*", "/", "%", "^"):
            l = self._require_number(left, expr.line, f"'{op}'")
            r = self._require_number(right, expr.line, f"'{op}'")
            if op == "-":
                return l - r
            if op == "*":
                return l * r
            if op == "/":
                if r == 0:
                    raise LeopardRuntimeError(expr.line, "division by zero")
                return l / r
            if op == "%":
                if r == 0:
                    raise LeopardRuntimeError(expr.line, "division by zero")
                return l % r
            return l**r  # '^'

        if op == "=":
            return self._values_equal(left, right)
        if op == "<>":
            return not self._values_equal(left, right)
        if op in ("<", ">", "<=", ">="):
            l = self._require_number(left, expr.line, f"'{op}'")
            r = self._require_number(right, expr.line, f"'{op}'")
            if op == "<":
                return l < r
            if op == ">":
                return l > r
            if op == "<=":
                return l <= r
            return l >= r  # '>='

        raise LeopardRuntimeError(expr.line, f"unknown operator '{op}'")

    def _eval_Index(self, expr: ast.Index, env: Environment) -> Any:
        obj = self._eval(expr.obj, env)
        index = self._eval(expr.index, env)
        if isinstance(obj, str):
            if isinstance(index, bool) or not isinstance(index, int):
                raise LeopardRuntimeError(expr.line, "a string index must be a whole number")
            if index < 1 or index > len(obj):
                plural = "character" if len(obj) == 1 else "characters"
                raise LeopardRuntimeError(
                    expr.line, f"string index {index} is out of range (string has {len(obj)} {plural})"
                )
            return obj[index - 1]
        if not isinstance(obj, list):
            raise LeopardRuntimeError(
                expr.line, f"cannot index into {describe_type(obj)} — only lists and strings support [ ]"
            )
        if isinstance(index, bool) or not isinstance(index, int):
            raise LeopardRuntimeError(expr.line, "a list index must be a whole number")
        if index < 1 or index > len(obj):
            plural = "item" if len(obj) == 1 else "items"
            raise LeopardRuntimeError(
                expr.line, f"list index {index} is out of range (list has {len(obj)} {plural})"
            )
        return obj[index - 1]

    def _eval_PropertyAccess(self, expr: ast.PropertyAccess, env: Environment) -> Any:
        obj = self._eval(expr.obj, env)
        if isinstance(obj, (list, str)) and expr.name == "length":
            return len(obj)
        if self.gui_properties is not None and self.gui_properties.is_gui_object(obj):
            return self.gui_properties.get(obj, expr.name, expr.line)
        raise LeopardRuntimeError(expr.line, f"'.{expr.name}' needs a GUI control (not available yet)")

    def _eval_Call(self, expr: ast.Call, env: Environment) -> Any:
        if isinstance(expr.callee, ast.PropertyAccess) and expr.callee.name == "add":
            obj = self._eval(expr.callee.obj, env)
            if not isinstance(obj, list):
                raise LeopardRuntimeError(expr.line, f"'.add()' needs a list, not {describe_type(obj)}")
            if len(expr.args) != 1:
                raise LeopardRuntimeError(expr.line, "'.add()' takes exactly one argument")
            obj.append(self._eval(expr.args[0], env))
            return None

        if isinstance(expr.callee, ast.PropertyAccess):
            obj = self._eval(expr.callee.obj, env)
            if self.gui_methods is not None and self.gui_methods.is_gui_object(obj):
                args = [self._eval(a, env) for a in expr.args]
                return self.gui_methods.call(obj, expr.callee.name, args, expr.line)
            raise LeopardRuntimeError(
                expr.line, f"'.{expr.callee.name}()' needs a GUI control (not available yet)"
            )

        if not isinstance(expr.callee, ast.Identifier):
            raise LeopardRuntimeError(expr.line, "this value is not something that can be called")

        name = expr.callee.name
        args = [self._eval(a, env) for a in expr.args]

        if name in self.functions:
            return self._call_function(self.functions[name], args, expr.line)
        if name in self.gui_builtins:
            return self._call_builtin(self.gui_builtins[name], name, args, expr.line)
        if name in builtins_core.BUILTINS:
            return self._call_builtin(builtins_core.BUILTINS[name], name, args, expr.line)
        if name in builtins_files.BUILTINS:
            return self._call_builtin(builtins_files.BUILTINS[name], name, args, expr.line)
        if name in _GUI_ONLY_NAMES:
            raise LeopardRuntimeError(expr.line, f"'{name}' needs a window (not available yet)")
        if env.has(name):
            raise LeopardRuntimeError(expr.line, f"'{name}' is a variable, not a function")
        raise LeopardRuntimeError(expr.line, f"'{name}' is not defined")

    def _call_function(self, decl: ast.FunctionDecl, args: list, line: int) -> Any:
        if len(args) != len(decl.params):
            plural = "argument" if len(decl.params) == 1 else "arguments"
            raise LeopardRuntimeError(
                line, f"'{decl.name}' expects {len(decl.params)} {plural}, got {len(args)}"
            )
        call_env = Environment(parent=self.globals)
        for param, value in zip(decl.params, args):
            call_env.set(param, value)
        try:
            self._exec_block(decl.body, call_env)
        except _ReturnSignal as ret:
            return ret.value
        return None

    def _call_builtin(self, fn, name: str, args: list, line: int) -> Any:
        try:
            return fn(*args)
        except LeopardRuntimeError:
            raise
        except TypeError as exc:
            if "positional argument" in str(exc) or "argument" in str(exc):
                raise LeopardRuntimeError(line, f"'{name}()' called with the wrong number of arguments") from exc
            raise LeopardRuntimeError(line, str(exc)) from exc
        except (ValueError, OSError) as exc:
            raise LeopardRuntimeError(line, str(exc)) from exc

    # -- helpers ------------------------------------------------------------

    def _require_bool(self, value: Any, line: int, where: str) -> bool:
        if not isinstance(value, bool):
            raise LeopardRuntimeError(line, f"{where} must be true/false, not {describe_type(value)}")
        return value

    def _require_number(self, value: Any, line: int, where: str) -> Any:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise LeopardRuntimeError(line, f"{where} needs a number, not {describe_type(value)}")
        return value

    def _values_equal(self, left: Any, right: Any) -> bool:
        if isinstance(left, bool) != isinstance(right, bool):
            return False
        left_is_num = isinstance(left, (int, float)) and not isinstance(left, bool)
        right_is_num = isinstance(right, (int, float)) and not isinstance(right, bool)
        if left_is_num and right_is_num:
            return left == right
        return type(left) is type(right) and left == right


def interpret(program: ast.Program) -> None:
    Interpreter().run(program)
