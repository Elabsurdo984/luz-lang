from .tokens import TokenType

class Interpreter:
    def __init__(self):
        self.symbol_table = {}

    def visit(self, node):
        if isinstance(node, list):
            result = None
            for statement in node:
                result = self.visit(statement)
            return result

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return node.token.value

    def visit_StringNode(self, node):
        return node.token.value

    def visit_VarAssignNode(self, node):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node)
        self.symbol_table[var_name] = value
        return value

    def visit_VarAccessNode(self, node):
        var_name = node.token.value
        if var_name not in self.symbol_table:
            raise Exception(f"Variable '{var_name}' no definida")
        return self.symbol_table[var_name]

    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_token.type == TokenType.PLUS:
            return left + right
        elif node.op_token.type == TokenType.MINUS:
            if isinstance(left, str) or isinstance(right, str):
                raise Exception("Operación '-' no soportada para strings")
            return left - right
        elif node.op_token.type == TokenType.MUL:
            if isinstance(left, str) and isinstance(right, float):
                return left * int(right)
            if isinstance(left, float) or isinstance(right, float):
                 return left * right
            raise Exception("Operación '*' solo soportada entre números o string y número")
        elif node.op_token.type == TokenType.DIV:
            if isinstance(left, str) or isinstance(right, str):
                raise Exception("Operación '/' no soportada para strings")
            if right == 0:
                raise Exception("Error: División por cero")
            return left / right
        elif node.op_token.type == TokenType.EE:
            return 1.0 if left == right else 0.0
        elif node.op_token.type == TokenType.NE:
            return 1.0 if left != right else 0.0
        elif node.op_token.type == TokenType.LT:
            return 1.0 if left < right else 0.0
        elif node.op_token.type == TokenType.GT:
            return 1.0 if left > right else 0.0
        elif node.op_token.type == TokenType.LTE:
            return 1.0 if left <= right else 0.0
        elif node.op_token.type == TokenType.GTE:
            return 1.0 if left >= right else 0.0

    def visit_IfNode(self, node):
        for condition, block in node.cases:
            if self.visit(condition):
                return self.visit(block)
        
        if node.else_case:
            return self.visit(node.else_case)
        
        return 0.0
