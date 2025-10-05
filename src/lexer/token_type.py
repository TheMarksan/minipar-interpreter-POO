from enum import Enum, auto

class TokenType(Enum):
    # Palavras-chave
    CLASS = auto()
    EXTENDS = auto()
    VOID = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    C_CHANNEL = auto()
    SEQ = auto()
    PAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    NEW = auto()
    PRINT = auto()
    INPUT = auto()
    SEND = auto()
    RECEIVE = auto()
    RETURN = auto()
    SPLIT = auto()
    LEN = auto()
    TO_INT = auto()
    THIS = auto()

    # Operadores
    ASSIGN = auto()       # =
    PLUS = auto()         # +
    MINUS = auto()        # -
    MUL = auto()          # *
    DIV = auto()          # /
    EQ = auto()           # ==
    NEQ = auto()          # !=
    GT = auto()           # >
    LT = auto()           # <
    GTE = auto()          # >=
    LTE = auto()          # <=

    # Delimitadores
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    SEMICOLON = auto()    # ;
    DOT = auto()          # .
    COMMA = auto()

    # Literais e identificadores
    IDENT = auto()
    NUMBER = auto()
    TEXT = auto()
    COMMENT = auto()
    
    # Outros
    UNKNOWN = auto()
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]

    EOF = auto()
