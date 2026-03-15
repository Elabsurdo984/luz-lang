from .tokens import TokenType

class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"{self.token.value}"

class StringNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"\"{self.token.value}\""

class VarAccessNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f"{self.token.value}"

class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
    def __repr__(self): return f"({self.var_name_token.value} = {self.value_node})"

class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    def __repr__(self): return f"({self.left_node} {self.op_token.type.name} {self.right_node})"

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases # List of (condition, block)
        self.else_case = else_case # Block

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    def parse(self):
        return self.statements()

    def statements(self):
        statements = []
        while self.current_token.type != TokenType.EOF and self.current_token.type != TokenType.RBRACE:
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.current_token.type == TokenType.IF:
            return self.if_expr()
        
        if self.current_token.type == TokenType.IDENTIFIER:
            # Lookahead for assignment
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == TokenType.ASSIGN:
                var_name = self.current_token
                self.advance() # identifier
                self.advance() # =
                expr = self.expr()
                return VarAssignNode(var_name, expr)
        
        return self.expr()

    def if_expr(self):
        cases = []
        else_case = None

        # IF
        self.advance()
        condition = self.expr()
        if self.current_token.type != TokenType.LBRACE:
            raise Exception("Esperado '{' después de la condición de if")
        self.advance()
        block = self.statements()
        if self.current_token.type != TokenType.RBRACE:
            raise Exception("Esperado '}' después del bloque de if")
        self.advance()
        cases.append((condition, block))

        # ELIF
        while self.current_token.type == TokenType.ELIF:
            self.advance()
            condition = self.expr()
            if self.current_token.type != TokenType.LBRACE:
                raise Exception("Esperado '{' después de la condición de elif")
            self.advance()
            block = self.statements()
            if self.current_token.type != TokenType.RBRACE:
                raise Exception("Esperado '}' después del bloque de elif")
            self.advance()
            cases.append((condition, block))

        # ELSE
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            if self.current_token.type != TokenType.LBRACE:
                raise Exception("Esperado '{' después de else")
            self.advance()
            else_case = self.statements()
            if self.current_token.type != TokenType.RBRACE:
                raise Exception("Esperado '}' después del bloque de else")
            self.advance()

        return IfNode(cases, else_case)

    def expr(self):
        return self.bin_op(self.comp_expr, (TokenType.EE, TokenType.NE, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE))

    def comp_expr(self):
        return self.bin_op(self.arith_expr, (TokenType.PLUS, TokenType.MINUS))

    def arith_expr(self):
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    def term(self):
        return self.bin_op(self.factor, (TokenType.MUL, TokenType.DIV))

    def factor(self):
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token)
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return VarAccessNode(token)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type == TokenType.RPAREN:
                self.advance()
                return expr
        raise Exception(f"Sintaxis inválida en token: {token}")

    def bin_op(self, func, ops):
        left = func()
        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinOpNode(left, op_token, right)
        return left
