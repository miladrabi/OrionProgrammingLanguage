
import errors as Error
from visitor import RTResult
from globalSymbolTable import GLOBAL_SYMBOL_TABLE
import interpreter as Interpreter
import symTable as SymbolTable
import token as Token
import ast
import math
import random


class Value:
    def __init__(self, value = None):
        self.value = value
        self.setPosition()
        self.setContext()

    def setPosition(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context = None):
        self.context = context
        return self

    def __repr__(self):
        return str(self.value)

class Number(Value):
    def __init__(self, value):
        super().__init__(value)
        if type(self.value) == float:
            self.length = len(str(self.value)) - 1
        else:
            self.length = len(str(self.value))


    def _len(self):
        return Number(self.length).setContext(self.context), None

    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setContext(self.context), None

    def sub(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context), None

    def mul(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context), None

    def div(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, Error.RTError(
                    other.pos_start,
                    other.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value / other.value).setContext(self.context), None

    def mod(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, Error.RTError(
                    other.pos_start,
                    other.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value % other.value).setContext(self.context), None

    def compare_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).setContext(self.context), None

    def compare_lt(self, other):

        if isinstance(other, Number):
            return Number(int(self.value < other.value)).setContext(self.context), None

    def compare_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).setContext(self.context), None
    
    def compare_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).setContext(self.context), None

    def compare_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).setContext(self.context), None

    def compare_neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).setContext(self.context), None

    def compare_and(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).setContext(self.context), None

    def compare_or(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).setContext(self.context), None

    def unary_not(self):
        return Number(0 if self.value > 0 else 1).setContext(self.context), None



class String(Value):
    def __init__(self, value):
        super().__init__(value)
        self.length = len(self.value)

    def _len(self):
        return Number(self.length).setContext(self.context), None

    def add(self, other):
        return self.concat(other)
    
    def concat(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).setContext(self.context).setPosition(self.pos_start, self.pos_end), None
        elif isinstance(other, Number) or isinstance(other, List):
            return String(self.value + str(other.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end), None

    def mul(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).setContext(self.context).setPosition(self.pos_start, self.pos_end), None

    def sub(self, other):
        if isinstance(other, String) or isinstance(other, Number) or isinstance(other, List):
            substr = str(other.value)
            strlen = len(substr)
            indexes = [i for i in range(len(self.value)) if self.value.startswith(substr, i)]
            limit = len(indexes) - 1
            index = 0
            result = ""
            i = 0
            while(index <= limit):
                if i == indexes[index]:
                    i += strlen
                    index += 1;
                result += self.value[i]
                i += 1
            if len(result) == 0:
                result = self.value
            return String(result).setContext(self.context).setPosition(self.pos_start, self.pos_end), None



class List(Value):
    def __init__(self, value):
        super().__init__(value)
        self.length = len(self.value)

    def _len(self):
        return Number(self.length).setContext(self.context), None

    def concat(self, other):
        if isinstance(other, List):
            return List(self.value + other.value).setContext(self.context).setPosition(self.pos_start, self.pos_end), None
        elif isinstance(other, Number) or isinstance(other, String):
            return List(self.value + other.value).setContext(self.context).setPosition(self.pos_start, self.pos_end), None
    
    def add(self, other):
        if isinstance(other, Number):
            result = []
            for i in self.value:
                if isinstance(i, Number):
                    result.append(i.add(other)[0])
                elif isinstance(i, String):
                    result.append(i.concat(other)[0])
                elif isinstance(i, List):
                    result.append(i.add(other)[0])
            return List(result).setContext(self.context).setPosition(self.pos_start, self.pos_end), None
        elif isinstance(other, List):
            listlen = other.length
            result = []
            if listlen != self.length:
                raise Exception("Two lists must be of the same size when adding toghether")
            for el in range(self.length):
                result.append(self.value[el].add(other.value[el])[0])
            return List(result).setContext(self.context).setPosition(self.pos_start, self.pos_end), None

    def sub(self, other):
        if isinstance(other, Number):
            result = []
            for i in self.value:
                if isinstance(i, Number):
                    result.append(i.sub(other)[0])
                elif isinstance(i, String):
                    result.append(i.sub(other)[0])
                elif isinstance(i, List):
                    result.append(i.sub(other)[0])
            return List(result).setContext(self.context).setPosition(self.pos_start, self.pos_end), None
        elif isinstance(other, List):
            listlen = other.length
            result = []
            if listlen != self.length:
                raise Exception("Two lists must be of the same size when subtracting toghether")
            for el in range(self.length):
                result.append(self.value[el].sub(other.value[el])[0])
            return List(result).setContext(self.context).setPosition(self.pos_start, self.pos_end), None



class BaseFunction(Value):
    def __init__(self, functionName, functionSymtab):
        super().__init__()
        self.name = functionName or "<inline>"
        self.symtab = functionSymtab

    def generate_new_context(self, parentContext):
        context = SymbolTable.Context(self.name, parentContext, self.pos_start)
        context.symbolTable = SymbolTable.SymbolTable(self.symtab)
        return context

    def check_args(self, arg_names, arguments, exec_ctx):
        res = RTResult()
        if len(arguments) > len(arg_names):
            return res.failure(Error.RTError(self.pos_start, self.pos_end, f'Function \'{self.name}\' requires {len(arg_names)} arguments, {len(arguments) - len(arg_names)} more provided', exec_ctx))
        if len(arguments) < len(arg_names):
            return res.failure(Error.RTError(self.pos_start, self.pos_end, f'Function \'{self.name}\' requires {len(arg_names)} arguments, {len(arguments)} provided, needs {len(arg_names) - len(arguments)} more arguments', exec_ctx))
        return res.success(None)

    def populate_args(self, arg_names, arguments, exec_ctx):
        for i in range(len(arg_names)):
            name = arg_names[i]
            prop = SymbolTable.Symbol(Token.cons.LET, arguments[i])
            exec_ctx.symbolTable.define(name, prop)

    def check_and_populate_args(self, arg_names, arguments, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, arguments, exec_ctx))
        if res.error: return res
        self.populate_args(arg_names, arguments, exec_ctx)
        return res.success(None)

class Function(BaseFunction):
    def __init__(self, functionName, functionArguments, functionBody, functionSymtab):
        super().__init__(functionName, functionSymtab)
        self.arg_names = functionArguments
        self.body = functionBody

    def __repr__(self):
        return f'<Function {self.name}>'


    def execute(self, arguments, parentContext):
        res = RTResult()
        newContext = self.generate_new_context(parentContext)

        self.check_and_populate_args(self.arg_names, arguments, newContext)
        
        interp = Interpreter.Interpreter(self.body)
        result = res.register(interp.Interpret(newContext))
        if res.error: return res
        return res.success(result)


class BuiltInFunction(BaseFunction):
    def __init__(self, functionName):
        super().__init__(functionName, SymbolTable.SymbolTable())

    def execute(self, arguments, parentContext = None):
        res = RTResult()
        newContext = self.generate_new_context(parentContext)

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_execute_method)

        res.register(self.check_and_populate_args(method.arg_names, arguments, newContext))
        if res.error: return res

        result = res.register(method(newContext))
        if res.error: return res

        return res.success(result)

    def no_execute_method(self, args, parentContext = None):
        raise Exception(f'No execute_{self.name} method found')

    def __repr__(self):
        return f'<Built-in function {self.name}>'

    ## BUILT_IN FUNCTIONS
    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_range(self, exec_ctx):
        end = exec_ctx.symbolTable.get('end').type
        if not isinstance(end, Number):
            return RTResult().failure(Error.RTError(
                self.pos_start,
                self.pos_end,
                "'range' function argument must be an integer",
                exec_ctx
            ))
        end = end.value
        result = range(end)
        result = list(result)
        for index in range(len(result)):
            result[index] = Number(result[index])
        result = List(result)
        return RTResult().success(result)
    execute_range.arg_names = ['end']

    def execute_len(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('argument').type
        return RTResult().success(Number(arg.length))
    execute_len.arg_names = ['argument']

    def execute_is_number(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('argument').type
        if isinstance(arg, Number):
            return RTResult().success(Number(1))
        else:
            return RTResult().success(Number(0))
    execute_is_number.arg_names = ['argument']

    def execute_to_number(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('argument').type
        if isinstance(arg, List):
            return RTResult().failure(Error.RTError(
                self.pos_start,
                self.pos_end,
                f"Can not convert 'List' to Number.",
                exec_ctx
            ))
        try:
            if isinstance(arg, Number):
                if type(arg.value) == float:
                    value = float(arg.value)
                else:
                    value = int(arg.value)
            elif isinstance(arg, String):
                if '.' in arg.value:
                    value = float(arg.value)
                else:
                    value = int(arg.value)
        except:
            return RTResult().failure(Error.RTError(
                self.pos_start,
                self.pos_end,
                f"Can not convert {arg.value} to type Number",
                exec_ctx
            ))
        return RTResult().success(Number(value))
    execute_to_number.arg_names = ['argument']

    def execute_string(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('arguments')
        return RTResult().success(String(arg.value))
    execute_string.arg_names = ['argument']

    def execute_list(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('arguments').type
        if isinstance(arg, Number):
            return RTResult().success(List([arg.value]))
        elif isinstance(arg, String):
            result = []
            for i in arg.value:
                result.append(i)
            return RTResult().success(List(result))
        else:
            return RTResult().success(List(arg.value))
    execute_list.arg_names = ['arguments']

    def execute_is_string(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('argument').type
        if isinstance(arg, String):
            return RTResult().success(Number(1))
        else:
            return RTResult().success(Number(0))
    execute_is_string.arg_names = ['argument']
    
    def execute_is_list(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('argument').type
        if isinstance(arg, List):
            return RTResult().success(Number(1))
        else:
            return RTResult().success(Number(0))
    execute_is_list.arg_names = ['argument']


    def execute_random(self, exec_ctx):
        number = exec_ctx.symbolTable.get('number').type
        if isinstance(number, Number):
            result = random.randint(1, number.value)
            return RTResult().success(Number(result))
        else:
            return RTResult().failure(Error.RTError(
                self.pos_start,
                self.pos_end,
                f"'random' argument should be number",
                exec_ctx
            ))
    execute_random.arg_names = ['number']

    def execute_type(self, exec_ctx):
        arg = exec_ctx.symbolTable.get('arguments').type
        if isinstance(arg, Number):
            return RTResult().success(String('<Type Number>'))
        elif isinstance(arg, String):
            return RTResult().success(String('<Type String>'))
        else:
            return RTResult().success(String('<Type List>'))
    execute_type.arg_names = ['arguments']

    def execute_prompt(self, exec_ctx):
        msg = exec_ctx.symbolTable.get('message').type
        result = input(msg.value)
        return RTResult().success(String(result))
    execute_prompt.arg_names = ['message']


BuiltInFunction.input       = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("input")).copy()
BuiltInFunction.range       = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("range")).copy()
BuiltInFunction.len         = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("len")).copy()
BuiltInFunction.is_number   = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("is_number")).copy()
BuiltInFunction.is_string   = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("is_string")).copy()
BuiltInFunction.is_list     = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("is_list")).copy()
BuiltInFunction.to_number   = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("to_number")).copy()
BuiltInFunction.string      = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("string")).copy()
BuiltInFunction.list        = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("list")).copy()
BuiltInFunction.type        = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("type")).copy()
BuiltInFunction.prompt      = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("prompt")).copy()
BuiltInFunction.random      = SymbolTable.Symbol(Token.cons.FUNCTION, BuiltInFunction("random")).copy()

GLOBAL_SYMBOL_TABLE.define("input", BuiltInFunction.input)
GLOBAL_SYMBOL_TABLE.define("range", BuiltInFunction.range)
GLOBAL_SYMBOL_TABLE.define("len", BuiltInFunction.len)
GLOBAL_SYMBOL_TABLE.define("is_number", BuiltInFunction.is_number)
GLOBAL_SYMBOL_TABLE.define("is_string", BuiltInFunction.is_string)
GLOBAL_SYMBOL_TABLE.define("is_list", BuiltInFunction.is_list)
GLOBAL_SYMBOL_TABLE.define("to_number", BuiltInFunction.to_number)
GLOBAL_SYMBOL_TABLE.define("string", BuiltInFunction.string)
GLOBAL_SYMBOL_TABLE.define("list", BuiltInFunction.list)
GLOBAL_SYMBOL_TABLE.define("type", BuiltInFunction.type)
GLOBAL_SYMBOL_TABLE.define("prompt", BuiltInFunction.prompt)
GLOBAL_SYMBOL_TABLE.define("random", BuiltInFunction.random)

MATH_PI = SymbolTable.Symbol(Token.cons.CONST, Number(math.pi)).copy()
GLOBAL_SYMBOL_TABLE.define("MATH_PI", MATH_PI)
TRUE = SymbolTable.Symbol(Token.cons.CONST, Number(1)).copy()
GLOBAL_SYMBOL_TABLE.define("TRUE", TRUE)
FALSE = SymbolTable.Symbol(Token.cons.CONST, Number(0)).copy()
GLOBAL_SYMBOL_TABLE.define("FALSE", FALSE)
NULL = SymbolTable.Symbol(Token.cons.CONST, Number(None)).copy()
GLOBAL_SYMBOL_TABLE.define("NULL", NULL)