import visitor as visitor
import token as Token
import typeSystem as Type
import parser
import errors as Error
import symTable as SymbolTable
import ast
from globalSymbolTable import GLOBAL_SYMBOL_TABLE

class Interpreter(visitor.Visitor):
    def __init__(self, program, args = None, GlobalSymtab = None):
        if isinstance(program, parser.Parser):
            parseResult = program.parse()
            self.ast = parseResult
        else:
            self.ast = parser.ParseResult()
            self.ast.error = None
            self.ast.node = program


    def Interpret(self, context = None):
        if self.ast.error:
            print(self.ast.error.as_string())
        else:
            if context:
                self.symtab = context.symbolTable
            else:
                context = SymbolTable.Context('<main>')
                context.symbolTable = GLOBAL_SYMBOL_TABLE
                self.symtab = context.symbolTable
            result = self.visit(self.ast.node, context)
            if result:
                if result.error:
                    print(result.error.as_string())
            return result


    def findSymbol(self, symbol, context):
        symtab = context.symbolTable
        while symtab:
            if symtab.get(symbol):
                return symtab.get(symbol)
            if context.parent:
                symtab = context.parent.symbolTable
            else:
                break
        return None
                


    def visit_UpdateExpressionNode(self, node, context):
        res = visitor.RTResult()
        value = res.register(self.visit(node.argument, context))
        if res.error: return res

        name = node.argument.identifier.value

        if type(value) != str and type(value) != list:
            if node.operator.type == Token.cons.INC:
                result, error = value.add(Type.Number(1))
            elif node.operator.type == Token.cons.DEC:
                result, error = value.sub(Type.Number(1))
            
            if error: return res.failure(error)
            result.setPosition(node.pos_start, node.pos_end)
        else:
            res.failure(Error.RTError(node.pos_start, node.pos_end, f'Variable \'{name}\' does not support update expression', context))
        
        res.register(self.symtab.update(name, result, context))
        if res.error: return res


    def visit_IdentifierNode(self, node, context):
        identifier = node.identifier.value
        res = visitor.RTResult()
        if self.findSymbol(identifier, context):
            # It's a user-defined Function or Variable
            #ident = self.symtab.get(identifier)
            ident = self.findSymbol(identifier, context)
            # Checking wether the identifier is a variable or a function
            if ident.kind == Token.cons.FUNCTION:
                return res.success(ident.type)
            elif isinstance(ident.type, Type.Value) or isinstance(ident.type, Type.Number) or isinstance(ident.type, Type.String) or isinstance(ident.type, Type.List):
                return res.register(ident.type)
            else:
                # it was self.visit(ident.type.value, context)
                result = res.register(self.visit(ident.type, context))
                return res.success(result)
        elif identifier in Token.cons.FUNCTION:
            # It's a built-in Function
            return res.success(identifier)
        else:
            res.failure(Error.RTError(node.pos_start, node.pos_end, f'Unkown Variable or Function \'{node.identifier.value}\'', context))
            return res

    
    def visit_ForStatementNode(self, node, context):
        res = visitor.RTResult()
        # Node.init, node.test = NULL, node.update, node.body
        init = node.init.variableDeclarators[0].identifier.identifier.value
        forRange = res.register(self.visit(node.test, context))
        if res.error: return res
        for i in forRange.value:
            if isinstance(i, Type.String):
                iterator = Type.String(i.value).setContext(context).setPosition(node.pos_start, node.pos_end)
            elif isinstance(i, Type.List):
                iterator = Type.List(i.value).setContext(context).setPosition(node.pos_start, node.pos_end)
            elif type(i) == str:
                i = Type.String(i).setContext(context).setPosition(node.pos_start, node.pos_end)
                iterator = i
            else:
                iterator = Type.Number(i.value).setContext(context).setPosition(node.pos_start, node.pos_end)
            res.register(self.symtab.update(init, iterator, context))
            if res.error: return res
            res.register(self.visit(node.body, context))
            if res.error: return res
            del iterator


    def visit_InlineFunctionNode(self, node, context):
        res = visitor.RTResult()
        function = Type.Function(node.name, node.params, node.body, node.symtab)
        return res.success(function)

    def visit_CallExpressionNode(self, node, context):
        res = visitor.RTResult()
        function = res.register(self.visit(node.callee, context))
        if res.error: return res

        args = []
        for arg in node.arguments:
            if isinstance(arg, Type.Number):
                args.append(arg)
            else:
                arg = res.register(self.visit(arg, context))
                if res.error: return res
                args.append(arg)
        
        
        function.setPosition(node.pos_start, node.pos_end)
        result = res.register(function.execute(args, context))
        if res.error: return res
        return res.success(result)

    def visit_AssignmentExpressionNode(self, node, context):
        res = visitor.RTResult()
        name = node.left.identifier.value
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))
        if res.error: return res

        error = None
        if node.op.type == Token.cons.ASSIGN:
            value = right
        elif node.op.type == Token.cons.PAS:
            value, error = left.add(right)
        elif node.op.type == Token.cons.NAS:
            value, error = left.sub(right)
        elif node.op.type == Token.cons.DAS:
            value, error = left.div(right)
        elif node.op.type == Token.cons.MUAS:
            value, error = left.mul(right)
        elif node.op.type == Token.cons.MOAS:
            value, error = left.mod(right)
        
        if error: return res
        value.setPosition(node.pos_start, node.pos_end)
        res.register(self.symtab.update(name, value, context))
        if res.error: return res