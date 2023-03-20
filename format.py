from Model import *
from dataclasses import dataclass
from typing import Union

@dataclass
class FormatContext:
    indent: int = 0


class StringBuilder:
    def __init__(self, ctx:FormatContext):
        self.ctx = ctx
        self.indent_str = ' '*ctx.indent
        self.result = ''

    def add(self, s, newline=False):
        self.result += self.indent_str + s

        if newline:
            self.result += '\n'


    def get_result(self):
        return self.result




def format_wabbit(node: Union[Expression,Statement], ctx: FormatContext):
    indent = ' '*ctx.indent
    if isinstance(node, PrintStatement):
        return indent + 'print ' + format_wabbit(node.expression, ctx) + ';\n'
    elif isinstance(node, Integer):
        return str(node)
    elif isinstance(node, Char):
        return str(node)
    elif isinstance(node, Float):
        return str(node)
    elif isinstance(node, Bool):
        return str(node)
    elif isinstance(node, (BinaryOp, LogicalExpression)):
        return f'{format_wabbit(node.left_expression, ctx)} {node.op.lexeme} {format_wabbit(node.right_expression, ctx)}'
    elif isinstance(node, Block):
        return ''.join([f'{format_wabbit(stmt, ctx)}' for stmt in node.statements])
    elif isinstance(node, UnaryOp):
        return f'{node.op.lexeme}{format_wabbit(node.expression, ctx)}'
    elif isinstance(node, VarDeclaration):
        s = indent + f'var {node.name.lexeme}'
        if node.type_token is not None:
            s += f' {node.type_token.lexeme}'
        if node.expression is None:
            s +=';\n'
        else:
            s += f' = {format_wabbit(node.expression, ctx)};\n'
        return s
    elif isinstance(node, ConstDeclaration):
        s = indent + f'const {node.name.lexeme}'
        if node.type_token is not None:
            s += f' {node.type_token.lexeme}'

        if node.expression is None:
            s +=';\n'
        else:
            s += f' = {format_wabbit(node.expression, ctx)};\n'

        return s
    elif isinstance(node, Assignment):
        return indent + f'{node.name.lexeme} = {format_wabbit(node.expression, ctx)};\n'
    elif isinstance(node, Name):
        return f'{node.token.lexeme}'
    elif isinstance(node, IfStatement):
        s = indent + f'if {format_wabbit(node.condition, ctx)}'
        s += ' {\n'
        ctx.indent += 4
        s += f'{format_wabbit(node.then_branch, ctx)}'
        ctx.indent -= 4
        s += indent + '}\n'

        if node.else_branch:
            s += '{\n'
            ctx.indent += 4
            s += f'{format_wabbit(node.else_branch, ctx)}'
            ctx.indent += 4
            s += '}\n'
        return s

    elif isinstance(node, WhileStatement):
        s = indent + f'while {format_wabbit(node.condition, ctx)}'
        s += ' {\n'
        if node.body:
            ctx.indent += 4
            s += f'{format_wabbit(node.body, ctx)}'
            ctx.indent -= 4
        s += indent + '}\n'

        return s

    elif isinstance(node, FunctionDeclaration):
        s = indent + f'func {node.name.token.lexeme}('

        for ii,p in enumerate(node.params):
            s += f'{p.name.token.lexeme} {p.type_token.lexeme}'
            if (ii + 1) < node.arity:
                s += ', '
        s += f') {node.return_type.lexeme}'
        s += '{\n'
        ctx.indent += 4
        s += format_wabbit(node.body, ctx)
        ctx.indent -= 4
        s += '}\n'
        return s

    elif isinstance(node, Call):
        s = indent + f'{format_wabbit(node.callee, ctx)}('
        arity = len(node.arguments)
        for ii,arg in enumerate(node.arguments):
            if (ii + 1) < arity:
                s += ', '
            s += f'{format_wabbit(arg, ctx)}'
        s += ')'
        return s
    elif isinstance(node, Return):
        return indent + f'return {format_wabbit(node.expression, ctx)};\n'
    elif isinstance(node, Break):
        return indent + 'break;\n'
    elif isinstance(node, Continue):
        return indent + 'continue;\n'

    else:
        raise ValueError(f"Unknown node {node!r}")



