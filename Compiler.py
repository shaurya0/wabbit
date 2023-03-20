from Model import *
from Token import *

from llvmlite import ir
import llvmlite.binding as llvm


class Compiler:
    def __init__(self):
        self.type_map = {
            TokenType.TYPENAME_INTEGER: ir.IntType(32),
            TokenType.TYPENAME_BOOL: ir.IntType(1),
            TokenType.TYPENAME_CHAR: ir.IntType(8),
            TokenType.TYPENAME_FLOAT: ir.FloatType()
            }

        self.module = ir.Module('main')
        self.builder = None
        self.variables = {}

        llvm.load_library_permanently('wabbit/print_char.so')
        self.define_char_printf()
        self.scope_depth = 0

        self.i = 0


    def define_char_printf(self):
        c_func_name = 'print_char'
        return_type = ir.VoidType()
        fnty = ir.FunctionType(return_type, [ir.IntType(8)])
        func = ir.Function(self.module, fnty, 'print_char')
        self.variables = {'print_char':(func,ir.VoidType())}

    def print_char(self,arg,Type):
        if arg == '\\n':
            arg='\n'
        print_char_func, _ = self.variables['print_char']

        arg = ord(arg)

        char_val = ir.Constant(ir.IntType(8), arg)
        # ptr = self.builder.alloca(char_val.type)
        # self.builder.store(char_val, ptr)

        # ptr = self.builder.gep(ptr, [zero, zero])
        # ptr = self.builder.bitcast(ptr, ir.IntType(8).as_pointer())

        self.builder.call(print_char_func, [char_val])



    def inc(self):
        self.i += 1
        return 1

    def lookup_var(self, name:str):
        if name in self.variables:
            return self.variables[name]


    def _compile(self, node: Node):
        if isinstance(node, Literal):
            llvm_type = self.type_map[node.type_token.token_type]
            return ir.Constant(llvm_type, node.value), llvm_type
        elif isinstance(node, VarDeclaration):
            llvm_type = self.type_map[node.type_token.token_type]
            value, typ = self._compile(node.expression)
            if self.scope_depth == 0:
                gvar = ir.GlobalVariable(self.module, llvm_type, node.name.lexeme)
                gvar.linkage='internal'
                gvar.initializer = value
                self.variables[node.name.lexeme] = gvar, llvm_type
            else:
                ptr = self.builder.alloca(llvm_type)
                self.builder.store(value, ptr)
                self.variables[node.name.lexeme] = ptr, llvm_type


        elif isinstance(node, ConstDeclaration):
            llvm_type = self.type_map[node.type_token.token_type]
            value,typ = self._compile(node.expression)
            assert isinstance(node.expression, Literal) or isinstance(value, ir.values.Constant)
            if self.scope_depth == 0:
                gvar = ir.GlobalVariable(self.module, llvm_type,
                                         node.name.lexeme)
                gvar.linkage = 'internal'
                gvar.global_constant = True
                gvar.initializer = value
                self.variables[node.name.lexeme] = gvar, llvm_type
            else:
                self.variables[node.name.lexeme] = value, typ



        elif isinstance(node, FunctionDeclaration):
            return_type = self.type_map[node.return_type.token_type]
            args = []
            for p in node.params:
                t = self.type_map[p.type_token.token_type]
                args.append(t)

            fn_type = ir.FunctionType(return_type, tuple(args))
            func = ir.Function(self.module, fn_type, name=node.name.lexeme)
            block = func.append_basic_block()
            self.builder = ir.IRBuilder(block)
            previous_variables = self.variables.copy()
            for i,p in enumerate(node.params):
                t = self.type_map[p.type_token.token_type]
                ptr = self.builder.alloca(t)
                self.builder.store(func.args[i], ptr)

                # params_ptr.append((ptr, t))
                self.variables[p.name.token.lexeme] = (ptr,t)

            self.scope_depth += 1
            self._compile(node.body)
            self.scope_depth -= 1

            self.variables = previous_variables
            self.variables[node.name.lexeme] = func, return_type

            self.builder = None
            return func, return_type


            # rest of function declaration will get implemented by block
        elif isinstance(node, Block):
            for stmt in node.statements:
                self._compile(stmt)


        elif isinstance(node, IfStatement):
            cond, typ = self._compile(node.condition)
            if node.else_branch:
                with self.builder.if_else(cond) as (true,false):
                    self.scope_depth += 1
                    with true:
                        self._compile(node.then_branch)
                    with false:
                        self._compile(node.else_branch)

                    self.scope_depth -= 1

            else:
                with self.builder.if_then(cond):
                    self.scope_depth += 1
                    self._compile(node.then_branch)
                    self.scope_depth -= 1

        elif isinstance(node, PrintStatement):
            # arg, type = self._compile(node.expression)
            ret = self.print_char(node.expression.value, type)
            ret_type = self.type_map[TokenType.TYPENAME_INTEGER]
            return ret, ret_type

        elif isinstance(node, WhileStatement):
            cond, typ =self._compile(node.condition)

            while_entry = self.builder.append_basic_block("while_entry" +
                                                          str(self.inc()))

            while_loop_end = self.builder.append_basic_block("while_end"+str(self.i))


            self.builder.cbranch(cond, while_entry, while_loop_end)

            # Setting the builder position-at-start
            self.builder.position_at_start(while_entry)
            self._compile(node.body)
            cond, typ =self._compile(node.condition)
            self.builder.cbranch(cond, while_entry, while_loop_end)
            self.builder.position_at_start(while_loop_end)


        elif isinstance(node, Call):
            func_name = node.callee.token.lexeme
            func,ret_type = self.variables[func_name]
            args = []
            types = []
            for arg in node.arguments:
                a, t = self._compile(arg)
                args.append(a)
                types.append(t)

            ret = self.builder.call(func,args)

            return ret, ret_type

        elif isinstance(node, Parameter):
            pass
        elif isinstance(node, Grouping):
            return self._compile(node.expression)
        elif isinstance(node, UnaryOp):
            assert isinstance(node.expression, Literal)
            assert node.op.token_type ==TokenType.MINUS
            # yeesh
            llvm_type = self.type_map[node.expression.type_token.token_type]
            return ir.Constant(llvm_type, -node.expression.value), llvm_type




        elif isinstance(node, Return):
            value, typ = self._compile(node.expression)
            self.builder.ret(value)

        elif isinstance(node, BinaryOp):
            lhs, lhs_type  = self._compile(node.left_expression)
            rhs, rhs_type  = self._compile(node.right_expression)

            if isinstance(lhs_type, ir.types.IntType) and lhs_type.width == 32:
                if node.op.token_type == TokenType.PLUS:
                    return self.builder.add(lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.MINUS:
                    return self.builder.sub(lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.STAR:
                    return self.builder.mul(lhs, rhs), lhs_type
            else:
                if node.op.token_type == TokenType.PLUS:
                    return self.builder.fadd(lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.MINUS:
                    return self.builder.fsub(lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.STAR:
                    return self.builder.fmul(lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.SLASH:
                    return self.builder.fdiv(lhs, rhs), lhs_type

                else:
                    raise ValueError(f"Unsupported binary operator {node.op}")

        elif isinstance(node, LogicalExpression):
            lhs, lhs_type  = self._compile(node.left_expression)
            rhs, rhs_type  = self._compile(node.right_expression)

            if isinstance(lhs_type, ir.types.IntType) and lhs_type.width == 32:
                if node.op.token_type == TokenType.LESS:
                    return self.builder.icmp_signed('<', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.LESS_EQUAL:
                    return self.builder.icmp_signed('<=', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.GREATER:
                    return self.builder.icmp_signed('>', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.GREATER_EQUAL:
                    return self.builder.icmp_signed('>=', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.EQUAL_EQUAL:
                    return self.builder.icmp_signed('==', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.BANG_EQUAL:
                    return self.builder.icmp_signed('!=', lhs, rhs), lhs_type
                else:
                    raise ValueError(f"Unsupported logical operator {node.op}")
            else:
                if node.op.token_type == TokenType.LESS:
                    return self.builder.fcmp_ordered('<', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.LESS_EQUAL:
                    return self.builder.fcmp_ordered('<=', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.GREATER:
                    return self.builder.fcmp_ordered('>', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.GREATER_EQUAL:
                    return self.builder.fcmp_ordered('>=', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.EQUAL_EQUAL:
                    return self.builder.fcmp_ordered('==', lhs, rhs), lhs_type
                elif node.op.token_type == TokenType.BANG_EQUAL:
                    return self.builder.fcmp_ordered('!=', lhs, rhs), lhs_type
                else:
                    raise ValueError(f"Unsupported logical operator {node.op}")




        elif isinstance(node, Name):
            if node.token.lexeme not in self.variables:
                raise ValueError(f"Could not find '{node.token.lexeme}' in allocated variables")

            ptr, typ = self.variables[node.token.lexeme]
            if isinstance(ptr, ir.instructions.AllocaInstr):
                return self.builder.load(ptr), typ
            else:
                return ptr, typ
        elif isinstance(node, Assignment):
            value, typ = self._compile(node.expression)
            if node.name.lexeme in self.variables:
                ptr, typ = self.variables[node.name.lexeme]
                self.builder.store(value, ptr)
            else:
                ptr = self.builder.alloca(typ)
                self.builder.store(value, ptr)
                self.variables[name] = ptr,typ


    def compile(self, block: Block):
        self._compile(block)
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module

        module = llvm.parse_assembly(str(self.module))
        module.verify()


        with llvm.create_mcjit_compiler(module, target_machine) as mcjit:
            def on_compiled(module, objbytes):
                open('wabbit/wabbit_module.o', 'wb').write(objbytes)

            mcjit.set_object_cache(on_compiled, lambda m:None)
            mcjit.finalize_object()

    def print(self):
        print(self.module)
