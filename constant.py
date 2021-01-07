from signature import SIGNATURE
######################
# CONSTANTS
######################
DIGITS = "0123456789"
DIGIT_COMPLEMENT = ".xcbe-+"


## KEYWORDS
LET      = "LET"
CONST    = "CONST"
IF       = "IF"
ELSE     = "ELSE"
ELIF     = "ELIF"
WHILE    = "WHILE"
FOR      = "FOR"
RETURN   = "RETURN"
PACKAGE  = "PACKAGE"
FUNCTION = "FUNCTION"
IN       = "IN"
INLINE   = "INLINE"
GIVEN    = "GIVEN"
WHEN     = "WHEN"
DEFAULT  = "DEFAULT"
PUTS     = "PUTS"

KEYWORDS = {
    "let": LET,
    "const": CONST,
    "if": IF,
    "elif": ELIF,
    "else": ELSE,
    "for": FOR,
    "while": WHILE,
    "ret": RETURN,
    "package": PACKAGE,
    "func": FUNCTION,
    "in": IN,
    "inline" : INLINE,
    "given" : GIVEN,
    "when" : WHEN,
    "default" : DEFAULT,
    "puts": PUTS
}


## OPERATORS

PLUS  = "PLUS"
MINUS = "MINUS"
DIV   = "DIV"
MUL   = "MUL"
MOD   = "MOD"
INC   = "INC"
DEC   = "DEC"
PAS   = "PAS"
NAS   = "NAS"
DAS   = "DAS"
MUAS  = "MUAS"
MOAS  = "MOAS"

## COMPARISONS

EQ   = "EQ"
LT   = "LT"
GT   = "GT"
NOT  = "NOT"
LTE  = "LTE"
GTE  = "GTE"
NEQ  = "NEQ"
AND  = "AND"
OR   = "OR"


## PUNCTUATIONS
ASSIGN    = "ASSIGN"
LPAREN    = "LPAREN"
RPAREN    = "RPAREN"
LBRACE    = "LBRACE"
RBRACE    = "RBRACE"
LBRACK    = "LBRACK"
RBRACK    = "RBRACK"
SEMICOLON = "SEMICOLON"
COMMA     = "COMMA"
COLON     = "COLON"
ARROW     = "ARROW"
CONCAT    = "CONCAT"
HASH      = "HASH"


## IDENTIFIERS + LITERALS
IDENT   = "IDENT"
STRLIT  = "STRLIT"
INT     = "INT"
FLOAT   = "FLOAT"
HEXNUM  = "HEXNUM"
OCTNUM  = "OCTNUM"
BINNUM  = "BINNUM"
SCINUM  = "SCINUM"
LIST    = "LIST"
EOF     = "EOF"
ILLEGAL = "ILLEGAL"

NUMBERS = [INT, FLOAT, HEXNUM, OCTNUM, BINNUM, SCINUM]

ESCAPES = '\b\f\n\r\t\\'