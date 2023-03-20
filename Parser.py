from typing import Union, List, Iterable
from Token import *
from Model import *


class Parser:
    VAR_TOKEN_TYPES = (TokenType.TYPENAME_INTEGER, TokenType.TYPENAME_FLOAT, TokenType.TYPENAME_CHAR, TokenType.TYPENAME_BOOL)
    LOGICAL_TOKEN_TYPES = (TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL, TokenType.GREATER,
                           TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Block:
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())

        return Block(statements)


    def statement(self) -> Union[Statement, Expression]:
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.VAR):
            return self.var_declaration()
        elif self.match(TokenType.CONST):
            return self.const_declaration()
        elif self.match(TokenType.BREAK):
            return self.break_statement()
        elif self.match(TokenType.CONTINUE):
            return self.continue_statement()
        elif self.match(TokenType.FUNC):
            return self.function_declaration()
        elif self.match(TokenType.LEFT_BRACE):
            return self.block()

        return self.expression_statement()


    def expression_statement(self) -> Expression:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ; after expression')
        return expr


    def expression(self):
        return self.assignment()


    def assignment(self):
        expr = self.orterm()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            assert(isinstance(expr, Name))
            return Assignment(expr.token, value)

        return expr


    def orterm(self):
        lhs = self.andterm()
        while self.match(TokenType.LOGICAL_OR):
            operator = self.previous()
            rhs = self.andterm()
            lhs = LogicalExpression(lhs, operator, rhs)
        return lhs

    def andterm(self):
        lhs = self.relterm()
        while self.match(TokenType.LOGICAL_AND):
            operator = self.previous()
            rhs = self.relterm()
            lhs = LogicalExpression(lhs, operator, rhs)
        return lhs

    def relterm(self):
        lhs = self.sumterm()
        while self.match(Parser.LOGICAL_TOKEN_TYPES):
            operator = self.previous()
            rhs = self.sumterm()
            lhs = LogicalExpression(lhs, operator, rhs)
        return lhs


    def sumterm(self):
        lhs = self.multerm()
        while self.match((TokenType.PLUS, TokenType.MINUS)):
            operator = self.previous()
            rhs = self.multerm()
            lhs = BinaryOp(lhs, operator, rhs)

        return lhs

    def multerm(self):
        lhs = self.factor()
        while self.match((TokenType.STAR, TokenType.SLASH)):
            operator = self.previous()
            rhs = self.factor()
            lhs = BinaryOp(lhs, operator, rhs)

        return lhs


    def factor(self):
        if self.match((TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            expr = self.factor()
            return UnaryOp(operator, expr)

        return self.call()


    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected identifier after func keyword")
        lparen = self.consume(TokenType.LEFT_PAREN, "Expected left paren after identifier in function declaration")
        params = []
        if self.match(TokenType.IDENTIFIER):
            arg_name = self.previous()
            type_token = self.consume(Parser.VAR_TOKEN_TYPES, "Expected typename in function argument")
            params.append(Parameter(Name(arg_name), type_token))
            while self.match(TokenType.COMMA):
                arg_name = self.consume(TokenType.IDENTIFIER, "Expected identifier after comma in function declaration arguments")
                type_token = self.consume(Parser.VAR_TOKEN_TYPES,
                                 "Expected typename in function argument")
                params.append(Parameter(Name(arg_name), type_token))
        self.consume(TokenType.RIGHT_PAREN, "Expected right paren after function arguments in declaration")
        return_type = self.consume(Parser.VAR_TOKEN_TYPES, "Expected return type annotation after function arguments")
        self.consume(TokenType.LEFT_BRACE, 'Expected left brace after function arguments for function body')
        body = self.block()

        return FunctionDeclaration(name, body, return_type, params)


    def call(self):
        expr = self.literal()

        if self.match(TokenType.LEFT_PAREN):
            paren = self.previous()
            arguments = []
            while not self.match(TokenType.RIGHT_PAREN):
                arguments.append(self.expression())
                if self.check(TokenType.COMMA):
                    self.advance()

            return Call(expr, paren, arguments)

        return expr

    def literal(self) -> Expression:
        if self.match(TokenType.TRUE):
            return Bool(self.previous().lexeme)
        elif self.match(TokenType.FALSE):
            return Bool(self.previous().lexeme)
        elif self.match(TokenType.INTEGER):
            return Integer(self.previous().lexeme)
        elif self.match(TokenType.FLOAT):
            return Float(self.previous().lexeme)
        elif self.match(TokenType.CHAR):
            return Char(self.previous().lexeme.replace("'", ""))
        elif self.match(TokenType.IDENTIFIER):
            identifier = self.previous()
            return Name(identifier)

        elif self.match(Parser.VAR_TOKEN_TYPES):
            to_cast_type = self.previous()
            return Name(to_cast_type)

        # grouping e.g. (a+b)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected right paren after grouping")
            return Grouping(expr)

        raise ValueError(f"Expected expression")

    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.statement())

        self.consume(TokenType.RIGHT_BRACE, "")
        return Block(statements)


    def if_statement(self):
        condition = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expected { after if condition")
        then_branch = self.block()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStatement(condition, then_branch, else_branch)

    def print_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value.")
        return PrintStatement(expr)


    def const_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected identifier after const keyword")
        type_token = None
        initializer = None
        if self.match(Parser.VAR_TOKEN_TYPES):
            type_token = self.previous()

        self.consume(TokenType.EQUAL, "Const var must have initializer")

        initializer = self.expression()
        if type_token is None:
            # TODO: type inference on initializer
            pass

        self.consume(TokenType.SEMICOLON, "Expected semicolon after const declaration")

        return ConstDeclaration(name, initializer, type_token)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected identifier after var keyword")
        type_token = None
        initializer = None
        if self.match(Parser.VAR_TOKEN_TYPES):
            type_token = self.previous()

        if type_token is None and not self.check(TokenType.EQUAL):
            raise ValueError(f"Var declaration does not specify type and doesn't have initializer")

        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected semicolon after variable declaration")

        return VarDeclaration(name, initializer, type_token)

    def while_statement(self):
        condition = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expected { after while condition")
        body = self.block()
        return WhileStatement(condition, body)

    def return_statement(self):
        keyword = self.previous()
        return_expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected semicolon after return keyword")
        return Return(keyword, return_expr)

    def break_statement(self):
        break_token = self.previous()
        self.consume(TokenType.SEMICOLON, "Expected semicolon after break")
        return Break(break_token)

    def continue_statement(self):
        continue_token = self.previous()
        self.consume(TokenType.SEMICOLON, "Expected semicolon after continue")
        return Continue(continue_token)

    def match(self, token_types: Union[Iterable[TokenType],TokenType]) -> bool:
        if not isinstance(token_types, Iterable):
            token_types = [token_types]

        for tt in token_types:
            if self.check(tt):
                self.advance()
                return True
        return False

    def is_at_end(self) -> Token:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current -1]

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().token_type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def consume(self, token_types: Union[Iterable[TokenType], TokenType],
                error_message: str) -> Token:
        if not isinstance(token_types, Iterable):
            token_types = [token_types]

        for tt in token_types:
            if self.check(tt):
                return self.advance()

        raise ValueError(f"ParseError on token: {self.peek()} {error_message}")
