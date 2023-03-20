from Model import *
from Scanner import *
from Token import *
from Parser import *
from TypeChecker import *
from format import format_wabbit, FormatContext
from interpreter import *
from Compiler import *
import argparse


parser = argparse.ArgumentParser(
                    prog='Wabbit compiler/interpreter')

parser.add_argument('-f', '--filename', required=False)
parser.add_argument('--print_tokens', action='store_true')
parser.add_argument('--print_statements', action='store_true')

parser.add_argument('--log_level',
                    action='store_true', default='info')
parser.add_argument('--test_format', action='store_true')
parser.add_argument('--test_interpreter', action='store_true')
parser.add_argument('--run_type_checker', action='store_true')
parser.add_argument('--compile', action='store_true')



def test_format():
    import operator
    mul = Token(TokenType.STAR, '*')
    div = Token(TokenType.SLASH, '/')
    add = Token(TokenType.PLUS, '+')
    lt = Token(TokenType.LESS, '<')
    le = Token(TokenType.LESS_EQUAL, '<=')
    eq = Token(TokenType.EQUAL_EQUAL, '==')
    float_token = Token(TokenType.FLOAT, "float")
    int_token = Token(TokenType.INTEGER, "int")
    def NamedToken(name: str):
        return Name(token=Token(TokenType.IDENTIFIER, lexeme=name))


    prog1 = PrintStatement(Integer("42"))
    format_wabbit(prog1, FormatContext())

    prog2 = Block([PrintStatement(Integer("42")), PrintStatement(Float("2.3"))])
    format_wabbit(prog2, FormatContext())

    prog3 = Block([PrintStatement(BinaryOp(Integer("2"), add, Integer("3"))), PrintStatement(UnaryOp(Token(TokenType.MINUS, "-"), Integer("5")))])
    format_wabbit(prog3, FormatContext())


    def program4():
        s1 = ConstDeclaration(Token(TokenType.IDENTIFIER, "pi"), Float("3.14159"))
        s2 = VarDeclaration(Token(TokenType.IDENTIFIER, "radius"), Float("4.0"))
        s3 = VarDeclaration(Token(TokenType.IDENTIFIER, "perimeter"), type_=float_token)
        bop1=BinaryOp(
            Float("2.0"), mul,
            BinaryOp(NamedToken("radius"), mul, NamedToken('pi')))
        s4 = Assignment(name=Token(TokenType.IDENTIFIER,'perimeter'), expression=bop1)
        s5 = PrintStatement(NamedToken('perimeter'))

        return Block([s1,s2,s3,s4,s5])

    print("=========================Program 4=====================")
    prog4 = program4()
    print(format_wabbit(prog4, FormatContext()))
    print()


    def program5():
        s1 = VarDeclaration(Token(TokenType.IDENTIFIER, "a"), Integer("2"), type_=int_token)
        s2 = VarDeclaration(Token(TokenType.IDENTIFIER, "b"), Integer("3"), type_=int_token)
        then_branch = PrintStatement(NamedToken("a"))
        else_branch = PrintStatement(NamedToken("b"))
        s3 = IfStatement(LogicalExpression(NamedToken("a"), lt, NamedToken("b")), then_branch, else_branch)

        return Block([s1,s2, s3])

    prog5 = program5()
    print("=========================Program 5=====================")
    print(format_wabbit(prog5, FormatContext()))
    print()



    def program6():
        s1 = VarDeclaration(Token(TokenType.IDENTIFIER, "x"), Integer("1"), type_=int_token)
        s2 = VarDeclaration(Token(TokenType.IDENTIFIER, "fact"), Integer("1"), type_=int_token)

        condition=LogicalExpression(NamedToken("x"), lt, Integer("11"))
        body = []
        bop1 = BinaryOp(NamedToken("fact"), mul, NamedToken("x"))
        body.append( Assignment(Token(TokenType.IDENTIFIER, "fact"), bop1) )
        body.append( Assignment(Token(TokenType.IDENTIFIER, "x"), BinaryOp(NamedToken("x"), add, Integer("1"))) )
        body.append( PrintStatement(NamedToken("fact")) )
        s3 = WhileStatement(condition, Block(body))
        return Block([s1,s2,s3])

    prog6 = program6()
    print("=========================Program 6=====================")
    print(format_wabbit(prog6, FormatContext()))
    print()


    def program7():
        body = []
        params = []
        params.append(Parameter(Name(Token(TokenType.IDENTIFIER, "n")), Token(TokenType.INTEGER, "int")))
        params.append(Parameter(Name(Token(TokenType.IDENTIFIER, "flag")), Token(TokenType.BOOL, "int")))
        function_body = []
        function_body.append(VarDeclaration(Token(TokenType.IDENTIFIER, "factor"), Integer("2"), type_=int_token))
        function_body.append(VarDeclaration(Token(TokenType.IDENTIFIER, "divisor"), type_=int_token))

        while_cond_expr = BinaryOp(NamedToken("n"), div, Integer("2"))
        while_condition = LogicalExpression(NamedToken("factor"), le, while_cond_expr)
        while_body = []
        while_body.append( Assignment(Token(TokenType.IDENTIFIER, "divisor"), BinaryOp(NamedToken("n"), div, NamedToken("factor"))) )
        then_branch = Block([Return(Token(TokenType.FALSE, "false"))])
        if_bop = BinaryOp(NamedToken("factor"), mul, NamedToken("divisor"))
        if_cond = LogicalExpression(if_bop, eq, NamedToken("n"))
        if_stmt = IfStatement(if_cond, then_branch)
        while_body.append(if_stmt)
        while_body.append( Assignment(Token(TokenType.IDENTIFIER, "factor"), BinaryOp(NamedToken("factor"), add, Integer("1"))) )
        while_stmt = WhileStatement(while_condition, Block(while_body))
        return_stmt = Return(Name(Token(TokenType.TRUE, "true")))

        function_body.append(while_stmt)
        function_body.append(return_stmt)
        function_return_type = Token(TokenType.BOOL, "bool")
        function_decl = FunctionDeclaration(name=Name(Token(TokenType.IDENTIFIER,
                                                       "isprime")),
                                            body=Block(function_body),
                                            return_type=function_return_type,
                                            params=params)
        body.append(function_decl)
        body.append(PrintStatement(Call(NamedToken("isprime"), Token(TokenType.LEFT_PAREN, "("), [Integer("15")])))
        body.append(PrintStatement(Call(NamedToken("isprime"), Token(TokenType.LEFT_PAREN, "("), [Integer("37")])))

        return Block(body)




    prog7 = program7()
    print("=========================Program 7=====================")
    print(format_wabbit(prog7, FormatContext()))
    print()



def test_interpreter():
    mul = Token(TokenType.STAR, '*')
    div = Token(TokenType.SLASH, '/')
    add = Token(TokenType.PLUS, '+')
    lt = Token(TokenType.LESS, '<')
    le = Token(TokenType.LESS_EQUAL, '<=')
    eq = Token(TokenType.EQUAL_EQUAL, '==')
    float_token = Token(TokenType.FLOAT, "float")
    int_token = Token(TokenType.INTEGER, "int")
    def NamedToken(name: str):
        return Name(token=Token(TokenType.IDENTIFIER, lexeme=name))

    def program6():
        s1 = VarDeclaration(Token(TokenType.IDENTIFIER, "x"), Integer("1"), type_=int_token)
        s2 = VarDeclaration(Token(TokenType.IDENTIFIER, "fact"), Integer("1"), type_=int_token)

        condition=LogicalExpression(NamedToken("x"), lt, Integer("11"))
        body = []
        bop1 = BinaryOp(NamedToken("fact"), mul, NamedToken("x"))
        body.append( Assignment(Token(TokenType.IDENTIFIER, "fact"), bop1) )
        body.append( Assignment(Token(TokenType.IDENTIFIER, "x"), BinaryOp(NamedToken("x"), add, Integer("1"))) )
        body.append( PrintStatement(NamedToken("fact")) )
        s3 = WhileStatement(condition, Block(body))
        return Block([s1,s2,s3])

    prog6 = program6()
    interpret(prog6)





args = parser.parse_args()
def main():
    if args.test_format:
        test_format()
    elif args.test_interpreter:
        test_interpreter()
    else:
        with open(args.filename, 'r') as fid:
            source = fid.read()
            scanner = Scanner(source)
            tokens = scanner.scan_tokens()
            if args.print_tokens:
                scanner.print_tokens()
            parser = Parser(tokens)
            block = parser.parse()
            if args.print_statements:
                for s in block.statements:
                    print(s)

            if args.run_type_checker or args.compile:
                # TypeChecker mutates block and adds type token attribute to expression nodes
                run_type_checker(block)

                if args.compile:
                    compiler = Compiler()
                    compiler.compile(block)
                    compiler.print()







if __name__ == '__main__':
    main()
