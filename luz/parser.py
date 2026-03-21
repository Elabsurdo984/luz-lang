# parser.py
#
# The Parser is the second stage of the Luz interpreter pipeline.  It receives
# the flat list of Token objects produced by the Lexer and builds an Abstract
# Syntax Tree (AST) — a hierarchical data structure that represents the program's
# grammatical structure.
#
# Pipeline position:
#   list[Token] → [Parser.parse()] → list[ASTNode] → Interpreter
#
# Design: Recursive Descent
# ──────────────────────────
# The parser is a hand-written recursive-descent parser.  Each grammar rule is
# represented by a method.  Methods call each other recursively, mirroring the
# nested structure of the grammar.
#
# Operator Precedence (lowest → highest):
#   logical or  (or)
#   logical and (and)
#   logical not (not)
#   comparisons (== != < > <= >=)
#   addition / subtraction (+ -)
#   multiplication / division / modulo (* / // %)
#   exponentiation (**)           ← right-associative
#   unary minus, literals, grouping, identifiers, index access
#
# Each precedence level is a separate method (logical_or → logical_and → … →
# factor).  Higher-precedence operators are parsed deeper in the call chain,
# which automatically gives them tighter binding.
#
# AST Nodes
# ─────────
# Every syntactic construct maps to a dedicated node class defined at the top
# of this file.  Node classes are intentionally simple data containers — all
# evaluation logic lives in the Interpreter.  Each node stores a `line`
# attribute (attached after construction) so the interpreter can report the
# source line when an error occurs at runtime.

from .tokens import TokenType
from .exceptions import (
    UnexpectedTokenFault, UnexpectedEOFault, StructureFault,
    ParseFault, ExpressionFault, OperatorFault, SyntaxFault
)


# ── AST Node classes ──────────────────────────────────────────────────────────
# One class per distinct syntactic construct.  __repr__ methods exist purely
# for debugging — they are never called during normal interpretation.

# Represents an integer or float literal value.
class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"{self.token.value}"

# Represents a string literal value.
class StringNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"\"{self.token.value}\""

# Represents a boolean literal (true / false).
class BooleanNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"{self.token.type.name.lower()}"

# Represents the null literal.
class NullNode:
    def __repr__(self): return "null"

# Represents a list literal: [expr, expr, …]
class ListNode:
    def __init__(self, elements):
        self.elements = elements  # List of AST nodes, one per element
    def __repr__(self): return f"{self.elements}"

# Represents a dictionary literal: {key: value, …}
class DictNode:
    def __init__(self, pairs):
        self.pairs = pairs  # List of (key_node, value_node) tuples
    def __repr__(self): return f"{{{self.pairs}}}"

# Represents reading a value via subscript: expr[index]
# After evaluation base_node and index_node are both evaluated, then the
# interpreter performs the actual lookup depending on the container type.
class IndexAccessNode:
    def __init__(self, base_node, index_node):
        self.base_node = base_node
        self.index_node = index_node
    def __repr__(self): return f"{self.base_node}[{self.index_node}]"

# Represents writing to a subscript position: expr[index] = value
# This is a statement-level construct; the interpreter mutates the container
# in-place rather than returning a new value.
class IndexAssignNode:
    def __init__(self, base_node, index_node, value_node):
        self.base_node = base_node
        self.index_node = index_node
        self.value_node = value_node
    def __repr__(self): return f"({self.base_node}[{self.index_node}] = {self.value_node})"

# Represents a unary operation: -expr or not expr
class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token  # The operator token (MINUS or NOT)
        self.node = node          # The operand
    def __repr__(self): return f"({self.op_token.type.name} {self.node})"

# Represents reading a variable: just its name.
class VarAccessNode:
    def __init__(self, token):
        self.token = token  # The IDENTIFIER token (carries the name as .value)
    def __repr__(self): return f"{self.token.value}"

# Represents assigning to a variable: name = expr
class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
    def __repr__(self): return f"({self.var_name_token.value} = {self.value_node})"

# Represents a binary operation: left op right  (e.g. a + b, x == y)
class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    def __repr__(self): return f"({self.left_node} {self.op_token.type.name} {self.right_node})"

# Represents an if / elif* / else? chain.
# cases is a list of (condition_node, block) pairs — one per if/elif branch.
# else_case is a block (list of statements) or None.
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases        # [(condition, block), …]
        self.else_case = else_case

# Represents a while loop: while condition { block }
class WhileNode:
    def __init__(self, condition_node, block):
        self.condition_node = condition_node
        self.block = block  # List of statement nodes

# Represents a for loop with a numeric range: for var = start to end { block }
# The loop variable is scoped to the loop body.
class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, block):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.block = block

# Represents a for-each loop over a collection: for item in expr { block }
# Works with lists, strings (iterates characters), and dicts (iterates keys).
class ForEachNode:
    def __init__(self, var_name_token, iterable_node, block):
        self.var_name_token = var_name_token
        self.iterable_node = iterable_node
        self.block = block

# Represents a function definition: function name(args) { block }
# arg_tokens is a list of IDENTIFIER tokens (the parameter names).
class FuncDefNode:
    def __init__(self, name_token, arg_tokens, block):
        self.name_token = name_token
        self.arg_tokens = arg_tokens
        self.block = block

# Represents a return statement inside a function body.
# expression_node may be None for a bare `return`.
class ReturnNode:
    def __init__(self, expression_node):
        self.expression_node = expression_node

# Represents an import statement: import "path/to/file.luz"
class ImportNode:
    def __init__(self, file_path_token):
        self.file_path_token = file_path_token  # STRING token carrying the path

# Represents an attempt/rescue block (structured error handling).
# error_var_token is the IDENTIFIER token used to bind the error message inside
# the rescue body.
class AttemptRescueNode:
    def __init__(self, try_block, error_var_token, catch_block):
        self.try_block = try_block
        self.error_var_token = error_var_token
        self.catch_block = catch_block

# Represents the `alert` statement — raises a user-defined error at runtime.
class AlertNode:
    def __init__(self, expression_node):
        self.expression_node = expression_node

# The following three node classes carry no data — their type alone is
# sufficient for the interpreter to know what to do.
class BreakNode:
    def __repr__(self): return "break"

class ContinueNode:
    def __repr__(self): return "continue"

class PassNode:
    def __repr__(self): return "pass"

# Represents a class definition: class Name { method ... }
# or with inheritance:          class Name extends Parent { method ... }
class ClassDefNode:
    def __init__(self, name_token, methods, parent_token=None):
        self.name_token = name_token
        self.parent_token = parent_token  # IDENTIFIER token for the parent class, or None
        self.methods = methods  # List of FuncDefNode

# Represents reading an attribute: obj.name
class AttributeAccessNode:
    def __init__(self, obj_node, attr_token):
        self.obj_node = obj_node
        self.attr_token = attr_token
    def __repr__(self): return f"{self.obj_node}.{self.attr_token.value}"

# Represents writing an attribute: obj.name = value
class AttributeAssignNode:
    def __init__(self, obj_node, attr_token, value_node):
        self.obj_node = obj_node
        self.attr_token = attr_token
        self.value_node = value_node
        
class MethodCallNode:
    def __init__(self, obj_node, method_token, arguments):
        self.obj_node = obj_node
        self.method_token = method_token
        self.arguments = arguments

# Represents a function call: name(arg, arg, …)
# arguments is a list of AST nodes (the evaluated argument expressions).
class CallNode:
    def __init__(self, func_name_token, arguments):
        self.func_name_token = func_name_token
        self.arguments = arguments
    def __repr__(self): return f"{self.func_name_token.value}({self.arguments})"


# ── Parser ────────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    # advance() moves to the next token in the list.  The bounds check ensures
    # that current_token stays at EOF rather than raising an IndexError when the
    # parser tries to look past the end of the list.
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    # parse() is the public entry point.  It delegates to statements() and
    # wraps unexpected Python exceptions into a ParseFault so callers always
    # receive a LuzError on failure, never a raw Python traceback.
    # Known SyntaxFault subclasses are re-raised as-is to preserve their type.
    def parse(self):
        try:
            return self.statements()
        except UnexpectedTokenFault as e:
            raise e
        except SyntaxFault as e:
            raise e
        except Exception as e:
            raise ParseFault(f"Error while parsing code: {str(e)}")

    # statements() collects a sequence of statements until it hits EOF or a
    # closing brace '}'.  The RBRACE check allows this same method to parse
    # both top-level programs and the bodies of blocks (if, while, function, …).
    def statements(self):
        statements = []
        while self.current_token.type != TokenType.EOF and self.current_token.type != TokenType.RBRACE:
            statements.append(self.statement())
        return statements

    # statement() recognises the opening token of each statement form and
    # dispatches to the appropriate parsing method.  For constructs that don't
    # have a distinctive leading keyword (expressions, assignments) it falls
    # through to expr() at the bottom.
    def statement(self):
        if self.current_token.type == TokenType.IF:
            return self.if_expr()

        if self.current_token.type == TokenType.WHILE:
            return self.while_expr()

        if self.current_token.type == TokenType.FOR:
            return self.for_expr()

        if self.current_token.type == TokenType.FUNCTION:
            return self.func_def()

        if self.current_token.type == TokenType.RETURN:
            line = self.current_token.line
            self.advance()
            # `return` with no expression is valid — the function returns None.
            # We stop at RBRACE or EOF rather than trying to parse a non-existent expr.
            expr = None
            if self.current_token.type not in (TokenType.EOF, TokenType.RBRACE):
                expr = self.expr()
            node = ReturnNode(expr); node.line = line
            return node

        if self.current_token.type == TokenType.IMPORT:
            line = self.current_token.line
            self.advance()
            if self.current_token.type != TokenType.STRING:
                raise UnexpectedTokenFault(f"Expected module path string after 'import', received {self.current_token}")
            path_token = self.current_token
            self.advance()
            node = ImportNode(path_token); node.line = line
            return node

        if self.current_token.type == TokenType.ATTEMPT:
            return self.attempt_rescue_expr()

        if self.current_token.type == TokenType.ALERT:
            line = self.current_token.line
            self.advance()
            expr = self.expr()
            node = AlertNode(expr); node.line = line
            return node

        if self.current_token.type == TokenType.BREAK:
            line = self.current_token.line
            self.advance()
            node = BreakNode(); node.line = line
            return node

        if self.current_token.type == TokenType.CONTINUE:
            line = self.current_token.line
            self.advance()
            node = ContinueNode(); node.line = line
            return node

        if self.current_token.type == TokenType.PASS:
            line = self.current_token.line
            self.advance()
            node = PassNode(); node.line = line
            return node
        
        if self.current_token.type == TokenType.CLASS:
            return self.class_def()

        if self.current_token.type == TokenType.IDENTIFIER:
            # One-token lookahead: if the token after the identifier is '=',
            # this is a variable assignment rather than an expression.
            # We must check here before entering expr() because expr() would
            # parse the identifier as a VarAccessNode and then get confused by
            # the '=' that follows.
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == TokenType.ASSIGN:
                var_name = self.current_token
                self.advance()  # Consume the identifier
                self.advance()  # Consume '='
                expr = self.expr()
                node = VarAssignNode(var_name, expr); node.line = var_name.line
                return node

        # Fall through: parse as a general expression (function call, arithmetic, …)
        node = self.expr()

        # Post-expression check for index assignment: lista[0] = 5
        if isinstance(node, IndexAccessNode) and self.current_token.type == TokenType.ASSIGN:
            line = node.line
            self.advance()  # Consume '='
            value = self.expr()
            assign_node = IndexAssignNode(node.base_node, node.index_node, value)
            assign_node.line = line
            return assign_node

        # Post-expression check for attribute assignment: obj.attr = value
        if isinstance(node, AttributeAccessNode) and self.current_token.type == TokenType.ASSIGN:
            line = node.line
            self.advance()  # Consume '='
            value = self.expr()
            assign_node = AttributeAssignNode(node.obj_node, node.attr_token, value)
            assign_node.line = line
            return assign_node

        return node

    # attempt_rescue_expr() parses the structured error-handling construct:
    #   attempt { statements } rescue (err) { statements }
    # The error variable is bound in the rescue scope to the string
    # representation of whatever error was caught.
    def attempt_rescue_expr(self):
        line = self.current_token.line
        self.advance()  # Consume 'attempt'
        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' after attempt")
        self.advance()  # Consume '{'

        try_block = self.statements()

        if self.current_token.type == TokenType.EOF:
            raise UnexpectedEOFault("Unexpected end of file in attempt block")
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault(f"Expected '}}' at the end of attempt block, received {self.current_token}")
        self.advance()  # Consume '}'

        if self.current_token.type != TokenType.RESCUE:
            raise StructureFault("Expected 'rescue' after attempt block")
        self.advance()  # Consume 'rescue'

        if self.current_token.type != TokenType.LPAREN:
            raise StructureFault("Expected '(' after rescue")
        self.advance()  # Consume '('

        if self.current_token.type != TokenType.IDENTIFIER:
            raise UnexpectedTokenFault("Expected error variable name in rescue")
        error_var = self.current_token
        self.advance()  # Consume the error variable name

        if self.current_token.type != TokenType.RPAREN:
            raise UnexpectedTokenFault("Expected ')'")
        self.advance()  # Consume ')'

        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' for rescue block")
        self.advance()  # Consume '{'

        catch_block = self.statements()

        if self.current_token.type == TokenType.EOF:
            raise UnexpectedEOFault("Unexpected end of file in rescue block")
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault(f"Expected '}}' at the end of rescue block, received {self.current_token}")
        self.advance()  # Consume '}'

        node = AttemptRescueNode(try_block, error_var, catch_block); node.line = line
        return node

    # func_def() parses:  function name(param, …) { body }
    # Parameters are just identifier names at parse time; their values are
    # bound by LuzFunction.__call__() at call time.
    def func_def(self):
        line = self.current_token.line
        self.advance()  # Consume 'function'
        if self.current_token.type != TokenType.IDENTIFIER:
            raise UnexpectedTokenFault("Expected function name")
        name_token = self.current_token
        self.advance()  # Consume the name

        if self.current_token.type != TokenType.LPAREN:
            raise StructureFault("Expected '('")
        self.advance()  # Consume '('

        # Parse the parameter list, which may be empty.
        # Both IDENTIFIER and SELF are valid parameter names (methods use `self`
        # as their first parameter to receive the instance at call time).
        arg_tokens = []
        if self.current_token.type in (TokenType.IDENTIFIER, TokenType.SELF):
            arg_tokens.append(self.current_token)
            self.advance()
            # Additional parameters are comma-separated.
            while self.current_token.type == TokenType.COMMA:
                self.advance()  # Consume ','
                if self.current_token.type not in (TokenType.IDENTIFIER, TokenType.SELF):
                    raise UnexpectedTokenFault("Expected argument name")
                arg_tokens.append(self.current_token)
                self.advance()

        if self.current_token.type != TokenType.RPAREN:
            raise UnexpectedTokenFault("Expected ')'")
        self.advance()  # Consume ')'

        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{'")
        self.advance()  # Consume '{'

        block = self.statements()

        if self.current_token.type == TokenType.EOF:
            raise UnexpectedEOFault("Unexpected end of file in function definition")
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault("Expected '}'")
        self.advance()  # Consume '}'

        node = FuncDefNode(name_token, arg_tokens, block); node.line = line
        return node
    
    def class_def(self):
        line = self.current_token.line
        self.advance()  # Consume 'class'
        if self.current_token.type != TokenType.IDENTIFIER:
            raise UnexpectedTokenFault("Expected class name")
        name_token = self.current_token
        self.advance()

        # Optional inheritance clause: extends ParentName
        parent_token = None
        if self.current_token.type == TokenType.EXTENDS:
            self.advance()  # Consume 'extends'
            if self.current_token.type != TokenType.IDENTIFIER:
                raise UnexpectedTokenFault("Expected parent class name after 'extends'")
            parent_token = self.current_token
            self.advance()

        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' after class name")
        self.advance()  # Consume '{'
        methods = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise UnexpectedEOFault("Unexpected end of file in class")
            if self.current_token.type != TokenType.FUNCTION:
                raise UnexpectedTokenFault("Expected method definition inside class")
            methods.append(self.func_def())
        self.advance()  # Consume '}'
        node = ClassDefNode(name_token, methods, parent_token); node.line = line
        return node

    # if_expr() parses the full if / elif* / else? chain into a single IfNode.
    # All branches are collected into the same node so the interpreter can
    # evaluate them sequentially without needing to recurse.
    def if_expr(self):
        line = self.current_token.line
        cases = []
        else_case = None

        self.advance()  # Consume 'if'
        condition = self.expr()
        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' after if condition")
        self.advance()
        block = self.statements()
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault("Expected '}' after if block")
        self.advance()
        cases.append((condition, block))

        # Collect zero or more elif branches.
        while self.current_token.type == TokenType.ELIF:
            self.advance()  # Consume 'elif'
            condition = self.expr()
            if self.current_token.type != TokenType.LBRACE:
                raise StructureFault("Expected '{' after elif condition")
            self.advance()
            block = self.statements()
            if self.current_token.type != TokenType.RBRACE:
                raise UnexpectedTokenFault("Expected '}' after elif block")
            self.advance()
            cases.append((condition, block))

        # Optional else branch.
        if self.current_token.type == TokenType.ELSE:
            self.advance()  # Consume 'else'
            if self.current_token.type != TokenType.LBRACE:
                raise StructureFault("Expected '{' after else")
            self.advance()
            else_case = self.statements()
            if self.current_token.type != TokenType.RBRACE:
                raise UnexpectedTokenFault("Expected '}' after else block")
            self.advance()

        node = IfNode(cases, else_case); node.line = line
        return node

    # while_expr() parses:  while condition { body }
    def while_expr(self):
        line = self.current_token.line
        self.advance()  # Consume 'while'
        condition = self.expr()
        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' after while condition")
        self.advance()
        block = self.statements()
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault("Expected '}' after while block")
        self.advance()
        node = WhileNode(condition, block); node.line = line
        return node

    # for_expr() handles two loop forms:
    #   Range loop:   for i = 0 to 10 { … }
    #   For-each:     for item in list { … }
    # After consuming the variable name, a one-token lookahead decides which form.
    def for_expr(self):
        line = self.current_token.line
        self.advance()  # Consume 'for'
        if self.current_token.type != TokenType.IDENTIFIER:
            raise UnexpectedTokenFault("Expected variable name after 'for'")
        var_name = self.current_token
        self.advance()

        if self.current_token.type == TokenType.IN:
            # for-each: for item in <iterable> { body }
            self.advance()  # Consume 'in'
            iterable = self.expr()
            if self.current_token.type != TokenType.LBRACE:
                raise StructureFault("Expected '{' after for-each iterable")
            self.advance()
            block = self.statements()
            if self.current_token.type != TokenType.RBRACE:
                raise UnexpectedTokenFault("Expected '}' after for block")
            self.advance()
            node = ForEachNode(var_name, iterable, block); node.line = line
            return node

        # Range loop: for i = start to end { body }
        if self.current_token.type != TokenType.ASSIGN:
            raise StructureFault("Expected '=' or 'in' after for variable")
        self.advance()  # Consume '='
        start_value = self.expr()
        if self.current_token.type != TokenType.TO:
            raise StructureFault("Expected 'to' after for start value")
        self.advance()  # Consume 'to'
        end_value = self.expr()
        if self.current_token.type != TokenType.LBRACE:
            raise StructureFault("Expected '{' after for range")
        self.advance()
        block = self.statements()
        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault("Expected '}' after for block")
        self.advance()
        node = ForNode(var_name, start_value, end_value, block); node.line = line
        return node

    # ── Expression parsing (operator-precedence chain) ────────────────────────
    # Each method handles one precedence level.  Lower-precedence operators are
    # parsed by methods higher in the call chain.  The chain is:
    #   expr → logical_or → logical_and → logical_not → comp_expr
    #       → arith_expr → term → power → factor

    def expr(self):
        # Top-level expression entry point — delegates to the lowest-precedence
        # operator level in the chain.
        return self.logical_or()

    def logical_or(self):
        # `or` has the lowest precedence of any binary operator.
        return self.bin_op(self.logical_and, (TokenType.OR,))

    def logical_and(self):
        return self.bin_op(self.logical_not, (TokenType.AND,))

    def logical_not(self):
        # `not` is a unary prefix operator.  Allowing logical_not() to call
        # itself recursively means `not not x` works naturally.
        if self.current_token.type == TokenType.NOT:
            op_token = self.current_token
            self.advance()
            return UnaryOpNode(op_token, self.logical_not())
        return self.comp_expr()

    def comp_expr(self):
        # All comparison operators share the same precedence level, so they are
        # all handled by a single bin_op call.
        return self.bin_op(self.arith_expr, (TokenType.EE, TokenType.NE, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE))

    def arith_expr(self):
        # Addition and subtraction bind less tightly than multiplication.
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    def term(self):
        # Multiplication, division, integer division, and modulo all have equal
        # precedence and bind more tightly than addition/subtraction.
        return self.bin_op(self.power, (TokenType.MUL, TokenType.DIV, TokenType.IDIV, TokenType.MOD))

    def power(self):
        # Exponentiation is right-associative: 2**3**2 == 2**(3**2) == 512.
        # Right-associativity is achieved by recursing into power() again on the
        # right-hand side, rather than using the iterative bin_op helper (which
        # would produce a left-associative tree).
        base = self.factor()
        if self.current_token.type == TokenType.POW:
            op = self.current_token
            self.advance()
            exp = self.power()  # Recurse right → right-associative
            node = BinOpNode(base, op, exp)
            node.line = op.line
            return node
        return base

    def factor(self):
        # factor() handles the highest-precedence constructs:
        #   • unary minus
        #   • literal values (numbers, strings, booleans)
        #   • collection literals (lists, dicts)
        #   • parenthesised expressions
        #   • identifiers (which may be variable access or function calls)
        # After any of the above, a trailing '[' triggers index-access parsing
        # to handle chained subscripts: a[0][1][2]
        token = self.current_token
        node = None

        if token.type == TokenType.MINUS:
            # Unary minus: recurse into factor() so that '--x' also works.
            self.advance()
            node = UnaryOpNode(token, self.factor())
            node.line = token.line
            return node

        if token.type in (TokenType.INT, TokenType.FLOAT):
            self.advance()
            node = NumberNode(token)
            node.line = token.line
        elif token.type == TokenType.STRING:
            self.advance()
            node = StringNode(token)
            node.line = token.line
        elif token.type in (TokenType.TRUE, TokenType.FALSE):
            self.advance()
            node = BooleanNode(token)
            node.line = token.line
        elif token.type == TokenType.NULL:
            self.advance()
            node = NullNode()
            node.line = token.line
        elif token.type == TokenType.LBRACKET:
            node = self.list_literal()
        elif token.type == TokenType.LBRACE:
            node = self.dict_literal()
        elif token.type == TokenType.IDENTIFIER:
            # Could be a plain variable read or a function call — identifier_expr
            # peeks at the next token to decide.
            node = self.identifier_expr()
        elif token.type == TokenType.SELF:
            # `self` inside a method refers to the current instance.
            # It is treated as a variable access so that `self.attr` parsing
            # falls through to the DOT-chaining loop below.
            self.advance()
            node = VarAccessNode(token)
            node.line = token.line
        elif token.type == TokenType.LPAREN:
            # Parenthesised sub-expression for explicit grouping.
            self.advance()  # Consume '('
            node = self.expr()
            if self.current_token.type != TokenType.RPAREN:
                raise UnexpectedTokenFault("Expected ')'")
            self.advance()  # Consume ')'
        elif token.type == TokenType.EOF:
            raise UnexpectedEOFault("Unexpected end of expression")
        else:
            raise ExpressionFault(f"Invalid expression at token: {token}")

        # Handle zero or more chained index operations: base[i][j][k]…
        # Each iteration wraps the current node in a new IndexAccessNode.
        while self.current_token.type == TokenType.LBRACKET:
            bracket_line = self.current_token.line
            self.advance()  # Consume '['
            index = self.expr()
            if self.current_token.type != TokenType.RBRACKET:
                raise UnexpectedTokenFault("Expected ']'")
            self.advance()  # Consume ']'
            index_node = IndexAccessNode(node, index)
            index_node.line = bracket_line
            node = index_node

        # Handle zero or more chained dot accesses: obj.attr  or  obj.method(args)
        # This loop also handles chaining: obj.a.b.c()
        while self.current_token.type == TokenType.DOT:
            dot_line = self.current_token.line
            self.advance()  # Consume '.'
            if self.current_token.type != TokenType.IDENTIFIER:
                raise UnexpectedTokenFault("Expected attribute or method name after '.'")
            attr_token = self.current_token
            self.advance()  # Consume the attribute/method name
            if self.current_token.type == TokenType.LPAREN:
                # Method call: obj.method(args)
                self.advance()  # Consume '('
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expr())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        if self.current_token.type == TokenType.RPAREN:
                            break
                        args.append(self.expr())
                if self.current_token.type != TokenType.RPAREN:
                    raise UnexpectedTokenFault("Expected ')'")
                self.advance()  # Consume ')'
                node = MethodCallNode(node, attr_token, args)
                node.line = dot_line
            else:
                # Attribute read: obj.attr
                node = AttributeAccessNode(node, attr_token)
                node.line = dot_line

        return node

    # identifier_expr() disambiguates between a variable access and a function
    # call by peeking at the token after the identifier.
    def identifier_expr(self):
        token = self.current_token
        self.advance()  # Consume the identifier
        if self.current_token.type == TokenType.LPAREN:
            # Function call: identifier(arg, …)
            self.advance()  # Consume '('
            args = []
            if self.current_token.type != TokenType.RPAREN:
                args.append(self.expr())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()  # Consume ','
                    # A trailing comma before ')' is tolerated (e.g. f(a,))
                    if self.current_token.type == TokenType.RPAREN:
                        break
                    args.append(self.expr())

            if self.current_token.type != TokenType.RPAREN:
                raise UnexpectedTokenFault("Expected ',' or ')'")
            self.advance()  # Consume ')'
            node = CallNode(token, args); node.line = token.line
            return node
        else:
            # Plain variable read
            node = VarAccessNode(token); node.line = token.line
            return node

    # list_literal() parses:  [ expr, expr, … ]
    # A trailing comma before ']' is permitted so that multi-line lists are
    # easier to write without a linting error on the last element.
    def list_literal(self):
        line = self.current_token.line
        self.advance()  # Consume '['
        elements = []
        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.advance()  # Consume ','
                if self.current_token.type == TokenType.RBRACKET:
                    break  # Trailing comma — stop before the closing bracket
                elements.append(self.expr())

        if self.current_token.type != TokenType.RBRACKET:
            raise UnexpectedTokenFault("Expected ']' at the end of list")
        self.advance()  # Consume ']'
        node = ListNode(elements); node.line = line
        return node

    # dict_literal() parses:  { key: value, key: value, … }
    # Keys can be any expression, though in practice they will usually be
    # strings or numbers.  A trailing comma before '}' is also permitted.
    def dict_literal(self):
        line = self.current_token.line
        self.advance()  # Consume '{'
        pairs = []
        if self.current_token.type != TokenType.RBRACE:
            key = self.expr()
            if self.current_token.type != TokenType.COLON:
                raise StructureFault("Expected ':' after dictionary key")
            self.advance()  # Consume ':'
            value = self.expr()
            pairs.append((key, value))

            while self.current_token.type == TokenType.COMMA:
                self.advance()  # Consume ','
                if self.current_token.type == TokenType.RBRACE:
                    break  # Trailing comma — stop before '}'
                key = self.expr()
                if self.current_token.type != TokenType.COLON:
                    raise StructureFault("Expected ':' after dictionary key")
                self.advance()  # Consume ':'
                value = self.expr()
                pairs.append((key, value))

        if self.current_token.type != TokenType.RBRACE:
            raise UnexpectedTokenFault("Expected '}' at the end of dictionary")
        self.advance()  # Consume '}'
        node = DictNode(pairs); node.line = line
        return node

    # bin_op() is a reusable helper that implements left-associative binary
    # operators for a given precedence level.
    #
    # Parameters:
    #   func – a method reference that parses the next-higher precedence level
    #           (the operands of the operators being handled here)
    #   ops  – a tuple of TokenType values that are the operators at this level
    #
    # It builds a left-leaning tree:  (((a op b) op c) op d)
    # which is correct for left-associative operators.
    #
    # The ExpressionFault catch around the right-hand operand converts a missing
    # operand into a more descriptive OperatorFault message.
    def bin_op(self, func, ops):
        left = func()
        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            try:
                right = func()
            except ExpressionFault:
                raise OperatorFault(f"Operator '{op_token}' expects a valid expression on the right")
            bin_node = BinOpNode(left, op_token, right)
            bin_node.line = op_token.line
            left = bin_node  # The new node becomes the left operand for the next iteration
        return left
