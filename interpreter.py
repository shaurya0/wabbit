from typing import Union, List
from Token import *
from Model import *

class InterpreterContext:
    def __init__(self, enclosing: "InterpreterContext"=None):
        self.env = {}
        self.enclosing_context = None

    def define(self, name:str, value: Literal):
        self.env[name] = value

    def lookup(self, name: str) -> Literal:
        if name in self.env:
            return self.env[name]

        return None


def interpret(node: Node):
    context = InterpreterContext()
    return interpret_node(node, context)



def interpret_node(node: Node, context: InterpreterContext):
    if isinstance(node, (Literal)):
        return node.value
    elif isinstance(node, PrintStatement):
        value = interpret_node(node.expression, context)
        print(value)
        return None
    elif isinstance(node, BinaryOp):
        lhs = interpret_node(node.left_expression, context)
        rhs = interpret_node(node.right_expression, context)
        if node.op.token_type == TokenType.PLUS:
            return lhs + rhs
        elif node.op.token_type ==TokenType.MINUS:
            return lhs - rhs
        elif node.op.token_type ==TokenType.STAR:
            return lhs * rhs
        elif node.op.token_type ==TokenType.SLASH:
            return lhs / rhs
        else:
            raise RuntimeError(f"failed to interpret {node!r}")
    elif isinstance(node, UnaryOp):
        if node.op.token_type ==TokenType.MINUS:
            expr = interpret_node(node.expression, context)
            assert(isinstance(node, (int, float)))
            return -expr
        elif node.op.token_type ==TokenType.BANG:
            expr = interpret_node(node.expression, context)
            assert(isinstance(node, bool))
            return not expr
        else:
            raise RuntimeError(f"failed to interpret {node!r}")

    elif isinstance(node, LogicalExpression):
        lhs = interpret_node(node.left_expression, context)
        rhs = interpret_node(node.right_expression, context)
        if node.op.token_type == TokenType.EQUAL_EQUAL:
            return lhs == rhs
        elif node.op.token_type ==TokenType.LESS:
            return lhs < rhs
        elif node.op.token_type ==TokenType.LESS_EQUAL:
            return lhs <= rhs
        elif node.op.token_type ==TokenType.GREATER:
            return lhs > rhs
        elif node.op.token_type ==TokenType.GREATER_EQUAL:
            return lhs >= rhs
        elif node.op.token_type ==TokenType.BANG_EQUAL:
            return lhs != rhs

        else:
            raise RuntimeError(f"failed to interpret {node!r}")

    # elif isinstance(node, IfStatement):

    elif isinstance(node, ConstDeclaration):
        name = node.name.lexeme
        value = interpret_node(node.expression, context)
        context.define(name, value)
        return None

    elif isinstance(node, Name):
        name = node.token.lexeme
        return context.lookup(name)

    elif isinstance(node, VarDeclaration):
        name = node.name.lexeme
        value = interpret_node(node.expression, context)
        context.define(name, value)
        return None

    elif isinstance(node, IfStatement):
        condition = interpret_node(node.condition, context)
        if condition:
            return interpret_node(node.then_branch, context)
        else:
            if node.else_branch:
                return interpret_node(node.else_branch, context)

    elif isinstance(node, Block):
        for stmt in node.statements:
            interpret_node(stmt, context)
        return None

    elif isinstance(node, Assignment):
        name = node.name.lexeme
        if name not in context.env:
            raise RuntimeError(f"Tried to assign undeclared variable {name}")

        value = interpret_node(node.expression, context)
        context.define(name, value)
        return None

    elif isinstance(node, WhileStatement):
        while interpret_node(node.condition, context):
            interpret_node(node.body, context)

        return None

