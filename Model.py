# %%
from typing import Union, List
from typing import TypeVar, Generic
from Token import *
class Node:
    def __init__(self):
        pass

class Expression(Node):
    def __init__(self):
        pass

class Statement(Node):
    def __init__(self):
        pass


class Literal:
    def __init__(self, value: str):
        assert(len(value) > 0)
        if value[0].isdigit():
            if value.isdigit():
                self.value = int(value)
                self.type_token = Token(TokenType.TYPENAME_INTEGER, 'int')
            else:
                self.value = float(value)
                self.type_token = Token(TokenType.TYPENAME_FLOAT, 'float')
        elif value == 'true':
            self.value = True
            self.type_token = Token(TokenType.TYPENAME_BOOL, 'bool')
        elif value == 'false':
            self.value = False
            self.type_token = Token(TokenType.TYPENAME_BOOL, 'bool')
        else:
            # char
            self.value = value
            self.type_token = Token(TokenType.TYPENAME_CHAR, 'char')

    def __add__(self, other):
        assert isinstance(self.value, (int,float))
        return Literal(self.value + other.value)

    def __sub__(self, other):
        assert isinstance(self.value, (int,float))
        return Literal(self.value - other.value)

    def __mul__(self, other):
        assert isinstance(self.value, (int,float))
        return Literal(self.value * other.value)

    def __truediv__(self, other):
        assert isinstance(self.value, (int,float))
        return Literal(self.value // other.value)

    def __mod__(self, other):
        return Literal(self.value % other.value)

    def __lt__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value < other.value

    def __le__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value <= other.value

    def __eq__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value == other.value

    def __ne__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value != other.value

    def __gt__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value > other.value

    def __ge__(self, other):
        assert isinstance(self.value, (int,float,str))
        return self.value >= other.value

    def __str__(self):
        return str(self.value)


class Float(Literal):
    def __init__(self, value):
        super().__init__(value)

class Integer(Literal):
    def __init__(self, value):
        super().__init__(value)

class Char(Literal):
    def __init__(self, value):
        super().__init__(value)

class Bool(Literal):
    def __init__(self, value):
        super().__init__(value)



class Name(Expression):
    def __init__(self, token: "Token"):
        self.token = token

    def __repr__(self):
        return f"Name {self.token.lexeme}"


class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    def __repr__(self):
        s = '{\n'
        s += "\t====Block===\n"

        for stmt in self.statements:
            s+= f'\t{stmt}\n'

        s += '}\n'

        return s

class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self):
        return f"Print({self.expression})"

class BinaryOp(Expression):
    def __init__(self, left_expression: Expression, op: "Token", right_expression: Expression):
        self.left_expression = left_expression
        self.op = op
        self.right_expression = right_expression

    def __repr__(self):
        return f"BinaryOp: {self.left_expression} {self.op.lexeme} {self.right_expression}"


class LogicalExpression(Expression):
    def __init__(self, left_expression: Expression, op: "Token", right_expression: Expression):
        # TODO: check that op is logical token type
        self.left_expression = left_expression
        self.op = op
        self.right_expression = right_expression

    def __repr__(self):
        return f"LogicalExpression: {self.left_expression} {self.op.lexeme} {self.right_expression}"

class UnaryOp(Expression):
    def __init__(self, op: "Token", expression: Expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        return f"UnaryOp: {self.op} {self.expression}"


class VarDeclaration(Statement):
    def __init__(self, name: "Token", expression: Expression=None, type_token: "Token"=None):
        self.name = name
        self.expression = expression
        self.type_token = type_token

    def __repr__(self):
        s = f"VarDeclaration: {self.name.lexeme}"
        if self.type_token:
            s += f'[{self.type_token.lexeme}]'
        if self.expression:
            s += f" = {self.expression};"

        return s



class ConstDeclaration(Statement):
    def __init__(self, name: "Token", expression: Expression, type_token: "Token"=None):
        self.name = name
        self.expression = expression
        self.type_token = type_token

    def __repr__(self):
        s = f"ConstDeclaration: {self.name.lexeme}"
        if self.type_token:
            s += f'[{self.type_token.lexeme}]'
        if self.expression:
            s += f" = {self.expression}"
        return s


class Assignment(Statement):
    def __init__(self, name: "Token", expression: Expression):
        self.name = name
        self.expression = expression

    def __repr__(self):
        return f"Assignment: {self.name.lexeme} = {self.expression}"



class IfStatement(Statement):
    def __init__(self, condition: Expression, then_branch: Block, else_branch: Block=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


    def __repr__(self):
        s = f"IfStatement: ({self.condition})\n"
        s += f'{self.then_branch}'


        if self.else_branch is not None:
            s += f'{self.else_branch}'

        return s


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Block=None):
        self.condition = condition
        self.body = body

    def __repr__(self):
        s = f"WhileStatement: ({self.condition})\n"
        s += f'{self.body}'

        return s


class Parameter(Expression):
    def __init__(self, name: Name, type_token: "Token"):
        self.name = name
        self.type_token = type_token

    def __repr__(self):
        return f"{self.name.token.lexeme} {self.type_token.lexeme}"



class FunctionDeclaration(Statement):
    def __init__(self, name: Name, body: Block, return_type: "Token", params: List[Parameter]=None):
        self.name = name
        self.params = params if params is not None else []
        self.body = body
        self.return_type = return_type
        self.arity = len(self.params)


    def __repr__(self):
        s = f"Function: {self.name.lexeme}("

        for ii,p in enumerate(self.params):
            s +=f'{p}'
            if ii < self.arity - 1:
                s +=', '
        s += f') {self.return_type.lexeme}\n'
        s += f'{self.body}'
        return s


class Call(Expression):
    def __init__(self, callee: Expression, paren: "Token", arguments: List[Expression]=None):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments if arguments is not None else []
        self.arity = len(self.arguments)

    def __repr__(self):
        s = f'Call {self.callee}('
        for ii,a in enumerate(self.arguments):
            s +=f'{a}'
            if ii < self.arity - 1:
                s +=', '
        s += ')\n'
        return s

class Grouping(Expression):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"({self.expression})"


class Return(Statement):
    def __init__(self, token: "Token", expression: Expression):
        self.expression = expression

    def __repr__(self):
        return f"Return {self.expression}"

class Break(Statement):
    def __init__(self, token: "Token"):
        self.token = token

    def __repr__(self):
        return "Break"


class Continue(Statement):
    def __init__(self, token: "Token"):
        self.token = token

    def __repr__(self):
        return "Continue"
