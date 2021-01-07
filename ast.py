class Node:
    pass

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

class IfStatementNode(Node):
    def __init__(self, test, body, alternative):
        self.test = test
        self.body = body
        self.alternative = alternative
        self.pos_start = test.pos_start
        self.pos_end = alternative.pos_end if alternative else body.pos_end

class ForStatementNode(Node):
    def __init__(self, init, test, update, body):
        self.init = init
        self.test = test
        self.update = update
        self.body = body
        self.pos_start = self.init.pos_start
        self.pos_end = self.body.pos_end

class PutStatementNode(Node):
    def __init__(self, arguments):
        self.arguments = arguments
        self.pos_start = arguments[0].pos_start
        self.pos_end = arguments[-1].pos_start

class WhileStatementNode(Node):
    def __init__(self, test, body):
        self.test = test
        self.body = body
        self.pos_start = test.pos_start
        self.pos_end = body.pos_end

class BlockStatementNode(Node):
    def __init__(self, body):
        self.body = body
        if len(body) > 0:
            self.pos_start = body[0].pos_start
            self.pos_end = body[-1].pos_end

class ExpressionStatementNode(Node):
    def __init__(self, expression):
        self.expression = expression
        self.pos_start = expression.pos_start
        self.pos_end = expression.pos_end

class ListExpressionNode(Node):
    def __init__(self, elements, pos_start = None, pos_end = None):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

class UpdateExpressionNode(Node):
    def __init__(self, operator, argument):
        self.operator = self.token = operator
        self.argument = argument
        self.pos_start = argument.pos_start
        self.pos_end = operator.pos_end

class AssignmentExpressionNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = self.token = op
        self.right = right
        self.pos_start = left.pos_start
        self.pos_end = right.pos_end

class CallExpressionNode(Node):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
        self.pos_start = callee.pos_start
        if len(arguments) > 0:
            self.pos_end = arguments[-1].pos_end
        else:
            self.pos_end = self.pos_start

class VariableDeclarationNode(Node):
    def __init__(self, kind, declarations):
        self.kind = kind
        self.variableDeclarators = declarations
        self.pos_start = kind.pos_start
        self.pos_end = declarations[-1].pos_end

class VariableDeclaratorNode(Node):
    def __init__(self, identifier, init):
        self.identifier = identifier
        self.init = init
        self.pos_start = identifier.pos_start
        if init:
            self.pos_end = init.pos_end
        else:
            self.pos_end = identifier.pos_end

class InlineFunctionNode(Node):
    def __init__(self, params, body, symbolTable):
        self.name = None
        self.params = params
        self.body = body
        self.symtab = symbolTable
        self.pos_start = self.name.pos_start if self.name else 0
        self.pos_end = body.pos_end

    def setPosition(self, name):
        self.name = name.identifier.value
        self.pos_start = name.pos_start

class MemberExpressionNode(Node):
    def __init__(self, identifier, Property):
        self.identifier = identifier
        self.property = Property
        self.pos_start = identifier.pos_start
        self.pos_end = Property.pos_end

class IdentifierNode(Node):
    def __init__(self, identifier):
        self.identifier = identifier
        self.pos_start = self.identifier.pos_start
        self.pos_end = self.identifier.pos_end

    def __repr__(self):
        return f'[Identifier: {self.identifier.value}]'

class LiteralNode(Node):
    def __init__(self, stringToken):
        self.token = stringToken
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

class ReturnNode(Node):
    def __init__(self, expr):
        self.expr = expr
        self.pos_start = expr.pos_start
        self.pos_end = expr.pos_end

class NumberNode(Node):
    def __init__(self, token):
        self.token = token
        self.value = token.value
        self.pos_start = self.token.pos_start
        self.pos_end   = self.token.pos_end

    def __repr__(self):
        return f'NumberNode[v:{self.value}]'

class UnaryOpNode(Node):
    def __init__(self, op, expr):
        self.expr = expr
        self.token = self.op = op
        self.pos_start = self.op.pos_start
        self.pos_end = self.expr.pos_end

class BinOpNode(Node):
    def __init__(self, left, op, right, pos_start = None, pos_end = None):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end

    def __repr__(self):
        return f'BinOp[l:{self.left}, o:{self.op}, r:{self.right}]'