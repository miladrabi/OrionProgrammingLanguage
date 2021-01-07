import lexer as Lexer
import parser as Parser
import typeSystem as Type
import interpreter as Interpreter
import sys

name = sys.argv[1]
file = open(name, 'r')
program, fileName = file.read(), file.name

lexer = Lexer.Lexer(fileName, program)
parser = Parser.Parser(lexer)
#program = parser.parse()
#program = program.node
interp = Interpreter.Interpreter(parser)
interp.Interpret()
