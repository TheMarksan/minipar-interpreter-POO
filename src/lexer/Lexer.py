import re
from .token_type import TokenType
from .token import Token

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.keywords = {
            "class": TokenType.CLASS,
            "extends": TokenType.EXTENDS,
            "void": TokenType.VOID,
            "int": TokenType.INT,
            "float": TokenType.FLOAT,
            "string": TokenType.STRING,
            "bool": TokenType.BOOL,
            "c_channel": TokenType.C_CHANNEL,
            "seq": TokenType.SEQ,
            "par": TokenType.PAR,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "new": TokenType.NEW,
            "print": TokenType.PRINT,
            "input": TokenType.INPUT,
            "send": TokenType.SEND,
            "receive": TokenType.RECEIVE,
            "return": TokenType.RETURN,
            "split": TokenType.SPLIT,
            "len": TokenType.LEN,
            "to_int": TokenType.TO_INT,
            "this": TokenType.THIS,
            "strlen": TokenType.STRLEN,
            "substr": TokenType.SUBSTR,
            "charat": TokenType.CHARAT,
            "indexof": TokenType.INDEXOF,
            "parseint": TokenType.PARSEINT,
        }

    # ------------------- Métodos utilitários -------------------
    def peek(self):
        return self.source[self.position] if self.position < len(self.source) else '\0'

    def advance(self):
        char = self.peek()
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def match(self, expected):
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def add_token(self, tokens, type_, lexeme, line, column):
        tokens.append(Token(type_, lexeme, line, column))

    # ------------------- Função principal -------------------
    def tokenize(self):
        tokens = []

        while self.position < len(self.source):
            char = self.advance()
            start_line = self.line
            start_col = self.column - 1

            # Ignorar espaços e tabulações
            if char.isspace():
                continue

            # ------------------- Comentários -------------------
            if char == '#':
                # Comentário de linha conforme BNF (# até fim da linha)
                lexeme = ""
                while self.peek() != '\n' and self.peek() != '\0':
                    lexeme += self.advance()
                self.add_token(tokens, TokenType.COMMENT, lexeme, start_line, start_col)
                continue
            
            # ------------------- Operador de divisão e comentários C-style -------------------
            if char == '/':
                # Verificar se é // (comentário não suportado)
                if self.peek() == '/':
                    # Consumir o segundo /
                    self.advance()
                    # Consumir o resto da linha para contexto do erro
                    error_preview = ""
                    while self.peek() != '\n' and self.peek() != '\0' and len(error_preview) < 30:
                        error_preview += self.advance()
                    # Criar token de erro com mensagem clara
                    error_msg = f"Comentário '//' não suportado. Use '#' para comentários. Linha {start_line}"
                    self.add_token(tokens, TokenType.ERROR, error_msg, start_line, start_col)
                    continue
                # É apenas divisão
                self.add_token(tokens, TokenType.DIV, '/', start_line, start_col)
                continue

            # ------------------- Strings -------------------
            if char == '"':
                lexeme = ""
                while self.peek() != '"' and self.peek() != '\0':
                    lexeme += self.advance()
                if self.peek() == '\0':
                    self.add_token(tokens, TokenType.UNKNOWN, '"' + lexeme, start_line, start_col)
                    break
                self.advance()
                self.add_token(tokens, TokenType.TEXT, lexeme, start_line, start_col)
                continue

            # ------------------- Números -------------------
            if char.isdigit():
                lexeme = char
                while self.peek().isdigit():
                    lexeme += self.advance()
                if self.peek() == '.':
                    lexeme += self.advance()
                    while self.peek().isdigit():
                        lexeme += self.advance()
                    self.add_token(tokens, TokenType.NUMBER, lexeme, start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.NUMBER, lexeme, start_line, start_col)
                continue

            # ------------------- Identificadores e Palavras-chave -------------------
            if char.isalpha() or char == '_':
                lexeme = char
                while self.peek().isalnum() or self.peek() == '_':
                    lexeme += self.advance()
                # Case-insensitive keyword lookup
                type_ = self.keywords.get(lexeme.lower(), TokenType.IDENT)
                self.add_token(tokens, type_, lexeme, start_line, start_col)
                continue

            # ------------------- Operadores compostos -------------------
            if char == '&':
                if self.match('&'):
                    self.add_token(tokens, TokenType.AND, '&&', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.REFERENCE, '&', start_line, start_col)
                continue
            
            if char == '|':
                if self.match('|'):
                    self.add_token(tokens, TokenType.OR, '||', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.UNKNOWN, '|', start_line, start_col)
                continue

            if char == '=':
                if self.match('='):
                    self.add_token(tokens, TokenType.EQ, '==', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.ASSIGN, '=', start_line, start_col)
                continue

            if char == '!':
                if self.match('='):
                    self.add_token(tokens, TokenType.NEQ, '!=', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.UNKNOWN, '!', start_line, start_col)
                continue

            if char == '>':
                if self.match('='):
                    self.add_token(tokens, TokenType.GTE, '>=', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.GT, '>', start_line, start_col)
                continue

            if char == '<':
                if self.match('='):
                    self.add_token(tokens, TokenType.LTE, '<=', start_line, start_col)
                else:
                    self.add_token(tokens, TokenType.LT, '<', start_line, start_col)
                continue

            # ------------------- Símbolos isolados -------------------
            symbols = {
                '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MUL,
                '%': TokenType.MOD,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON, '.': TokenType.DOT,
                ',': TokenType.COMMA,
            }

            if char in symbols:
                self.add_token(tokens, symbols[char], char, start_line, start_col)
            else:
                self.add_token(tokens, TokenType.UNKNOWN, char, start_line, start_col)

        # EOF
        self.add_token(tokens, TokenType.EOF, '', self.line, self.column)
        return tokens
