from Token import *
from typing import Union, List
import os

class Scanner:
    Keywords = {
    "else":   TokenType.ELSE,
    "false":  TokenType.FALSE,
    "func":   TokenType.FUNC,
    "if":     TokenType.IF,
    "print":  TokenType.PRINT,
    "return": TokenType.RETURN,
    "true":   TokenType.TRUE,
    "var":    TokenType.VAR,
    "while":  TokenType.WHILE,
    "const":  TokenType.CONST,
    "break":  TokenType.BREAK,
    "int":    TokenType.TYPENAME_INTEGER,
    "float":  TokenType.TYPENAME_FLOAT,
    "bool":   TokenType.TYPENAME_BOOL,
    "char":   TokenType.TYPENAME_CHAR,
    }

    def __init__(self, source: str):
        self.start = 0
        self.current = 0
        self.line = 1

        self.source = source
        self.tokens: List[Token] = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)


    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
            return
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
            return
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
            return
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
            return
        elif c == ',':
            self.add_token(TokenType.COMMA)
            return
        elif c == '.':
            self.add_token(TokenType.DOT)
            return
        elif c == '-':
            self.add_token(TokenType.MINUS)
            return
        elif c == '+':
            self.add_token(TokenType.PLUS)
            return
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
            return
        elif c == '*':
            self.add_token(TokenType.STAR)
            return
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            return
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            return
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            return
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            return
        elif c == '&':
            if self.match('&'):
                self.add_token(TokenType.LOGICAL_AND)
                return
            raise ValueError(f"Unterminated logical and found at {self.line}")
        elif c == '|':
            if self.match('|'):
                self.add_token(TokenType.LOGICAL_OR)
                return
            raise ValueError(f"Unterminated logical or found at {self.line}")
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                while (self.peek() != '*' and self.peek_next() !='/') and not self.is_at_end():
                    self.advance()
                if self.match('*') and self.match('/'):
                    return
                else:
                    raise ValueError(f"Invalid multiline comment starting at {self.line}")


            else:
                self.add_token(TokenType.SLASH)
            return

        elif c == ' ' or c == '\r' or c == '\t':
            # ignore whitespace
            return

        elif c == '\n':
            self.line += 1
            return
        elif c == "'":
            self.char()
            return
        else:
            if c.isdigit():
                self.number()
            elif c.isidentifier():
                self.identifier()
            else:
                raise ValueError(f"Unexpected character at line {self.line}: {c}")


    def match(self, c: str) -> bool:
        if self.is_at_end():
            return False

        if self.source[self.current] != c:
            return False

        self.current +=1
        return True


    def peek(self) -> str:
        if self.is_at_end():
            return '\0'

        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1]

    def advance(self) -> str:
        r = self.source[self.current]
        self.current += 1
        return r


    def add_token(self, token_type: TokenType):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, self.line))


    def identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start:self.current]
        if text in Scanner.Keywords:
            token_type = Scanner.Keywords[text]
        else:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)


    def number(self):
        token_type = TokenType.INTEGER
        while self.peek().isdigit():
            self.advance()


        if self.peek() == '.' and self.peek_next().isdigit():
            token_type = TokenType.FLOAT

            # consume "."
            self.advance()

            while self.peek().isdigit():
                self.advance()


        substr = self.source[self.start:self.current]
        if token_type == TokenType.INTEGER:
            value = substr
        else:
            value = substr

        self.add_token(token_type)

    def char(self):
        character = self.advance()
        char_terminator = self.advance()
        if character == '\\' and char_terminator.isalpha():
            import os
            char_terminator = "'"
            character = os.linesep
            self.advance()
        if char_terminator != "'":
            raise ValueError(f"Unterminated string at line {self.line}")

        char = character
        self.add_token(TokenType.CHAR)


    def scan_tokens(self) -> List[Token]:
        if len(self.tokens) > 0:
            return self.tokens

        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens

    def print_tokens(self):
        for t in self.tokens:
            print(t)
