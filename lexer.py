import token as Token
import errors as Error
from position import Position
import util

class Lexer:
    def __init__(self, fileName, Input):
        #TODO: Do we really need this property or not?
        self.fileName = fileName
        self.input = Input + '\n'
        self.currentChar = None
        self.pos = Position(0, 1, 0, fileName, self.input)
        ## TODO: decide wether to store tokens or make them on the fly
        self.tokens = []
        self.advance()

    ## HELPER FUNCTIONS
    def advance(self):
        if self.pos.index > len(self.input) - 1:
            self.currentChar = None
        else:
            self.currentChar = self.input[self.pos.index]
            self.pos.advance(self.currentChar)

    def peek(self, offset = 1):
            if self.pos.index + (offset - 1) > len(self.input) - 1:
                return None
            return self.input[self.pos.index + (offset - 1)]

    def error(self):
        raise Exception(f'Illegal Character. got = \'{self.currentChar}\' ')

    def isSpace(self, ch):
        return ch == ' ' or ch == '\t' or ch == '\n' or ch == '\r'

    ## Checks for double operators
    ## TODO: Rethink on it. There should be a better solution
    def isOperator(self, ch):
        if self.peek() == '=':
            if ch == '=':
                return Token.Token(Token.cons.EQ, "==", pos_start = self.pos)
            if ch == '>':
                return Token.Token(Token.cons.GTE, ">=", pos_start = self.pos)
            if ch == '<':
                return Token.Token(Token.cons.LTE, "<=", pos_start = self.pos)
            if ch == '+':
                return Token.Token(Token.cons.PAS, "+=", pos_start = self.pos)
            if ch == '-':
                return Token.Token(Token.cons.NAS, "-=", pos_start = self.pos)
            if ch == '*':
                return Token.Token(Token.cons.MUAS, "*=", pos_start = self.pos)
            if ch == '/':
                return Token.Token(Token.cons.DAS, "/=", pos_start = self.pos)
            if ch == '%':
                return Token.Token(Token.cons.MOAS, "%=", pos_start = self.pos)
            if ch == '!':
                return Token.Token(Token.cons.NEQ, "!=", pos_start = self.pos)
        elif self.peek() == '+' and ch == '+':
            return Token.Token(Token.cons.INC, "++", pos_start = self.pos)
        elif self.peek() == '-' and ch == '-':
            return Token.Token(Token.cons.DEC, "--", pos_start = self.pos)
        elif self.peek() == '>' and ch == '-':
            return Token.Token(Token.cons.ARROW, "->", pos_start = self.pos)
        elif self.peek() == '&' and ch == '&':
            return Token.Token(Token.cons.AND, "&&", pos_start = self.pos)
        elif self.peek() == '|' and ch == '|':
            return Token.Token(Token.cons.OR, "||", pos_start = self.pos)
        elif self.peek() == '.' and ch == '.':
            return Token.Token(Token.cons.CONCAT, "..", pos_start = self.pos)
        else:
            return None

    def makeNumber(self):
        value = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar in (Token.cons.DIGITS + Token.cons.DIGIT_COMPLEMENT):
            if self.peek() == '.' and self.peek(2) == '.':
                break
            if self.currentChar == '-':
                if 'e' in value:
                    value += self.currentChar
                else:
                    break
            else:       
                value += self.currentChar
            self.advance()

        if 'e' in value:
            tok = Token.Token(Token.cons.SCINUM, util.evaluate_scinum(value), pos_start, self.pos)
        elif 'x' in value:
            tok = Token.Token(Token.cons.HEXNUM, int(value, 0), pos_start, self.pos)
        elif 'c' in value:
            tok = Token.Token(Token.cons.OCTNUM, int(value[2:], 8), pos_start, self.pos)
        elif 'b' in value:
            tok = Token.Token(Token.cons.BINNUM, int(value[2:], 2), pos_start, self.pos)
        elif '.' in value:
            tok = Token.Token(Token.cons.FLOAT, float(value), pos_start, self.pos)
        else:
            tok = Token.Token(Token.cons.INT, int(value), pos_start, self.pos)

        return tok

    def makeIdentifier(self):
        value = ""
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar.isalnum() or self.currentChar == '_':
            value += self.currentChar
            self.advance()

        if value in Token.cons.KEYWORDS:
            tok = Token.Token(Token.cons.KEYWORDS[value], value, pos_start, self.pos.copy())
        else:
            tok = Token.Token(Token.cons.IDENT, value, pos_start, self.pos.copy())
        return tok


    def makeString(self):
        value = ""
        pos_start = self.pos.copy()
        end = self.currentChar
        self.advance()
        while self.currentChar is not None and self.currentChar != end:
            if self.currentChar in Token.cons.ESCAPES:
                if self.currentChar == '\b':
                    value += '\\b'
                elif self.currentChar == '\f':
                    value += '\\f'
                elif self.currentChar == '\n':
                    value += '\\n'
                elif self.currentChar == '\r':
                    value += '\\r'
                elif self.currentChar == '\t':
                    value += '\\t'
                elif self.currentChar == '\\':
                    value += '\\\\'
            else:
                value += self.currentChar
            self.advance()

        self.advance()
        return Token.Token(Token.cons.STRLIT, value, pos_start, self.pos)

    def consumeComment(self):
        self.advance()
        tmp = self.currentChar
        if tmp == '/':
            while self.currentChar != '\n':
                self.advance()
        elif tmp == '*':
            while True:
                if self.currentChar == '*' and self.peek() == '/':
                    self.advance()
                    break
                else:
                    self.advance()
                    
    ## MAIN FUNCTION
    def tokenize(self):
        while self.currentChar != None:
            if self.isSpace(self.currentChar):
                self.advance()
                continue
            if self.currentChar in Token.cons.DIGITS:
                self.tokens.append(self.makeNumber())
                continue
            if self.currentChar.isalpha() or self.currentChar == '_':
                self.tokens.append(self.makeIdentifier())
                continue
            if self.currentChar in '\' "':
                self.tokens.append(self.makeString())
                continue
            if self.currentChar == '=':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.ASSIGN, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '+':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.PLUS, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '-':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.MINUS, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '*':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.MUL, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '/':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    if self.peek() == '/' or self.peek() == '*':
                        self.consumeComment()
                    else:
                        self.tokens.append(Token.Token(Token.cons.DIV, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '%':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.MOD, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '!':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.NOT, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '<':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.LT, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '>':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.GT, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '&':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.BAND, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '|':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
                else:
                    self.tokens.append(Token.Token(Token.cons.BOR, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '.':
                if self.isOperator(self.currentChar):
                    self.tokens.append(self.isOperator(self.currentChar))
                    self.advance()
            elif self.currentChar == '(':
                self.tokens.append(Token.Token(Token.cons.LPAREN, self.currentChar, pos_start = self.pos))
            elif self.currentChar == ')':
                self.tokens.append(Token.Token(Token.cons.RPAREN, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '{':
                self.tokens.append(Token.Token(Token.cons.LBRACE, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '}':
                self.tokens.append(Token.Token(Token.cons.RBRACE, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '[':
                self.tokens.append(Token.Token(Token.cons.LBRACK, self.currentChar, pos_start = self.pos))
            elif self.currentChar == ']':
                self.tokens.append(Token.Token(Token.cons.RBRACK, self.currentChar, pos_start = self.pos))
            elif self.currentChar == ',':
                self.tokens.append(Token.Token(Token.cons.COMMA, self.currentChar, pos_start = self.pos))
            elif self.currentChar == ';':
                self.tokens.append(Token.Token(Token.cons.SEMICOLON, self.currentChar, pos_start = self.pos))
            elif self.currentChar == ':':
                self.tokens.append(Token.Token(Token.cons.COLON, self.currentChar, pos_start = self.pos))
            elif self.currentChar == '#':
                self.tokens.append(Token.Token(Token.cons.HASH, self.currentChar, pos_start = self.pos))
            else:
                pos_start = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], Error.IllegalCharError(pos_start, self.pos, "'" + char + "'")
            self.advance()
        self.tokens.append(Token.Token(Token.cons.EOF, None, pos_start = self.pos))
        return self.tokens, None