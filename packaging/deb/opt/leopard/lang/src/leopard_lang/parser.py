"""Token stream -> AST. Recursive-descent, precedence climbing for expressions.

Reserved-word keywords that name builtins (GRAMMAR.md §12) are valid in expression
position exactly like an identifier (e.g. `notice "hi"`, `str(score)`); see
EXPRESSION_KEYWORDS below. A bare identifier followed directly by another expression
with no operator between them (e.g. `notice "hi"`) is a no-parens "command" call —
see _simple_statement. Turtle commands (§10) are deliberately NOT in this set — since
Phase 13 they're only reachable as `canvasName.command(args)`, a dotted method call on
a declared `graphics` control, never as a bare statement — `_postfix_expr`'s dot/paren
handling (below) already parses that generically for any receiver, keyword or not.
"""

from __future__ import annotations

from . import ast_nodes as ast
from .errors import LeopardSyntaxError
from .tokens import Token, TokenType

CONTROL_DECL_TYPES = {
    TokenType.TEXTBOX,
    TokenType.TEXTEDIT,
    TokenType.LABEL,
    TokenType.BUTTON,
    TokenType.BMPBUTTON,
    TokenType.LISTBOX,
    TokenType.COMBOBOX,
    TokenType.RADIOBUTTON,
    TokenType.CHECKBOX,
    TokenType.GROUPBOX,
    TokenType.GRAPHICS,
}

_BUILTINS = {
    TokenType.STR,
    TokenType.NUM,
    TokenType.SPLIT,
    TokenType.JOIN,
    TokenType.PRINT,
    TokenType.NOTICE,
    TokenType.CONFIRM,
    TokenType.ASK,
    TokenType.BEEP,
    TokenType.DATE,
    TokenType.TIME,
    TokenType.WRITE_FILE,
    TokenType.APPEND_FILE,
    TokenType.READ_FILE,
    TokenType.DELETE_FILE,
    TokenType.MAKE_DIR,
    TokenType.REMOVE_DIR,
    TokenType.FILE_EXISTS,
    TokenType.OPEN_FILE_DIALOG,
    TokenType.SAVE_FILE_DIALOG,
    TokenType.COLOR_DIALOG,
    TokenType.FONT_DIALOG,
    TokenType.OPEN_URL,
    TokenType.OPEN_EMAIL,
    TokenType.RUN_PROGRAM,
    TokenType.ASCII,
    TokenType.SET_CURSOR,
    TokenType.CLOSE_WINDOW,
    TokenType.MAXIMIZE_WINDOW,
    TokenType.MINIMIZE_WINDOW,
    TokenType.PLAY_SOUND,
    TokenType.STOP_SOUND,
    TokenType.PLAY_MUSIC,
    TokenType.STOP_MUSIC,
    TokenType.PAUSE_MUSIC,
    TokenType.DOWNLOAD_FILE,
}

# Reserved words valid in expression position, resolving like a plain identifier.
# `window` is here because §12 shows `window.title = "..."` as a property access,
# which requires `window` to resolve as an identifier referring to the current window
# — flagged in GRAMMAR.md's §15 open questions (see IMPLEMENTATION_PLAN.md's Phase 4
# decisions-log entry). Turtle command words are deliberately excluded (Phase 13):
# they're only ever meaningful as a method name after a dot (`canvas1.go(...)`), which
# `_postfix_expr` already handles without consulting this set at all.
EXPRESSION_KEYWORDS = _BUILTINS | {TokenType.WINDOW}

_EXPRESSION_START_TYPES = {
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.TRUE,
    TokenType.FALSE,
    TokenType.IDENTIFIER,
    TokenType.LPAREN,
    TokenType.LBRACKET,
    TokenType.MINUS,
    TokenType.NOT,
} | EXPRESSION_KEYWORDS

_COMPARISON_OPS = {
    TokenType.EQ: "=",
    TokenType.EQ_WORD: "=",  # `eq` — same operator as `=`, just a word spelling (GRAMMAR.md §4)
    TokenType.NEQ: "<>",
    TokenType.LT: "<",
    TokenType.GT: ">",
    TokenType.LE: "<=",
    TokenType.GE: ">=",
}
_ADDITIVE_OPS = {TokenType.PLUS: "+", TokenType.MINUS: "-"}
_MULTIPLICATIVE_OPS = {TokenType.STAR: "*", TokenType.SLASH: "/", TokenType.PERCENT: "%"}

_EVENT_KEYWORDS = {
    TokenType.CLICK: "click",
    TokenType.CHANGE: "change",
    TokenType.SELECT: "select",
    TokenType.CLOSE: "close",
    TokenType.MOUSEMOVE: "mousemove",
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # -- token stream helpers -------------------------------------------------

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _peek_next(self) -> Token:
        nxt = self.pos + 1
        return self.tokens[nxt] if nxt < len(self.tokens) else self.tokens[-1]

    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type is not TokenType.EOF:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, message: str) -> Token:
        if not self._check(token_type):
            raise LeopardSyntaxError(self._peek().line, message)
        return self._advance()

    # -- program shape (GRAMMAR.md §2) ---------------------------------------

    def parse_program(self) -> ast.Program:
        window = self._parse_window_header_if_present()
        if window is not None:
            self._skip_blank_newlines()
            self._expect(TokenType.EOF, "expected end of file after the program's window block")
            return ast.Program(window=window, body=[])

        body = self._parse_statements_until(TokenType.EOF)
        return ast.Program(window=None, body=body)

    def _parse_window_header_if_present(self) -> ast.WindowDecl | None:
        line = self._peek().line
        if not self._check(TokenType.WINDOW):
            return None
        self._advance()

        title_tok = self._expect(TokenType.STRING, "expected a quoted window title")
        self._expect(TokenType.COMMA, "expected ',' after window title")
        width_tok = self._expect(TokenType.NUMBER, "expected a width after window title")
        self._expect(TokenType.COMMA, "expected ',' after window width")
        height_tok = self._expect(TokenType.NUMBER, "expected a height after window width")
        body = self._parse_block("the window header")
        return ast.WindowDecl(
            title=title_tok.value, width=width_tok.value, height=height_tok.value,
            body=body, line=line,
        )

    # -- blocks & statement sequences ----------------------------------------

    def _parse_block(self, context: str) -> list[ast.Stmt]:
        self._expect(TokenType.COLON, f"expected ':' after {context}")
        self._expect(TokenType.NEWLINE, f"expected a new line after ':' in {context}")
        self._skip_blank_newlines()
        self._expect(TokenType.INDENT, f"expected an indented block after {context}")
        stmts = self._parse_statements_until(TokenType.DEDENT)
        self._expect(TokenType.DEDENT, f"expected the indented block in {context} to end")
        return stmts

    def _parse_statements_until(self, end_type: TokenType) -> list[ast.Stmt]:
        stmts: list[ast.Stmt] = []
        self._skip_blank_newlines()
        while not self._check(end_type):
            stmts.append(self._statement())
            self._skip_blank_newlines()
        return stmts

    def _skip_blank_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    # -- statement dispatch ---------------------------------------------------

    def _statement(self) -> ast.Stmt:
        if self._check(TokenType.IF):
            return self._if_statement()
        if self._check(TokenType.WHILE):
            return self._while_statement()
        if self._check(TokenType.FOR):
            return self._for_statement()
        if self._check(TokenType.BREAK):
            line = self._advance().line
            self._expect(TokenType.NEWLINE, "expected a new line after 'break'")
            return ast.Break(line=line)
        if self._check(TokenType.CONTINUE):
            line = self._advance().line
            self._expect(TokenType.NEWLINE, "expected a new line after 'continue'")
            return ast.Continue(line=line)
        if self._check(TokenType.RETURN):
            return self._return_statement()
        if self._check(TokenType.FUNCTION):
            return self._function_decl()
        if self._check(TokenType.MENU):
            return self._menu_decl()
        if self._check(TokenType.ON):
            return self._event_handler()
        if self._check(*CONTROL_DECL_TYPES):
            return self._control_decl()

        return self._simple_statement()

    # -- control flow (GRAMMAR.md §5) -----------------------------------------

    def _if_statement(self) -> ast.If:
        line = self._advance().line  # 'if'
        condition = self._expr()
        then_body = self._parse_block("'if' condition")

        elseif_clauses: list[tuple[ast.Expr, list[ast.Stmt]]] = []
        while self._check(TokenType.ELSEIF):
            self._advance()
            elseif_cond = self._expr()
            elseif_body = self._parse_block("'elseif' condition")
            elseif_clauses.append((elseif_cond, elseif_body))

        else_body = None
        if self._match(TokenType.ELSE):
            else_body = self._parse_block("'else'")

        return ast.If(
            condition=condition, then_body=then_body, elseif_clauses=elseif_clauses,
            else_body=else_body, line=line,
        )

    def _while_statement(self) -> ast.While:
        line = self._advance().line  # 'while'
        condition = self._expr()
        body = self._parse_block("'while' condition")
        return ast.While(condition=condition, body=body, line=line)

    def _for_statement(self) -> ast.For:
        line = self._advance().line  # 'for'
        var_tok = self._expect(TokenType.IDENTIFIER, "expected a loop variable name after 'for'")
        self._expect(TokenType.EQ, "expected '=' after the 'for' loop variable")
        start = self._expr()
        self._expect(TokenType.TO, "expected 'to' after the 'for' loop's starting value")
        end = self._expr()
        step = None
        if self._match(TokenType.STEP):
            step = self._expr()
        body = self._parse_block("the 'for' loop header")
        return ast.For(var=var_tok.lexeme, start=start, end=end, step=step, body=body, line=line)

    def _return_statement(self) -> ast.Return:
        line = self._advance().line  # 'return'
        value = None
        if not self._check(TokenType.NEWLINE):
            value = self._expr()
        self._expect(TokenType.NEWLINE, "expected a new line after 'return'")
        return ast.Return(value=value, line=line)

    # -- functions (GRAMMAR.md §6) ---------------------------------------------

    def _function_decl(self) -> ast.FunctionDecl:
        line = self._advance().line  # 'function'
        name_tok = self._expect(TokenType.IDENTIFIER, "expected a function name after 'function'")
        self._expect(TokenType.LPAREN, "expected '(' after the function name")
        params: list[str] = []
        if not self._check(TokenType.RPAREN):
            params.append(self._expect(TokenType.IDENTIFIER, "expected a parameter name").lexeme)
            while self._match(TokenType.COMMA):
                params.append(self._expect(TokenType.IDENTIFIER, "expected a parameter name after ','").lexeme)
        self._expect(TokenType.RPAREN, "expected ')' after the parameter list")
        body = self._parse_block("the function header")
        return ast.FunctionDecl(name=name_tok.lexeme, params=params, body=body, line=line)

    # -- controls (GRAMMAR.md §7) -----------------------------------------------

    def _control_decl(self) -> ast.ControlDecl:
        kind_tok = self._advance()
        caption = None
        if self._check(TokenType.STRING):
            caption = self._advance().value
        self._expect(TokenType.AS, f"expected 'as' after '{kind_tok.lexeme}'")
        name_tok = self._expect(TokenType.IDENTIFIER, "expected a control name after 'as'")
        self._expect(TokenType.AT, "expected 'at' after the control name")
        x = self._expr()
        self._expect(TokenType.COMMA, "expected ',' after the control's x position")
        y = self._expr()
        self._expect(TokenType.COMMA, "expected ',' after the control's y position")
        w = self._expr()
        self._expect(TokenType.COMMA, "expected ',' after the control's width")
        h = self._expr()
        self._expect(TokenType.NEWLINE, "expected a new line after the control declaration")
        return ast.ControlDecl(
            kind=kind_tok.lexeme, caption=caption, name=name_tok.lexeme, x=x, y=y, w=w, h=h,
            line=kind_tok.line,
        )

    # -- menus (GRAMMAR.md §8) ---------------------------------------------------

    def _menu_decl(self) -> ast.MenuDecl:
        line = self._advance().line  # 'menu'
        title_tok = self._expect(TokenType.STRING, "expected a quoted menu title after 'menu'")
        self._expect(TokenType.AS, "expected 'as' after the menu title")
        name_tok = self._expect(TokenType.IDENTIFIER, "expected a menu name after 'as'")
        body = self._parse_menu_body("the menu header")
        return ast.MenuDecl(title=title_tok.value, name=name_tok.lexeme, body=body, line=line)

    def _parse_menu_body(self, context: str) -> list[ast.MenuItem]:
        self._expect(TokenType.COLON, f"expected ':' after {context}")
        self._expect(TokenType.NEWLINE, f"expected a new line after ':' in {context}")
        self._skip_blank_newlines()
        self._expect(TokenType.INDENT, f"expected an indented block after {context}")
        items: list[ast.MenuItem] = []
        self._skip_blank_newlines()
        while not self._check(TokenType.DEDENT):
            items.append(self._menu_item())
            self._skip_blank_newlines()
        self._expect(TokenType.DEDENT, f"expected the indented block in {context} to end")
        return items

    def _menu_item(self) -> ast.MenuItem:
        if self._check(TokenType.ITEM):
            line = self._advance().line
            title_tok = self._expect(TokenType.STRING, "expected a quoted title after 'item'")
            self._expect(TokenType.AS, "expected 'as' after the item title")
            name_tok = self._expect(TokenType.IDENTIFIER, "expected an item name after 'as'")
            self._expect(TokenType.NEWLINE, "expected a new line after the menu item")
            return ast.ItemDecl(title=title_tok.value, name=name_tok.lexeme, line=line)

        if self._check(TokenType.CHECKITEM):
            line = self._advance().line
            title_tok = self._expect(TokenType.STRING, "expected a quoted title after 'checkitem'")
            self._expect(TokenType.AS, "expected 'as' after the checkitem title")
            name_tok = self._expect(TokenType.IDENTIFIER, "expected a checkitem name after 'as'")
            self._expect(TokenType.NEWLINE, "expected a new line after the checkitem")
            return ast.CheckItemDecl(title=title_tok.value, name=name_tok.lexeme, line=line)

        if self._check(TokenType.SUBMENU):
            line = self._advance().line
            title_tok = self._expect(TokenType.STRING, "expected a quoted title after 'submenu'")
            self._expect(TokenType.AS, "expected 'as' after the submenu title")
            name_tok = self._expect(TokenType.IDENTIFIER, "expected a submenu name after 'as'")
            body = self._parse_menu_body("the submenu header")
            return ast.SubmenuDecl(title=title_tok.value, name=name_tok.lexeme, body=body, line=line)

        if self._check(TokenType.SEPARATOR):
            line = self._advance().line
            self._expect(TokenType.NEWLINE, "expected a new line after 'separator'")
            return ast.Separator(line=line)

        raise LeopardSyntaxError(
            self._peek().line,
            "expected 'item', 'checkitem', 'submenu', or 'separator' inside a menu",
        )

    # -- events (GRAMMAR.md §9) ---------------------------------------------------

    def _event_handler(self) -> ast.EventHandler:
        line = self._advance().line  # 'on'
        if not self._check(*_EVENT_KEYWORDS):
            raise LeopardSyntaxError(
                self._peek().line,
                "expected 'click', 'change', 'select', 'close', or 'mousemove' after 'on'",
            )
        event = _EVENT_KEYWORDS[self._advance().type]

        target = None
        if self._check(TokenType.IDENTIFIER):
            target = self._advance().lexeme

        body = self._parse_block(f"the 'on {event}' header")
        return ast.EventHandler(event=event, target=target, body=body, line=line)

    # -- assignment / expression statements ---------------------------------------
    #
    # GRAMMAR.md §4: `=` doubles as both assignment and equality-comparison — there's
    # no separate `==`. That's only unambiguous because assignment targets are always
    # a bare name or a postfix chain (`.prop`, `[index]`), never a full expression. So
    # a statement's leading operand is parsed just up to `_unary_expr` (postfix chains,
    # no operators) rather than the full `_expr()`, and an immediately-following `=` is
    # checked for *before* continuing up the precedence chain — where a bare `=` would
    # otherwise be consumed as the comparison operator instead.

    def _simple_statement(self) -> ast.Stmt:
        line = self._peek().line

        # `not ...` can never be an assignment target, so it's safe to skip the
        # restricted base-parse below and hand it straight to the full expression
        # grammar (which itself starts above `_unary_expr`, at `_not_expr`).
        if self._check(TokenType.NOT):
            expr = self._expr()
            self._expect(TokenType.NEWLINE, "expected a new line after the statement")
            return ast.ExprStatement(expr=expr, line=line)

        base = self._unary_expr()

        if self._match(TokenType.EQ):
            value = self._expr()
            self._expect(TokenType.NEWLINE, "expected a new line after the assignment")
            if isinstance(base, ast.Identifier):
                return ast.Assignment(target=base.name, value=value, line=line)
            if isinstance(base, (ast.PropertyAccess, ast.Index)):
                return ast.PropertyAssignment(target=base, value=value, line=line)
            raise LeopardSyntaxError(line, "left-hand side of '=' is not something that can be assigned to")

        if isinstance(base, ast.Identifier) and self._check(*_EXPRESSION_START_TYPES):
            args = [self._expr()]
            while self._match(TokenType.COMMA):
                args.append(self._expr())
            expr: ast.Expr = ast.Call(callee=base, args=args, line=line)
        else:
            expr = self._expr_continue(base)
            if isinstance(expr, ast.Identifier):
                # A bare name as an entire statement (nothing followed it, and it
                # didn't continue into a larger expression either) is a zero-arg
                # command — e.g. `up`/`down`/`home`/`north` (GRAMMAR.md §10). This
                # only applies at statement position: `x + 1` still parses as
                # addition, not `x() + 1` — see _expr_continue above.
                expr = ast.Call(callee=expr, args=[], line=line)

        self._expect(TokenType.NEWLINE, "expected a new line after the statement")
        return ast.ExprStatement(expr=expr, line=line)

    def _expr_continue(self, base: ast.Expr) -> ast.Expr:
        """Resume the precedence chain above `_unary_expr` from an already-parsed operand."""
        expr = self._power_expr_cont(base)
        expr = self._multiplicative_expr_cont(expr)
        expr = self._additive_expr_cont(expr)
        expr = self._concat_expr_cont(expr)
        expr = self._comparison_expr_cont(expr)
        expr = self._and_expr_cont(expr)
        expr = self._or_expr_cont(expr)
        return expr

    # -- expressions (GRAMMAR.md §4), precedence climbing --------------------------
    #
    # or > and > not > comparison > concat (&) > additive (+ -) > multiplicative (* / %)
    # > power (^) > unary (-) > postfix (. [] ()) > primary
    #
    # Each level is split into `_xxx_expr` (parse the tighter level, then continue) and
    # `_xxx_expr_cont(left)` (just the continuation loop) so `_expr_continue` above can
    # resume the chain partway up from an already-parsed operand.

    def _expr(self) -> ast.Expr:
        return self._or_expr()

    def _or_expr(self) -> ast.Expr:
        return self._or_expr_cont(self._and_expr())

    def _or_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(TokenType.OR):
            line = self._advance().line
            right = self._and_expr()
            left = ast.BinaryOp(left=left, op="or", right=right, line=line)
        return left

    def _and_expr(self) -> ast.Expr:
        return self._and_expr_cont(self._not_expr())

    def _and_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(TokenType.AND):
            line = self._advance().line
            right = self._not_expr()
            left = ast.BinaryOp(left=left, op="and", right=right, line=line)
        return left

    def _not_expr(self) -> ast.Expr:
        if self._check(TokenType.NOT):
            line = self._advance().line
            operand = self._not_expr()
            return ast.UnaryOp(op="not", operand=operand, line=line)
        return self._comparison_expr()

    def _comparison_expr(self) -> ast.Expr:
        return self._comparison_expr_cont(self._concat_expr())

    def _comparison_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(*_COMPARISON_OPS):
            tok = self._advance()
            right = self._concat_expr()
            left = ast.BinaryOp(left=left, op=_COMPARISON_OPS[tok.type], right=right, line=tok.line)
        return left

    def _concat_expr(self) -> ast.Expr:
        return self._concat_expr_cont(self._additive_expr())

    def _concat_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(TokenType.AMP):
            line = self._advance().line
            right = self._additive_expr()
            left = ast.BinaryOp(left=left, op="&", right=right, line=line)
        return left

    def _additive_expr(self) -> ast.Expr:
        return self._additive_expr_cont(self._multiplicative_expr())

    def _additive_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(*_ADDITIVE_OPS):
            tok = self._advance()
            right = self._multiplicative_expr()
            left = ast.BinaryOp(left=left, op=_ADDITIVE_OPS[tok.type], right=right, line=tok.line)
        return left

    def _multiplicative_expr(self) -> ast.Expr:
        return self._multiplicative_expr_cont(self._power_expr())

    def _multiplicative_expr_cont(self, left: ast.Expr) -> ast.Expr:
        while self._check(*_MULTIPLICATIVE_OPS):
            tok = self._advance()
            right = self._power_expr()
            left = ast.BinaryOp(left=left, op=_MULTIPLICATIVE_OPS[tok.type], right=right, line=tok.line)
        return left

    def _power_expr(self) -> ast.Expr:
        return self._power_expr_cont(self._unary_expr())

    def _power_expr_cont(self, left: ast.Expr) -> ast.Expr:
        if self._check(TokenType.CARET):
            line = self._advance().line
            right = self._power_expr()  # right-associative
            return ast.BinaryOp(left=left, op="^", right=right, line=line)
        return left

    def _unary_expr(self) -> ast.Expr:
        if self._check(TokenType.MINUS):
            line = self._advance().line
            operand = self._unary_expr()
            return ast.UnaryOp(op="-", operand=operand, line=line)
        return self._postfix_expr()

    def _postfix_expr(self) -> ast.Expr:
        expr = self._primary()
        while True:
            if self._check(TokenType.DOT):
                line = self._advance().line
                # Property names (.text, .size, .font, ...) aren't reserved words
                # (GRAMMAR.md §14 never lists them), but their spellings can collide
                # with keywords reserved for other reasons (e.g. `text`/`size`/`font`
                # are also turtle commands) — so any word-like token is accepted here.
                name_tok = self._peek()
                if not name_tok.lexeme.isidentifier():
                    raise LeopardSyntaxError(name_tok.line, "expected a property name after '.'")
                self._advance()
                expr = ast.PropertyAccess(obj=expr, name=name_tok.lexeme, line=line)
            elif self._check(TokenType.LBRACKET):
                line = self._advance().line
                index = self._expr()
                self._expect(TokenType.RBRACKET, "expected ']' after the index")
                expr = ast.Index(obj=expr, index=index, line=line)
            elif self._check(TokenType.LPAREN):
                line = self._advance().line
                args: list[ast.Expr] = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._expr())
                    while self._match(TokenType.COMMA):
                        args.append(self._expr())
                self._expect(TokenType.RPAREN, "expected ')' after the argument list")
                expr = ast.Call(callee=expr, args=args, line=line)
            else:
                break
        return expr

    def _primary(self) -> ast.Expr:
        tok = self._peek()

        if tok.type is TokenType.NUMBER:
            self._advance()
            return ast.Literal(value=tok.value, line=tok.line)
        if tok.type is TokenType.STRING:
            self._advance()
            return ast.Literal(value=tok.value, line=tok.line)
        if tok.type is TokenType.TRUE:
            self._advance()
            return ast.Literal(value=True, line=tok.line)
        if tok.type is TokenType.FALSE:
            self._advance()
            return ast.Literal(value=False, line=tok.line)
        if tok.type is TokenType.IDENTIFIER or tok.type in EXPRESSION_KEYWORDS:
            self._advance()
            return ast.Identifier(name=tok.lexeme, line=tok.line)
        if tok.type is TokenType.LPAREN:
            self._advance()
            expr = self._expr()
            self._expect(TokenType.RPAREN, "expected ')' to close '('")
            return expr
        if tok.type is TokenType.LBRACKET:
            self._advance()
            elements: list[ast.Expr] = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._expr())
                while self._match(TokenType.COMMA):
                    elements.append(self._expr())
            self._expect(TokenType.RBRACKET, "expected ']' to close the list literal")
            return ast.ListLiteral(elements=elements, line=tok.line)

        raise LeopardSyntaxError(tok.line, f"expected an expression, found '{tok.lexeme or tok.type.name}'")


def parse(tokens: list[Token]) -> ast.Program:
    return Parser(tokens).parse_program()
