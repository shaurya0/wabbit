from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    BANG = auto()
    EQUAL = auto()
    BANG_EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    IDENTIFIER = auto()
    CHAR = auto()
    INTEGER = auto()
    FLOAT = auto()
    TYPENAME_CHAR = auto()
    TYPENAME_INTEGER = auto()
    TYPENAME_FLOAT = auto()
    TYPENAME_BOOL = auto()

    ELSE = auto()
    FALSE = auto()
    FUNC = auto()
    IF = auto()
    PRINT = auto()
    RETURN = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    CONST = auto()
    BREAK = auto()
    CONTINUE = auto()
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    EOF = auto()

@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    line: int=-1

    def __init__(self, token_type: TokenType, lexeme: str, line: int=-1):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line

