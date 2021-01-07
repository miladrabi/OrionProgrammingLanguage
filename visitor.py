import token as Token
import typeSystem as Type
import ast
import symTable as SymbolTable
import errors as Error
from globalSymbolTable import GLOBAL_SYMBOL_TABLE

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
        self.returnFlag = False


    def register(self, res):
        if isinstance(res, RTResult):
            if res.error: self.error = res.error
            return res.value

        return res

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

class NodeVisitor:
    def visit(self, node, context):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, context)

    def generic_visit(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method found')



class Visitor(NodeVisitor):

    def visit_ProgramNode(self, node, context):
        res = RTResult()
        if len(node.statements) > 0:
            for statement in node.statements:
                result = res.register(self.visit(statement, context))
                if res.error: return res
        else:
            return

    def visit_IfStatementNode(self, node, context):
        res = RTResult()
        test = res.register(self.visit(node.test, context))
        if res.error: return res
        if test.value:
            result = res.register(self.visit(node.body, context))
            if res.error: return res
            return res.success(result)
        elif node.alternative is not None:
            result = res.register(self.visit(node.alternative, context))
            if res.error: return res
            return res.success(result)

    def visit_WhileStatementNode(self, node, context):
        res = RTResult()
        if type(node.test) == type(None):
            return res.failure(Error.RTError(node.post_start, node.pos_end, 'Infinite loop', context))
        test = res.register(self.visit(node.test, context))
        if res.error: return res
        test = test.value
        while test:
            res.register(self.visit(node.body, context))
            if res.error: return res
            test = res.register(self.visit(node.test, context))
            if res.error: return res
            test = test.value

        

    def visit_BlockStatementNode(self, node, context):
        res = RTResult()
        for statement in node.body:
            if isinstance(statement, ast.ReturnNode):
                value = res.register(self.visit(statement, context))
                if res.error: return res
                return res.success(value)
            
            value = res.register(self.visit(statement, context))
            if res.error: return res
        return res.success(value)

    def visit_ListExpressionNode(self, node, context):
        res = RTResult()
        elements = []
        for element in node.elements:
            result = res.register(self.visit(element, context))
            if res.error: return res
            elements.append(result)
        
        return res.success(Type.List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))
                        
    def visit_VariableDeclarationNode(self, node, context):
        res = RTResult()
        kind = node.kind
        for declaration in node.variableDeclarators:
            ident = declaration.identifier.identifier.value
            init = res.register(self.visit(declaration.init, context))
            if res.error: return res
            if isinstance(init, SymbolTable.FunctionContext):
                prop = SymbolTable.Symbol(kind, Type.Function(init))
            else:
                prop = SymbolTable.Symbol(kind, init)
                
            self.symtab.define(ident, prop)

    def visit_VariableDeclaratorNode(self, node, context):
        pass

    def visit_MemberExpressionNode(self, node, context):
        res = RTResult()
        ident = res.register(self.visit(node.identifier, context))
        if res.error: return res
        prop = res.register(self.visit(node.property, context))
        if res.error: return res
        if isinstance(ident, Type.List) or isinstance(ident, Type.String):
            if prop.value > ident.length - 1:
                return res.failure(Error.RTError(node.pos_start, node.pos_end, "Index out of range", context))
            value = ident.value[prop.value]
            if type(value) == str:
                value = Type.String(value).setContext(context).setPosition(node.pos_start, node.pos_end)
            elif type(value) == list:
                value = Type.List(value).setContext(context).setPosition(node.pos_start, node.pos_end)
            elif type(value) == int or type(value) == float:
                value = Type.Number(value).setContext(context).setPosition(node.pos_start, node.pos_end)
            return res.success(value)
        else:
            res.failure(Error.RTError(node.pos_start, node.pos_end, f'Variable \'{ident}\' does not support member expression.', context))

    def visit_PutStatementNode(self, node, context):
        res = RTResult()
        result = ""
        for arg in node.arguments:
            stmt = res.register(self.visit(arg, context))
            if res.error: return res
            result += str(stmt)

        print(result)
    
    def visit_CallExpressionNode(self, node, context):
        pass

    def visit_LiteralNode(self, node, context):
        return RTResult().success(Type.String(node.token.value).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_ReturnNode(self, node, context):
        value = self.visit(node.expr, context)
        return value

    def visit_NumberNode(self, node, context):
        return RTResult().success(Type.Number(node.value).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.expr, context))
        if res.error: return res

        error = None
        if node.op.type == Token.cons.MINUS:
            value, error = number.mul(Type.Number(-1))
        elif node.op.type == Token.cons.NOT:
            value, error = number.unary_not()
        elif node.op.type == Token.cons.HASH:
            value, error = number._len()

        if error: return res.failure(error)
        return res.success(value.setPosition(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))
        if res.error: return res

        if node.op.type == Token.cons.PLUS:
            result, error = left.add(right)
        elif node.op.type == Token.cons.MINUS:
            result, error = left.sub(right)
        elif node.op.type == Token.cons.MUL:
            result, error = left.mul(right)
        elif node.op.type == Token.cons.DIV:
            result, error = left.div(right)
        elif node.op.type == Token.cons.MOD:
            result, error = left.mod(right)
        elif node.op.type == Token.cons.EQ:
            result, error = left.compare_eq(right)
        elif node.op.type == Token.cons.LT:
            result, error = left.compare_lt(right)
        elif node.op.type == Token.cons.GT:
            result, error = left.compare_gt(right)
        elif node.op.type == Token.cons.LTE:
            result, error = left.compare_lte(right)
        elif node.op.type == Token.cons.GTE:
            result, error = left.compare_gte(right)
        elif node.op.type == Token.cons.NEQ:
            result, error = left.compare_neq(right)
        elif node.op.type == Token.cons.AND:
            result, error = left.compare_and(right)
        elif node.op.type == Token.cons.OR:
            result, error = left.compare_or(right)
        elif node.op.type == Token.cons.CONCAT:
            result, error = left.concat(right)

        if error: return res.failure(error)
        return res.success(result.setPosition(node.pos_start, node.pos_end))
        