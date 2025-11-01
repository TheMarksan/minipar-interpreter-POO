from dataclasses import dataclass
from lexer.token_type import TokenType

@dataclass
class Token:
    """
    Representa um token único gerado pelo analisador léxico.
    """
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.lexeme}', linha={self.line}, coluna={self.column})"
