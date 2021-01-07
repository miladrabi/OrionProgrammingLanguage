import token as Token
import ast
import typeSystem as Type
import symTable as SymbolTable
import errors as Error
from globalSymbolTable import GLOBAL_SYMBOL_TABLE

# TODO: Variable Declaration should be in AST or not?

class ParseResult:
    def __init__(self):
        self.error = None
        self.node  = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

class Parser:
    def __init__(self, lexer):
        
        tokens, error = lexer.tokenize()
        if error: print(error.as_string())
        self.tokens = tokens
        # TODO: There must be a way to not store all of the contexts. Think about it and then apply it.
        self.currentToken = None
        self.pos = 0
        self.advance()


    ## HELPER FUNCTIONS
    def advance(self):
        if self.pos > len(self.tokens) - 1:
            self.currentToken = None
        else:
            self.currentToken = self.tokens[self.pos]
            self.pos += 1

    def peek(self):
        if self.pos > len(self.tokens) - 1:
            return Token.Token(Token.cons.EOF, None)
        else:
            return self.tokens[self.pos]

    def error(self, Type):
        raise Exception(f'Parsing Error: expected:\'{Type}\', got:\'{self.currentToken.type}\' ')

    def consume(self, Type):
        if self.currentToken.type == Type:
            self.advance()
            return True
        else:
            self.error(Type)

    def parse(self):
        res = self.program()
        if not res.error and self.currentToken.type != Token.cons.EOF:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '+', '-', '*' or '/'"))
        return res

    ## PARSING FUNCTIONS
    def program(self):
        res = ParseResult()
        statements = []
        while self.currentToken.type != Token.cons.EOF:
            if self.currentToken.type in (Token.cons.LET, Token.cons.CONST):
                
                stmt = self.varDecl_stmt(GLOBAL_SYMBOL_TABLE)[0]
                stmt = res.register(stmt)
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.IDENT:
                stmt = res.register(self.expr_stmt())
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.FUNCTION:
                stmt = res.register(self.function_stmt(GLOBAL_SYMBOL_TABLE))
                if res.error: return res
            elif self.currentToken.type == Token.cons.IF:
                stmt = res.register(self.if_stmt())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.FOR:
                stmt = res.register(self.for_stmt(GLOBAL_SYMBOL_TABLE))
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.WHILE:
                stmt = res.register(self.while_stmt())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.PUTS:
                stmt = res.register(self.put_statement())
                if res.error: return res
                statements.append(stmt)
            else:
                statements.append(res.register(self.expr()))
                if res.error: return res
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected binary operation such as '+', '-', etc."))
        
        
        return res.success(ast.ProgramNode(statements))

    def put_statement(self):
        res = ParseResult()
        arguments = []
        res.register(self.advance())
        if self.currentToken.type == Token.cons.SEMICOLON:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected arguments after 'puts' statement"))
        
        arg = res.register(self.expr())
        if res.error: return res
        arguments.append(arg)
        while self.currentToken.type == Token.cons.COMMA:
            res.register(self.advance())
            arg = res.register(self.expr())
            if res.error: return res
            arguments.append(arg)
        
        if self.currentToken.type != Token.cons.SEMICOLON:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, f"Unexpected character '{self.currentToken.value}'"))
        
        node = ast.PutStatementNode(arguments)
        res.register(self.advance())
        return res.success(node)

    def function_block(self):
        res = ParseResult()
        statements = []
        varnames = []
        symtab = SymbolTable.SymbolTable()
        while self.currentToken.type != Token.cons.RBRACE:
            if self.currentToken.type == Token.cons.LET:
                varDeclTuple = self.varDecl_stmt(symtab)
                declaration = res.register(varDeclTuple[0])
                if res.error: return res
                statements.append(declaration)
                symtab = varDeclTuple[1]
                varnames = varDeclTuple[2]
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.RETURN:
                stmt = res.register(self.return_stmt())
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.FUNCTION:
                stmt = res.register(self.function_stmt(GLOBAL_SYMBOL_TABLE))
                if res.error: return res
            elif self.currentToken.type == Token.cons.PUTS:
                stmt = res.register(self.put_statement())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.IDENT:
                stmt = res.register(self.expr_stmt())
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.IF:
                stmt = res.register(self.if_stmt())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.FOR:
                stmt = res.register(self.for_stmt(symtab))
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.WHILE:
                stmt = res.register(self.while_stmt())
                if res.error: return res
                statements.append(stmt)
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected expression or statement"))
        block = ast.BlockStatementNode(statements)
        return res.success(block), symtab, varnames


    def block(self):
        res = ParseResult()
        statements = []
        while self.currentToken.type != Token.cons.RBRACE:
            if self.currentToken.type == Token.cons.LET:
                stmt = res.register(self.varDecl_stmt(GLOBAL_SYMBOL_TABLE)[0])
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.IDENT:
                stmt = res.register(self.expr_stmt())
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.RETURN:
                stmt = res.register(self.return_stmt())
                if res.error: return res
                statements.append(stmt)
                if self.currentToken.type == Token.cons.SEMICOLON:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))
            elif self.currentToken.type == Token.cons.IF:
                stmt = res.register(self.if_stmt())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.FOR:
                stmt = res.register(self.for_stmt(GLOBAL_SYMBOL_TABLE))
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.WHILE:
                stmt = res.register(self.while_stmt())
                if res.error: return res
                statements.append(stmt)
            elif self.currentToken.type == Token.cons.PUTS:
                stmt = res.register(self.put_statement())
                if res.error: return res
                statements.append(stmt)
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected expression or statement"))

        return res.success(ast.BlockStatementNode(statements))

    def varDecl_stmt(self, symbolTable):
        res = ParseResult()
        kind = self.currentToken
        declaration = []
        varnames = []
        res.register(self.advance())
        if res.error: return res

        if self.currentToken.type != Token.cons.IDENT:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected identifier"))
        ident = res.register(self.factor())
        if res.error: return res
        idents = []
        idents.append(ident)
        varnames.append(ident.identifier)
        while self.currentToken.type == Token.cons.COMMA:
            res.register(self.advance())
            if res.error: return res

            if self.currentToken.type != Token.cons.IDENT:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected identifier"))
            ident = res.register(self.factor())
            if res.error: return res
            varnames.append(ident.identifier)
            idents.append(ident)
        if self.currentToken.type in (Token.cons.SEMICOLON, Token.cons.COLON):
            for ident in idents:
                declaration.append(ast.VariableDeclaratorNode(ident, ast.NumberNode(Token.Token(Token.cons.INT, 0))))
            node = ast.VariableDeclarationNode(kind, declaration)
        else:
            if self.currentToken.type == Token.cons.ASSIGN:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '='"))
    
            values = []
            value = res.register(self.expr())
            if res.error: return res
            values.append(value)
            while self.currentToken.type == Token.cons.COMMA:
                res.register(self.advance())
                if res.error: return res
                val = res.register(self.expr())
                if res.error: return res
                values.append(val)

            if self.currentToken.type != Token.cons.SEMICOLON:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ';'"))

        
            if len(values) > len(idents):
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Too many values to unpack"))
            unpackable = len(values) - 1
            for i in range(len(idents)):
                if i >= unpackable:
                    declaration.append(ast.VariableDeclaratorNode(idents[i], values[unpackable]))
                else:
                    declaration.append(ast.VariableDeclaratorNode(idents[i], values[i]))
            node = ast.VariableDeclarationNode(kind, declaration)
            symbols = {}
        for declaration in node.variableDeclarators:
            ident = declaration.identifier.identifier.value
            if isinstance(declaration.init, ast.InlineFunctionNode):
                declaration.init.setPosition(declaration.identifier)
                prop  = SymbolTable.Symbol(Token.cons.FUNCTION, declaration.init)
            else:
                prop  = SymbolTable.Symbol(kind.type, declaration.init)
            symbolTable.define(ident, prop)

        return res.success(node), symbolTable, varnames


    def inline_expr(self, symtab):
        res = ParseResult()
        
        if self.currentToken.type == Token.cons.LPAREN:
            res.register(self.advance())
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '('"))

        params = []
        while True:
            param = res.register(self.factor())
            if res.error: return res
            if isinstance(param, ast.IdentifierNode):
                param = param.identifier.value
            params.append(param)
            if self.currentToken.type == Token.cons.RPAREN:
                break
            
            if self.currentToken.type == Token.cons.COMMA:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ',' or ')'"))
        
        if self.currentToken.type == Token.cons.RPAREN:
            res.register(self.advance())
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))

        if self.currentToken.type == Token.cons.ARROW:
            res.register(self.advance())
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '->'"))
        
        body = res.register(self.expr())
        if res.error: return res
        funcSymtab = SymbolTable.SymbolTable()
        funcSymtab.parent = symtab

        node = ast.InlineFunctionNode(params, body, funcSymtab)
        return res.success(node)

    def return_stmt(self):
        res = ParseResult()
        if self.currentToken.type == Token.cons.RETURN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'return'"))

        node = res.register(self.expr())
        if res.error: return res
        node = ast.ReturnNode(node)
        return res.success(node)

    def if_stmt(self):
        res = ParseResult()
        if self.currentToken.type in (Token.cons.IF,Token.cons.ELIF, Token.cons.ELSE):
            tt = self.currentToken.type
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'if', 'elif', or 'else'"))
        if tt != Token.cons.ELSE:
            if self.currentToken.type == Token.cons.LPAREN:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '('"))
            
            test = res.register(self.expr())
            if res.error: return res

            if self.currentToken.type == Token.cons.RPAREN:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
            
            if self.currentToken.type == Token.cons.LBRACE:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '{'"))
            
            
            body = res.register(self.block())
            if res.error: return res
            
            if self.currentToken.type == Token.cons.RBRACE:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '}'"))
            
            if self.currentToken.type in (Token.cons.ELIF, Token.cons.ELSE):
                alternative = res.register(self.if_stmt())
                if res.error: return res
            else:
                alternative = None
            node = ast.IfStatementNode(test, body, alternative)
        else:
            if self.currentToken.type == Token.cons.LBRACE:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '{'"))
    
            body = res.register(self.block())
            if res.error: return res
            
            if self.currentToken.type == Token.cons.RBRACE:
                res.register(self.advance())
                if res.error: return res
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '}'"))
            
            node = body
        return res.success(node)

    def for_stmt(self, symtab):
        res = ParseResult()
        if self.currentToken.type == Token.cons.FOR:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'for'"))
        
        if self.currentToken.type == Token.cons.LPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '('"))

        
        if self.currentToken.type != Token.cons.LET:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'let' or variable declaration"))


        init = self.varDecl_stmt(symtab)
        if type(init) == tuple: init = init[0]
        init = res.register(init)
        if res.error: return res
        ident = init.variableDeclarators[0].identifier

        if self.currentToken.type == Token.cons.COLON:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ':'"))
        

        test = res.register(self.factor())
        if res.error: return res

        if self.currentToken.type == Token.cons.RPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
        

        if self.currentToken.type == Token.cons.LBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '{'"))
        

        body = res.register(self.block())
        if res.error: return res
        

        if self.currentToken.type == Token.cons.RBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '}'"))
        

        update = ast.UpdateExpressionNode(Token.Token(Token.cons.INC, '++'), ident)
        node = ast.ForStatementNode(init = init, test = test, update = update, body = body)
        return res.register(node)


    def while_stmt(self):
        res = ParseResult()
        if self.currentToken.type == Token.cons.WHILE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'while'"))
        

        if self.currentToken.type == Token.cons.LPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '('"))
        
        test = res.register(self.expr())
        if res.error: return res

        if self.currentToken.type == Token.cons.RPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
        
        
        if self.currentToken.type == Token.cons.LBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '{'"))

        body = res.register(self.block())
        if res.error: return res
        
        if self.currentToken.type == Token.cons.RBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '}'"))

        node = ast.WhileStatementNode(test, body)
        return res.success(node)

    def function_stmt(self, symtab):
        
        res = ParseResult()

        if self.currentToken.type == Token.cons.FUNCTION:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected 'function'"))
        
        functionName = self.currentToken.value

        if self.currentToken.type == Token.cons.IDENT:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected function name"))
        

        if self.currentToken.type == Token.cons.LPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '('"))
        
        params = []
        if self.currentToken.type != Token.cons.RPAREN:
            while True:
                param = res.register(self.factor())
                if res.error: return res
                if isinstance(param, ast.IdentifierNode):
                    param = param.identifier.value
                params.append(param)
                if self.currentToken.type == Token.cons.RPAREN:
                    break
                
                if self.currentToken.type == Token.cons.COMMA:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ','"))
        
        if self.currentToken.type == Token.cons.RPAREN:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))

        if self.currentToken.type == Token.cons.LBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '{'"))

        block = self.function_block()
        funcSymTab = block[1]
        funcSymTab.parent = symtab
        block = res.register(block[0])
        if res.error: return res

        if self.currentToken.type == Token.cons.RBRACE:
            res.register(self.advance())
            if res.error: return res
        else:
            return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '}'"))
    
        symtab.define(functionName, SymbolTable.Symbol(Token.cons.FUNCTION, Type.Function(functionName, params, block, funcSymTab)))

    def member_expr(self, ident):
        res = ParseResult()
        prop = res.register(self.arith_expr())
        if res.error: return res
        return res.success(ast.MemberExpressionNode(ident, prop))


    def list_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.currentToken.pos_start
        res.register(self.advance())
        if res.error: return res
        if self.currentToken.type == Token.cons.RBRACK:
            pos_end = self.currentToken.pos_start
        else:
            while True:
                el = res.register(self.expr())
                if res.error: return res
                elements.append(el)
                if self.currentToken.type == Token.cons.RBRACK:
                    pos_end = self.currentToken.pos_start
                    break
                if self.currentToken.type == Token.cons.COMMA:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ',' OR ']'"))
             
        return res.success(ast.ListExpressionNode(elements, pos_start, pos_end))

    def expr_stmt(self):
        res = ParseResult()
        ident = res.register(self.factor())
        if res.error: return res
        if self.currentToken.type in (Token.cons.INC, Token.cons.DEC):
            op = self.currentToken
            res.register(self.advance())
            if res.error: return res
            return res.success(ast.UpdateExpressionNode(operator = op, argument = ident))
        elif self.currentToken.type != Token.cons.SEMICOLON:
            op = self.currentToken
            res.register(self.advance())
            if res.error: return res
            right = res.register(self.expr())
            if res.error: return res
            return res.success(ast.AssignmentExpressionNode(left = ident, op = op, right = right))
        else:
            return res.register(ident)

    def call_expr(self, ident):
        res = ParseResult()
        args = []
        if self.currentToken.type != Token.cons.RPAREN:
            while True:
                arg = res.register(self.expr())
                if res.error: return res
                args.append(arg)
                if self.currentToken.type == Token.cons.RPAREN:
                    break
                if self.currentToken.type == Token.cons.COMMA:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ',' OR ')'"))

        return res.register(ast.CallExpressionNode(callee = ident, arguments = args))

    def binary_expr(self, function, operators):
        res = ParseResult()
        node = res.register(function())
        if res.error: return res

        while self.currentToken.type in operators:
            op = self.currentToken
            res.register(self.advance())
            right = res.register(function())
            if res.error: return res
            node = ast.BinOpNode(node, op, right)
        return res.success(node)

    def expr(self):
        return self.binary_expr(self.and_expr, (Token.cons.OR))

    def and_expr(self):
        return self.binary_expr(self.comp_expr, (Token.cons.AND))

    def comp_expr(self):
        return self.binary_expr(self.arith_expr, (Token.cons.IN,Token.cons.EQ,Token.cons.NEQ,Token.cons.LT,Token.cons.GT,Token.cons.LTE,Token.cons.GTE))

    def arith_expr(self):
        return self.binary_expr(self.term, (Token.cons.CONCAT, Token.cons.PLUS, Token.cons.MINUS))

    def term(self):
        return self.binary_expr(self.factor, (Token.cons.MUL, Token.cons.DIV, Token.cons.MOD))

    def factor(self):
        res = ParseResult()
        tok = self.currentToken
        if tok.type in (Token.cons.HASH, Token.cons.PLUS, Token.cons.MINUS, Token.cons.NOT):
            res.register(self.advance())
            node = res.register(self.factor())
            if res.error: return res
            return res.success(ast.UnaryOpNode(tok, node))
        elif tok.type in Token.cons.NUMBERS:
            res.register(self.advance())
            return res.success(ast.NumberNode(tok))
        elif tok.type == Token.cons.INLINE:
            res.register(self.advance())
            node = res.register(self.inline_expr(GLOBAL_SYMBOL_TABLE))
            if res.error: return res
            return res.success(node)
        elif tok.type == Token.cons.IDENT:
            res.register(self.advance())
            if res.error: return res
            if self.currentToken.type == Token.cons.LPAREN:
                res.register(self.advance())
                if res.error: return res
                node = res.register(self.call_expr(ast.IdentifierNode(tok)))
                if res.error: return res
                if self.currentToken.type == Token.cons.RPAREN:
                    res.register(self.advance())
                    if res.error: return res
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
                return res.success(node)
            elif self.currentToken.type == Token.cons.LBRACK:
                res.register(self.advance())
                node = res.register(self.member_expr(ast.IdentifierNode(tok)))
                if res.error: return res
                if self.currentToken.type == Token.cons.RBRACK:
                    res.register(self.advance())
                else:
                    return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ']'"))
                if res.error: return res
                return res.success(node)
            else:
                return res.success(ast.IdentifierNode(tok))
        elif tok.type == Token.cons.STRLIT:
            res.register(self.advance())
            if res.error: return res
            return res.success(ast.LiteralNode(tok))
        elif tok.type == Token.cons.LPAREN:
            res.register(self.advance())
            if res.error: return res
            node = res.register(self.expr())
            if res.error: return res
            if self.currentToken.type == Token.cons.RPAREN:
                res.register(self.advance())
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
            if res.error: return res
            return res.success(node)
        elif tok.type == Token.cons.LBRACK:
            node = res.register(self.list_expr())
            if self.currentToken.type == Token.cons.RBRACK:
                res.register(self.advance())
            else:
                return res.failure(Error.InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ']'"))
            if res.error: return res
            return res.success(node)
        return res.failure(Error.InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected Number, List, Variable, Function Call, or String Literal."))
        


        
            
            