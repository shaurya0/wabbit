from typing import Union, List, Iterable
from Token import *
from Model import *
from Parser import *
from Compiler import *

# TODO: check that function declarations include a return statement


class TypeCheckerContext:
    def __init__(self, compiler: Compiler=None):
        self.functions = {}
        self.function_args = {}

        # Only one level of nesting is allowed and no support for closures
        self.global_vars = {}
        self.global_consts = {}
        self.scope_depth = -1
        self.scope_vars = []
        self.scope_consts = []
        self.expected_return_type = None

# Bool flag indicates whether or not variable is const
def lookup_var(name: str, context: TypeCheckerContext) -> (Expression, bool):

    if name in context.global_vars:
        return (context.global_vars[name], False)
    elif name in context.global_consts:
        return (context.global_consts[name], True)
    if context.scope_depth > 0:
        for sv in context.scope_vars:
            if name in sv:
                return (sv[name], False)
        for sc in context.scope_consts:
            if name in sc:
                return (sc[name], False)

        if name in context.function_args:
            return context.function_args[name], False

    raise ValueError(f"Could not find variable '{name}' in any scope")


def _run_type_checker(node: Node, context: TypeCheckerContext) -> TokenType:
    if isinstance(node, BinaryOp):
        lhs = node.left_expression
        rhs = node.right_expression

        lhs_token_type = _run_type_checker(lhs, context)
        rhs_token_type = _run_type_checker(rhs, context)
        if lhs_token_type != rhs_token_type:
            raise ValueError(f"Op '{node.op.lexeme}' type mismatch {lhs_token_type} != {rhs_token_type} in {node!r}")

        return lhs_token_type
    elif isinstance(node, VarDeclaration):
        if node.type_token is None:
            node.type_token = Token(_run_type_checker(node.expression, context), '')

        if context.scope_depth == 0:
            context.global_vars[node.name.lexeme] = node
        else:
            context.scope_vars[-1][node.name.lexeme] = node

        return node.type_token.token_type

    elif isinstance(node, ConstDeclaration):
        if node.type_token is None:
            node.type_token = Token(_run_type_checker(node.expression, context), '')

        if context.scope_depth == 0:
            context.global_consts[node.name.lexeme] = node
        else:
            context.scope_consts[-1][node.name.lexeme] = node

        return node.type_token.token_type

    elif isinstance(node, FunctionDeclaration):
        context.functions[node.name.lexeme] = node
        for p in node.params:
            context.function_args[p.name.token.lexeme] = p

        context.expected_return_type = node.return_type.token_type

        _run_type_checker(node.body, context)

        context.expected_return_type = None
        context.function_args = {}

        return node.return_type.token_type

    elif isinstance(node, LogicalExpression):
        if not node.op.token_type in Parser.LOGICAL_TOKEN_TYPES:
            raise ValueError(f"{node!r} ")

        lhs = node.left_expression
        rhs = node.right_expression

        lhs_token_type = _run_type_checker(lhs, context)
        rhs_token_type = _run_type_checker(rhs, context)

        if lhs_token_type != rhs_token_type:
            raise ValueError(f"Op '{node.op.lexeme}' type mismatch {lhs_token_type} != {rhs_token_type} in {node!r}")


        # if not hasattr(node.left_expression, 'type_token'):
        #     node.left_expression.type_token = lhs_token_type

        # if not hasattr(node.right_expression, 'type_token'):
        #     node.right_expression.type_token = rhs_token_type

        return lhs_token_type

    elif isinstance(node, Assignment):
        var, is_const = lookup_var(node.name.lexeme, context)
        if is_const:
            raise ValueError(f"Tried to assign to constant variable '{var.name.lexeme}'")
        expr_type = _run_type_checker(node.expression, context)

        if var.type_token.token_type != expr_type:
            raise ValueError(f"Tried to assign {expr_type}, but {node.name.lexeme} was previously declared with type {var.type_token.token_type}")

        node.type_token = expr_type
        return expr_type

    elif isinstance(node, Call):
        assert(isinstance(node.callee, Name))
        func_name = node.callee.token.lexeme
        if func_name not in context.functions:
            raise ValueError(f"Tried calling undefined function '{func_name}'")

        func_decl = context.functions[func_name]

        if node.arity != func_decl.arity:
            raise ValueError(f"Tried calling function '{func_name}' with {node.arity} arguments but function takes {func_decl.arity}")

        for i,(param,arg) in enumerate(zip(func_decl.params,node.arguments)):
            param_token_type = _run_type_checker(param, context)
            arg_token_type = _run_type_checker(arg, context)
            if param_token_type != arg_token_type:
                raise ValueError(f"Expected {arg_token_type} on parameter {i} in function {func_decl!r}, but got {param_token_type} at {node!r}")

        node.type_token = func_decl.return_type.token_type
        return func_decl.return_type.token_type

    elif isinstance(node, PrintStatement):
        _run_type_checker(node.expression, context)
    elif isinstance(node, IfStatement):
        _run_type_checker(node.condition, context)
        _run_type_checker(node.then_branch, context)
        if node.else_branch:
            _run_type_checker(node.else_branch, context)


    elif isinstance(node, WhileStatement):
        _run_type_checker(node.condition, context)
        _run_type_checker(node.body, context)

    elif isinstance(node, Return):
        token_type = _run_type_checker(node.expression, context)

        if token_type != context.expected_return_type:
            raise ValueError(f"function returned type {token_type}, but the declared return type is {context.expected_return_type}")

        node.token_type = token_type
        return token_type


    elif isinstance(node, Block):
        context.scope_depth += 1
        if context.scope_depth > 0 :
            context.scope_consts.append({})
            context.scope_vars.append({})

        for stmt in node.statements:
            _run_type_checker(stmt, context)

        if context.scope_depth > 0 :
            context.scope_vars.pop()
            context.scope_consts.pop()

        context.scope_depth -= 1

    elif isinstance(node, Literal):
        return node.type_token.token_type
    elif isinstance(node, Name):
        var, is_const = lookup_var(node.token.lexeme, context)
        token_type = _run_type_checker(var, context)
        node.token_type = token_type
        return token_type
    elif isinstance(node, Parameter):
        return node.type_token.token_type
    elif isinstance(node, UnaryOp):
        assert node.op.token_type == TokenType.MINUS
        token_type = _run_type_checker(node.expression, context)
        node.token_type = token_type
        return token_type



def run_type_checker(block: Block):
    context = TypeCheckerContext()
    _run_type_checker(block, context)
