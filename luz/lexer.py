import string
from .tokens import TokenType, Token
from .exceptions import InvalidTokenFault

class Lexer:
    KEYWORDS = {
        'if': TokenType.IF,
        'elif': TokenType.ELIF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'to': TokenType.TO,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'import': TokenType.IMPORT,
        'attempt': TokenType.ATTEMPT,
        'rescue': TokenType.RESCUE,
        'alert': TokenType.ALERT,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'pass': TokenType.PASS,
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.current_char = self.text[0] if len(self.text) > 0 else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()

    def make_number(self):
        num_str = ''
        dot_count = 0
        line = self.line
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TokenType.INT, int(num_str), line)
        else:
            return Token(TokenType.FLOAT, float(num_str), line)

    def make_identifier(self):
        id_str = ''
        line = self.line
        while self.current_char is not None and (self.current_char in string.ascii_letters + string.digits + '_'):
            id_str += self.current_char
            self.advance()

        token_type = self.KEYWORDS.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str if token_type == TokenType.IDENTIFIER else None, line)

    ESCAPE_SEQUENCES = {
        'n': '\n',
        't': '\t',
        'r': '\r',
        '\\': '\\',
        '"': '"',
    }

    def make_string(self):
        string_val = ''
        line = self.line
        self.advance() # Skip starting quote

        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    e = InvalidTokenFault("Unexpected end of string after '\\'")
                    e.line = line
                    raise e
                escaped = self.ESCAPE_SEQUENCES.get(self.current_char)
                if escaped is None:
                    e = InvalidTokenFault(f"Unknown escape sequence '\\{self.current_char}'")
                    e.line = line
                    raise e
                string_val += escaped
            else:
                string_val += self.current_char
            self.advance()

        if self.current_char != '"':
            e = InvalidTokenFault("Unterminated string literal: expected '\"'")
            e.line = line
            raise e

        self.advance() # Skip ending quote
        return Token(TokenType.STRING, string_val, line)

    def make_star(self):
        line = self.line
        self.advance()
        if self.current_char == '*':
            self.advance()
            return Token(TokenType.POW, None, line)
        return Token(TokenType.MUL, None, line)

    def make_equals(self):
        line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TokenType.EE, None, line)
        return Token(TokenType.ASSIGN, None, line)

    def make_not_equals(self):
        line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TokenType.NE, None, line)
        e = InvalidTokenFault("Expected '=' after '!'")
        e.line = line
        raise e

    def make_less_than(self):
        line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TokenType.LTE, None, line)
        return Token(TokenType.LT, None, line)

    def make_greater_than(self):
        line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TokenType.GTE, None, line)
        return Token(TokenType.GT, None, line)

    def get_tokens(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.current_char.isdigit() or self.current_char == '.':
                tokens.append(self.make_number())
            elif self.current_char in string.ascii_letters:
                tokens.append(self.make_identifier())
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '+':
                tokens.append(Token(TokenType.PLUS, None, self.line))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, None, self.line))
                self.advance()
            elif self.current_char == '*':
                tokens.append(self.make_star())
            elif self.current_char == '%':
                tokens.append(Token(TokenType.MOD, None, self.line))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIV, None, self.line))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, None, self.line))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, None, self.line))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, None, self.line))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TokenType.COLON, None, self.line))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TokenType.LBRACKET, None, self.line))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TokenType.RBRACKET, None, self.line))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TokenType.LBRACE, None, self.line))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TokenType.RBRACE, None, self.line))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '!':
                tokens.append(self.make_not_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            else:
                e = InvalidTokenFault(f"Illegal character: '{self.current_char}'")
                e.line = self.line
                raise e

        tokens.append(Token(TokenType.EOF))
        return tokens
