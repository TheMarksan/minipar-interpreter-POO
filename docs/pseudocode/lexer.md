# Pseudocódigo do Lexer - MiniPar

## Estrutura Principal

```pseudocode
CLASSE Lexer:
    ATRIBUTOS:
        source_code: string
        position: inteiro
        line: inteiro
        column: inteiro
        keywords: dicionário<string, TokenType>
    
    MÉTODO construtor(source_code: string):
        this.source_code = source_code
        this.position = 0
        this.line = 1
        this.column = 1
        
        // Inicializar dicionário de palavras-chave (case-insensitive)
        this.keywords = {
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
            "this": TokenType.THIS
        }
```

## Métodos Utilitários com Lookahead

```pseudocode
    // LOOKAHEAD: Examina o próximo caractere sem consumi-lo
    MÉTODO peek(): char
        SE position < tamanho(source_code) ENTÃO
            RETORNAR source_code[position]  // Lookahead de 1 caractere
        SENÃO
            RETORNAR '\0'
        FIM SE
    
    MÉTODO advance(): char
        char = peek()  // Usa lookahead antes de avançar
        position = position + 1
        
        SE char == '\n' ENTÃO
            line = line + 1
            column = 1
        SENÃO
            column = column + 1
        FIM SE
        
        RETORNAR char
    
    // LOOKAHEAD: Verifica se o próximo caractere corresponde ao esperado
    MÉTODO match(expected: char): boolean
        SE peek() == expected ENTÃO  // Lookahead para verificar
            advance()  // Só consome se corresponder
            RETORNAR verdadeiro
        SENÃO
            RETORNAR falso
        FIM SE
    
    MÉTODO add_token(tokens: lista, type_: TokenType, lexeme: string, line: inteiro, column: inteiro):
        token = novo Token(type_, lexeme, line, column)
        adicionar token à lista tokens
```

## Algoritmo Principal de Tokenização

```pseudocode
    MÉTODO tokenize(): lista<Token>
        tokens = nova lista vazia
        
        ENQUANTO position < tamanho(source_code) FAÇA
            char = advance()
            start_line = line
            start_col = column - 1
            
            // Ignorar espaços em branco
            SE char é espaço EM BRANCO ENTÃO
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Comentários -------------------
            SE char == '#' ENTÃO
                lexeme = ""
                // LOOKAHEAD: Verifica próximo caractere antes de consumir
                ENQUANTO peek() != '\n' E peek() != '\0' FAÇA
                    lexeme = lexeme + advance()
                FIM ENQUANTO
                add_token(tokens, TokenType.COMMENT, lexeme, start_line, start_col)
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Operador de divisão -------------------
            SE char == '/' ENTÃO
                add_token(tokens, TokenType.DIV, '/', start_line, start_col)
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Strings -------------------
            SE char == '"' ENTÃO
                lexeme = ""
                // LOOKAHEAD: Examina caracteres até encontrar aspas de fechamento
                ENQUANTO peek() != '"' E peek() != '\0' FAÇA
                    lexeme = lexeme + advance()
                FIM ENQUANTO
                
                // LOOKAHEAD: Verifica se chegou ao fim do arquivo
                SE peek() == '\0' ENTÃO
                    add_token(tokens, TokenType.UNKNOWN, '"' + lexeme, start_line, start_col)
                    SAIR do loop
                SENÃO
                    advance() // consumir aspas de fechamento
                    add_token(tokens, TokenType.TEXT, lexeme, start_line, start_col)
                FIM SE
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Números -------------------
            SE char é dígito ENTÃO
                lexeme = char
                // LOOKAHEAD: Consome dígitos enquanto houver
                ENQUANTO peek() é dígito FAÇA
                    lexeme = lexeme + advance()
                FIM ENQUANTO
                
                // LOOKAHEAD: Verifica se é número decimal
                SE peek() == '.' ENTÃO
                    lexeme = lexeme + advance()
                    // LOOKAHEAD: Consome dígitos após o ponto decimal
                    ENQUANTO peek() é dígito FAÇA
                        lexeme = lexeme + advance()
                    FIM ENQUANTO
                FIM SE
                
                add_token(tokens, TokenType.NUMBER, lexeme, start_line, start_col)
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Identificadores e Palavras-chave -------------------
            SE char é letra OU char == '_' ENTÃO
                lexeme = char
                // LOOKAHEAD: Consome caracteres alfanuméricos
                ENQUANTO peek() é alfanumérico OU peek() == '_' FAÇA
                    lexeme = lexeme + advance()
                FIM ENQUANTO
                
                // Busca case-insensitive no dicionário de palavras-chave
                lexeme_lower = converter lexeme para minúsculas
                SE keywords contém lexeme_lower ENTÃO
                    type_ = keywords[lexeme_lower]
                SENÃO
                    type_ = TokenType.IDENT
                FIM SE
                
                add_token(tokens, type_, lexeme, start_line, start_col)
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Operadores compostos com LOOKAHEAD -------------------
            SE char == '=' ENTÃO
                // LOOKAHEAD: Verifica se é == ou apenas =
                SE match('=') ENTÃO  // match() usa lookahead internamente
                    add_token(tokens, TokenType.EQ, '==', start_line, start_col)
                SENÃO
                    add_token(tokens, TokenType.ASSIGN, '=', start_line, start_col)
                FIM SE
                CONTINUAR próxima iteração
            FIM SE
            
            SE char == '!' ENTÃO
                // LOOKAHEAD: Verifica se é != ou apenas !
                SE match('=') ENTÃO  // match() usa lookahead internamente
                    add_token(tokens, TokenType.NEQ, '!=', start_line, start_col)
                SENÃO
                    add_token(tokens, TokenType.UNKNOWN, '!', start_line, start_col)
                FIM SE
                CONTINUAR próxima iteração
            FIM SE
            
            SE char == '>' ENTÃO
                // LOOKAHEAD: Verifica se é >= ou apenas >
                SE match('=') ENTÃO  // match() usa lookahead internamente
                    add_token(tokens, TokenType.GTE, '>=', start_line, start_col)
                SENÃO
                    add_token(tokens, TokenType.GT, '>', start_line, start_col)
                FIM SE
                CONTINUAR próxima iteração
            FIM SE
            
            SE char == '<' ENTÃO
                // LOOKAHEAD: Verifica se é <= ou apenas <
                SE match('=') ENTÃO  // match() usa lookahead internamente
                    add_token(tokens, TokenType.LTE, '<=', start_line, start_col)
                SENÃO
                    add_token(tokens, TokenType.LT, '<', start_line, start_col)
                FIM SE
                CONTINUAR próxima iteração
            FIM SE
            
            // ------------------- Símbolos isolados -------------------
            symbols = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MUL,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON,
                '.': TokenType.DOT,
                ',': TokenType.COMMA
            }
            
            SE symbols contém char ENTÃO
                add_token(tokens, symbols[char], char, start_line, start_col)
            SENÃO
                add_token(tokens, TokenType.UNKNOWN, char, start_line, start_col)
            FIM SE
        
        FIM ENQUANTO
        
        // Adicionar token EOF
        add_token(tokens, TokenType.EOF, '', line, column)
        RETORNAR tokens
    
FIM MÉTODO
```

## Características Principais

### 1. **Lookahead de 1 Caractere**
- **FUNDAMENTAL**: O lexer utiliza lookahead de 1 caractere através do método `peek()`
- **Vantagens do Lookahead**:
  - Permite distinguir operadores simples de compostos (`=` vs `==`, `>` vs `>=`)
  - Evita backtracking ao reconhecer tokens
  - Facilita o reconhecimento de números decimais (verifica se há `.` após dígitos)
  - Permite parar corretamente em delimitadores de strings e comentários
- **Exemplos de Uso**:
  - `>=`: Consome `>`, faz lookahead para `=`, se encontrar consome também
  - `123.45`: Consome dígitos, faz lookahead para `.`, se encontrar continua
  - `"string"`: Consome caracteres até fazer lookahead e encontrar `"`

### 2. **Case-Insensitive Keywords**
- As palavras-chave são reconhecidas independentemente de maiúsculas/minúsculas
- `class`, `Class`, `CLASS` são todas reconhecidas como `TokenType.CLASS`

### 3. **Comentários**
- Formato: `# comentário até o fim da linha`
- Conforme especificação da BNF
- Usa lookahead para encontrar fim da linha

### 4. **Strings**
- Delimitadas por aspas duplas `"texto"`
- Suporte a escape de caracteres
- Detecção de strings não fechadas usando lookahead

### 5. **Números**
- Inteiros: `123`
- Decimais: `123.456`
- Suporte a números de ponto flutuante com lookahead para detectar o ponto

### 6. **Identificadores**
- Começam com letra ou underscore
- Podem conter letras, dígitos e underscores
- Case-sensitive para nomes de variáveis, métodos, etc.

### 7. **Operadores**
- Aritméticos: `+`, `-`, `*`, `/`
- Relacionais: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Atribuição: `=`
- **Operadores compostos usam lookahead**: `==`, `!=`, `>=`, `<=`

### 8. **Delimitadores**
- Parênteses: `(`, `)`
- Chaves: `{`, `}`
- Colchetes: `[`, `]`
- Ponto-e-vírgula: `;`
- Vírgula: `,`
- Ponto: `.`

### 9. **Controle de Posição**
- Rastreamento de linha e coluna para relatórios de erro
- Suporte a múltiplas linhas
- Tratamento adequado de quebras de linha

### 10. **Tokens Especiais**
- `EOF`: Fim do arquivo
- `UNKNOWN`: Caracteres não reconhecidos
- `COMMENT`: Comentários preservados para análise

## Análise do Lookahead

### **Técnica Utilizada: Lookahead LL(1)**
- **LL(1)**: Left-to-right, Leftmost derivation, 1 symbol lookahead
- **Não-determinismo resolvido**: O lookahead resolve ambiguidades entre tokens
- **Eficiência**: Reconhecimento em uma única passada sem backtracking

### **Situações Onde o Lookahead é Crítico:**

1. **Operadores Compostos**:
   ```
   '>' seguido de '=' → '>='
   '>' seguido de qualquer outro → '>'
   ```

2. **Números Decimais**:
   ```
   '123' seguido de '.' → continua lendo número decimal
   '123' seguido de qualquer outro → número inteiro
   ```

3. **Strings e Comentários**:
   ```
   '"' → continua até encontrar '"' de fechamento
   '#' → continua até encontrar '\n' ou EOF
   ```

4. **Identificadores vs Keywords**:
   ```
   Lê sequência completa de caracteres alfanuméricos
   Depois verifica se é palavra-chave ou identificador
   ```
