import visitor as Visitor
import token as Token
import ast
import errors as Error

class Symbol:
    def __init__(self, kind, type_):
        self.kind = kind
        self.type = type_

    def copy(self):
        return self


class SymbolTable:
    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent
        
    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def define(self, name, value):
        self.symbols[name] = value

    def update(self, name, value, context):
        res = Visitor.RTResult()
        if self.symbols[name].kind == Token.cons.CONST:
            return res.failure(Error.RTError(value.pos_start, value.pos_end, f"Constant variable '{name}' is immutable", context))
        # type.value = value.value
        self.symbols[name].type = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    def __init__(self, display_name, parent = None, parent_entry_position = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_position = parent_entry_position
        self.symbolTable = None

class FunctionContext:
    def __init__(self, functionName, functionArgs, functionBody, symtab, varnames):
        self.name     = functionName
        self.args     = functionArgs
        self.body     = functionBody
        self.symtab   = symtab
        self.varnames = varnames