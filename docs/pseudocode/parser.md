# Pseudocódigo do Parser - MiniPar

## Estrutura Principal

```pseudocode
CLASSE Parser:
    ATRIBUTOS:
        tokens: lista<Token>
        pos: inteiro  // Posição atual na lista de tokens
    
    MÉTODO construtor(tokens: lista<Token>):
        this.tokens = tokens
        this.pos = 0
```

## Métodos Utilitários com Lookahead

```pseudocode
    // LOOKAHEAD: Examina o token atual sem consumi-lo
    MÉTODO current_token(): Token
        SE pos < tamanho(tokens) ENTÃO
            RETORNAR tokens[pos]  // Lookahead no token atual
        SENÃO
            RETORNAR tokens[último]  // EOF
        FIM SE
    
    // LOOKAHEAD: Examina token futuro sem consumi-lo
    MÉTODO peek(offset: inteiro = 1): Token
        pos_futura = pos + offset
        SE pos_futura < tamanho(tokens) ENTÃO
            RETORNAR tokens[pos_futura]  // Lookahead no token futuro
        SENÃO
            RETORNAR tokens[último]  // EOF
        FIM SE
    
    // Consome o token atual e avança
    MÉTODO advance(): Token
        token = current_token()
        SE token.type != TokenType.EOF ENTÃO
            pos = pos + 1
        FIM SE
        RETORNAR token
    
    // Verifica e consome token esperado ou gera erro
    MÉTODO expect(token_type: TokenType): Token
        token = current_token()
        SE token.type != token_type ENTÃO
            LANÇAR SyntaxError("Expected " + token_type + ", got " + token.type 
                              + " at line " + token.line + ", column " + token.column)
        FIM SE
        RETORNAR advance()
    
    // LOOKAHEAD: Verifica se o token atual é de um dos tipos especificados
    MÉTODO match(*token_types: TokenType): boolean
        RETORNAR current_token().type está em token_types
    
    // Pula comentários
    MÉTODO skip_comments():
        ENQUANTO match(TokenType.COMMENT) FAÇA
            advance()
        FIM ENQUANTO
```

## Método Principal de Parsing

```pseudocode
    MÉTODO parse(): ProgramNode
        RETORNAR programa_minipar()
```

## Parsing do Programa Principal

```pseudocode
    MÉTODO programa_minipar(): ProgramNode
        program = novo ProgramNode()
        skip_comments()
        
        ENQUANTO NÃO match(TokenType.EOF) FAÇA
            skip_comments()
            
            // LOOKAHEAD: Verifica tipo do próximo elemento
            SE match(TokenType.CLASS) ENTÃO
                program.children.adicionar(parse_class())
                
            SENÃO SE match(TokenType.VOID, TokenType.INT, TokenType.FLOAT, 
                           TokenType.STRING, TokenType.BOOL) ENTÃO
                // LOOKAHEAD de 2 tokens: verifica se é função
                SE peek().type == TokenType.IDENT E peek(2).type == TokenType.LPAREN ENTÃO
                    program.children.adicionar(parse_function())
                SENÃO
                    program.children.adicionar(parse_declaration())
                FIM SE
                
            SENÃO SE match(TokenType.IDENT) ENTÃO
                // LOOKAHEAD: verifica se é instanciação ou declaração
                SE peek().type == TokenType.IDENT ENTÃO
                    program.children.adicionar(parse_declaration())
                SENÃO
                    program.children.adicionar(parse_statement())
                FIM SE
                
            SENÃO SE match(TokenType.C_CHANNEL) ENTÃO
                program.children.adicionar(parse_declaration())
                
            SENÃO SE match(TokenType.SEQ, TokenType.PAR) ENTÃO
                program.children.adicionar(parse_block())
                
            SENÃO SE match(TokenType.COMMENT) ENTÃO
                advance()
                
            SENÃO
                SAIR do loop
            FIM SE
            
            skip_comments()
        FIM ENQUANTO
        
        RETORNAR program
```

## Parsing de Classes

```pseudocode
    MÉTODO parse_class(): ClassNode
        expect(TokenType.CLASS)
        name = expect(TokenType.IDENT).lexeme
        
        parent = NULL
        // LOOKAHEAD: Verifica se há herança
        SE match(TokenType.EXTENDS) ENTÃO
            advance()
            parent = expect(TokenType.IDENT).lexeme
        FIM SE
        
        expect(TokenType.LBRACE)
        
        attributes = nova lista vazia
        methods = nova lista vazia
        
        skip_comments()
        ENQUANTO NÃO match(TokenType.RBRACE) FAÇA
            SE match(TokenType.VOID, TokenType.INT, TokenType.FLOAT, 
                     TokenType.STRING, TokenType.BOOL, TokenType.IDENT, TokenType.C_CHANNEL) ENTÃO
                
                return_type_token = current_token()
                return_type = advance().lexeme
                name_token = expect(TokenType.IDENT)
                
                // LOOKAHEAD: Verifica se é método ou atributo
                SE match(TokenType.LPAREN) ENTÃO
                    // É um método
                    advance()
                    parameters = parse_parameters()
                    expect(TokenType.RPAREN)
                    expect(TokenType.LBRACE)
                    body = parse_statements_list()
                    expect(TokenType.RBRACE)
                    
                    method = novo MethodNode(return_type, name_token.lexeme, parameters, body)
                    methods.adicionar(method)
                    
                SENÃO SE match(TokenType.LBRACKET) ENTÃO
                    // É um atributo array
                    advance()
                    SE NÃO match(TokenType.RBRACKET) ENTÃO
                        array_size = parse_expression()
                        expect(TokenType.RBRACKET)
                        
                        // LOOKAHEAD: Verifica se é array 2D
                        SE match(TokenType.LBRACKET) ENTÃO
                            advance()
                            array_size2 = parse_expression()
                            expect(TokenType.RBRACKET)
                            attr = novo AttributeNode(return_type, name_token.lexeme, 
                                                     True, [array_size, array_size2], True, [array_size, array_size2])
                        SENÃO
                            attr = novo AttributeNode(return_type, name_token.lexeme, 
                                                     True, array_size, False, NULL)
                        FIM SE
                    SENÃO
                        expect(TokenType.RBRACKET)
                        attr = novo AttributeNode(return_type, name_token.lexeme, True, NULL, False, NULL)
                    FIM SE
                    
                    attributes.adicionar(attr)
                    SE match(TokenType.SEMICOLON) ENTÃO
                        advance()
                    FIM SE
                    
                SENÃO
                    // É um atributo simples
                    attr = novo AttributeNode(return_type, name_token.lexeme, False, NULL, False, NULL)
                    attributes.adicionar(attr)
                    SE match(TokenType.SEMICOLON) ENTÃO
                        advance()
                    FIM SE
                FIM SE
            FIM SE
            skip_comments()
        FIM ENQUANTO
        
        expect(TokenType.RBRACE)
        RETORNAR novo ClassNode(name, parent, attributes, methods)
```

## Parsing de Funções

```pseudocode
    MÉTODO parse_function(): FunctionNode
        return_type = advance().lexeme
        name = expect(TokenType.IDENT).lexeme
        expect(TokenType.LPAREN)
        
        parameters = nova lista vazia
        SE NÃO match(TokenType.RPAREN) ENTÃO
            ENQUANTO verdadeiro FAÇA
                param_type = advance().lexeme
                param_name = expect(TokenType.IDENT).lexeme
                
                // LOOKAHEAD: Verifica se é parâmetro array
                SE match(TokenType.LBRACKET) ENTÃO
                    advance()
                    expect(TokenType.RBRACKET)
                    // Marca como array no parâmetro
                FIM SE
                
                parameters.adicionar((param_type, param_name))
                
                SE NÃO match(TokenType.COMMA) ENTÃO
                    SAIR do loop
                FIM SE
                advance()
            FIM ENQUANTO
        FIM SE
        
        expect(TokenType.RPAREN)
        expect(TokenType.LBRACE)
        body = parse_statements_list()
        expect(TokenType.RBRACE)
        
        RETORNAR novo FunctionNode(return_type, name, parameters, body)
```

## Parsing de Declarações

```pseudocode
    MÉTODO parse_declaration(): DeclarationNode
        type_name = advance().lexeme
        identifier = expect(TokenType.IDENT).lexeme
        
        is_array = False
        is_2d_array = False
        array_size = NULL
        array_dimensions = NULL
        initial_value = NULL
        
        // LOOKAHEAD: Verifica se é array
        SE match(TokenType.LBRACKET) ENTÃO
            advance()
            is_array = True
            
            SE NÃO match(TokenType.RBRACKET) ENTÃO
                first_size = parse_expression()
                expect(TokenType.RBRACKET)
                
                // LOOKAHEAD: Verifica se é array 2D
                SE match(TokenType.LBRACKET) ENTÃO
                    advance()
                    is_2d_array = True
                    second_size = parse_expression()
                    expect(TokenType.RBRACKET)
                    array_dimensions = [first_size, second_size]
                SENÃO
                    array_size = first_size
                FIM SE
            SENÃO
                expect(TokenType.RBRACKET)
            FIM SE
        FIM SE
        
        // LOOKAHEAD: Verifica se há inicialização
        SE match(TokenType.ASSIGN) ENTÃO
            advance()
            SE match(TokenType.LBRACE) ENTÃO
                initial_value = parse_brace_init()
            SENÃO SE match(TokenType.LBRACKET) ENTÃO
                initial_value = parse_array_init()
            SENÃO
                initial_value = parse_expression()
            FIM SE
        FIM SE
        
        SE match(TokenType.SEMICOLON) ENTÃO
            advance()
        FIM SE
        
        RETORNAR novo DeclarationNode(type_name, identifier, initial_value, 
                                     is_array, array_size, is_2d_array, array_dimensions)
```

## Parsing de Blocos SEQ/PAR

```pseudocode
    MÉTODO parse_block(): BlockNode
        block_type = advance().lexeme.to_lower()  // "seq" ou "par"
        
        // LOOKAHEAD: Verifica se tem chaves
        SE match(TokenType.LBRACE) ENTÃO
            advance()
            statements = parse_statements_list()
            expect(TokenType.RBRACE)
        SENÃO
            // Bloco sem chaves (não recomendado, pode causar problemas)
            statements = nova lista vazia
            ENQUANTO NÃO match(TokenType.EOF, TokenType.SEQ, TokenType.PAR) FAÇA
                skip_comments()
                SE match(TokenType.EOF, TokenType.SEQ, TokenType.PAR) ENTÃO
                    SAIR do loop
                FIM SE
                stmt = parse_statement()
                SE stmt != NULL ENTÃO
                    statements.adicionar(stmt)
                FIM SE
                SE match(TokenType.SEQ, TokenType.PAR) ENTÃO
                    SAIR do loop
                FIM SE
            FIM ENQUANTO
        FIM SE
        
        RETORNAR novo BlockNode(block_type, statements)
```

## Parsing de Statements

```pseudocode
    MÉTODO parse_statements_list(): lista<ASTNode>
        statements = nova lista vazia
        skip_comments()
        
        ENQUANTO NÃO match(TokenType.RBRACE, TokenType.EOF) FAÇA
            skip_comments()
            SE match(TokenType.RBRACE) ENTÃO
                SAIR do loop
            FIM SE
            
            stmt = parse_statement()
            SE stmt != NULL ENTÃO
                statements.adicionar(stmt)
            FIM SE
            skip_comments()
        FIM ENQUANTO
        
        RETORNAR statements
    
    MÉTODO parse_statement(): ASTNode
        skip_comments()
        
        // LOOKAHEAD: Determina tipo do statement
        SE match(TokenType.SEQ, TokenType.PAR) ENTÃO
            RETORNAR parse_block()
            
        SENÃO SE match(TokenType.IF) ENTÃO
            RETORNAR parse_if()
            
        SENÃO SE match(TokenType.WHILE) ENTÃO
            RETORNAR parse_while()
            
        SENÃO SE match(TokenType.FOR) ENTÃO
            RETORNAR parse_for()
            
        SENÃO SE match(TokenType.PRINT) ENTÃO
            RETORNAR parse_print()
            
        SENÃO SE match(TokenType.RETURN) ENTÃO
            RETORNAR parse_return()
            
        SENÃO SE match(TokenType.THIS) ENTÃO
            obj_name = advance().lexeme
            SE match(TokenType.DOT) ENTÃO
                expect(TokenType.DOT)
                attr_name = expect(TokenType.IDENT).lexeme
                
                // LOOKAHEAD: Verifica operação com this
                SE match(TokenType.LBRACKET) ENTÃO
                    // Acesso a array: this.attr[index]
                    // ... (implementação de array access)
                SENÃO SE match(TokenType.ASSIGN) ENTÃO
                    // Atribuição: this.attr = valor
                    // ... (implementação de atribuição)
                SENÃO SE match(TokenType.LPAREN) ENTÃO
                    // Chamada de método: this.metodo()
                    // ... (implementação de chamada de método)
                FIM SE
            FIM SE
            
        SENÃO SE match(TokenType.INT, TokenType.FLOAT, TokenType.STRING, 
                       TokenType.BOOL, TokenType.C_CHANNEL) ENTÃO
            RETORNAR parse_declaration()
            
        SENÃO SE match(TokenType.IDENT) ENTÃO
            // LOOKAHEAD de 1 token: determina o tipo de statement
            SE peek().type == TokenType.IDENT ENTÃO
                // Declaração de variável customizada: Classe var;
                RETORNAR parse_declaration()
                
            SENÃO SE peek().type == TokenType.DOT ENTÃO
                // Acesso a objeto: obj.metodo() ou obj.atributo
                object_name = advance().lexeme
                expect(TokenType.DOT)
                
                method_token = current_token()
                SE match(TokenType.SEND) ENTÃO
                    // obj.SEND(...)
                    // ... (implementação)
                SENÃO SE match(TokenType.RECEIVE) ENTÃO
                    // obj.RECEIVE(...)
                    // ... (implementação)
                SENÃO SE match(TokenType.IDENT) ENTÃO
                    // obj.metodo() ou obj.atributo
                    // ... (implementação)
                FIM SE
                
            SENÃO SE peek().type == TokenType.LBRACKET ENTÃO
                // Acesso ou atribuição a array: arr[index]
                // ... (implementação)
                
            SENÃO SE peek().type == TokenType.ASSIGN ENTÃO
                // Atribuição: var = valor
                identifier = advance().lexeme
                expect(TokenType.ASSIGN)
                expression = parse_expression()
                SE match(TokenType.SEMICOLON) ENTÃO
                    advance()
                FIM SE
                RETORNAR novo AssignmentNode(identifier, expression)
                
            SENÃO SE peek().type == TokenType.LPAREN ENTÃO
                // Chamada de função: func()
                name = advance().lexeme
                expect(TokenType.LPAREN)
                arguments = parse_arguments()
                expect(TokenType.RPAREN)
                SE match(TokenType.SEMICOLON) ENTÃO
                    advance()
                FIM SE
                RETORNAR novo FunctionCallNode(name, arguments)
            FIM SE
            
        SENÃO SE match(TokenType.COMMENT) ENTÃO
            advance()
            RETORNAR NULL
        FIM SE
        
        SE match(TokenType.SEMICOLON) ENTÃO
            advance()
        FIM SE
        
        RETORNAR NULL
```

## Parsing de Estruturas de Controle

```pseudocode
    MÉTODO parse_if(): IfNode
        expect(TokenType.IF)
        condition = parse_condition()
        expect(TokenType.LBRACE)
        then_body = parse_statements_list()
        expect(TokenType.RBRACE)
        
        else_body = NULL
        // LOOKAHEAD: Verifica se há else
        SE match(TokenType.ELSE) ENTÃO
            advance()
            // LOOKAHEAD: Verifica se é else if
            SE match(TokenType.IF) ENTÃO
                else_body = [parse_if()]  // Recursivo para else if
            SENÃO
                expect(TokenType.LBRACE)
                else_body = parse_statements_list()
                expect(TokenType.RBRACE)
            FIM SE
        FIM SE
        
        RETORNAR novo IfNode(condition, then_body, else_body)
    
    MÉTODO parse_while(): WhileNode
        expect(TokenType.WHILE)
        condition = parse_condition()
        expect(TokenType.LBRACE)
        body = parse_statements_list()
        expect(TokenType.RBRACE)
        RETORNAR novo WhileNode(condition, body)
    
    MÉTODO parse_for(): ForNode
        expect(TokenType.FOR)
        var = expect(TokenType.IDENT).lexeme
        expect(TokenType.ASSIGN)
        init_expr = parse_expression()
        expect(TokenType.SEMICOLON)
        condition = parse_condition()
        expect(TokenType.SEMICOLON)
        
        increment_var = expect(TokenType.IDENT).lexeme
        expect(TokenType.ASSIGN)
        increment_expr = parse_expression()
        
        expect(TokenType.LBRACE)
        body = parse_statements_list()
        expect(TokenType.RBRACE)
        
        RETORNAR novo ForNode(var, init_expr, condition, 
                            novo AssignmentNode(increment_var, increment_expr), body)
```

## Parsing de Comandos

```pseudocode
    MÉTODO parse_print(): PrintNode
        expect(TokenType.PRINT)
        expect(TokenType.LPAREN)
        expression = parse_expression()
        expect(TokenType.RPAREN)
        SE match(TokenType.SEMICOLON) ENTÃO
            advance()
        FIM SE
        RETORNAR novo PrintNode(expression)
    
    MÉTODO parse_return(): ReturnNode
        expect(TokenType.RETURN)
        expression = parse_expression()
        SE match(TokenType.SEMICOLON) ENTÃO
            advance()
        FIM SE
        RETORNAR novo ReturnNode(expression)
    
    MÉTODO parse_arguments(): lista<ASTNode>
        args = nova lista vazia
        SE match(TokenType.RPAREN) ENTÃO
            RETORNAR args
        FIM SE
        
        ENQUANTO verdadeiro FAÇA
            args.adicionar(parse_expression())
            SE NÃO match(TokenType.COMMA) ENTÃO
                SAIR do loop
            FIM SE
            advance()
        FIM ENQUANTO
        
        RETORNAR args
```

## Parsing de Expressões com Precedência

```pseudocode
    // Condições (menor precedência que expressões)
    MÉTODO parse_condition(): ASTNode
        left = parse_logical_and()
        RETORNAR left
    
    MÉTODO parse_logical_and(): ASTNode
        left = parse_logical_or()
        
        // LOOKAHEAD: Verifica operador &&
        ENQUANTO match(TokenType.AND) FAÇA
            operator = advance().lexeme
            right = parse_logical_or()
            left = novo BinaryOpNode(left, operator, right)
        FIM ENQUANTO
        
        RETORNAR left
    
    MÉTODO parse_logical_or(): ASTNode
        left = parse_relational()
        
        // LOOKAHEAD: Verifica operador ||
        ENQUANTO match(TokenType.OR) FAÇA
            operator = advance().lexeme
            right = parse_relational()
            left = novo BinaryOpNode(left, operator, right)
        FIM ENQUANTO
        
        RETORNAR left
    
    MÉTODO parse_relational(): ASTNode
        left = parse_expression()
        
        // LOOKAHEAD: Verifica operador relacional
        SE match(TokenType.EQ, TokenType.NEQ, TokenType.GT, 
                 TokenType.LT, TokenType.GTE, TokenType.LTE) ENTÃO
            operator = advance().lexeme
            right = parse_expression()
            RETORNAR novo ConditionNode(left, operator, right)
        FIM SE
        
        RETORNAR left
    
    // Expressões aritméticas
    MÉTODO parse_expression(): ASTNode
        RETORNAR parse_additive()
    
    MÉTODO parse_additive(): ASTNode
        left = parse_multiplicative()
        
        // LOOKAHEAD: Verifica operadores + ou -
        ENQUANTO match(TokenType.PLUS, TokenType.MINUS) FAÇA
            operator = advance().lexeme
            right = parse_multiplicative()
            left = novo BinaryOpNode(left, operator, right)
        FIM ENQUANTO
        
        RETORNAR left
    
    MÉTODO parse_multiplicative(): ASTNode
        left = parse_unary()
        
        // LOOKAHEAD: Verifica operadores * ou /
        ENQUANTO match(TokenType.MUL, TokenType.DIV) FAÇA
            operator = advance().lexeme
            right = parse_unary()
            left = novo BinaryOpNode(left, operator, right)
        FIM ENQUANTO
        
        RETORNAR left
    
    MÉTODO parse_unary(): ASTNode
        // LOOKAHEAD: Determina tipo do valor
        SE match(TokenType.NUMBER) ENTÃO
            value = advance().lexeme
            RETORNAR novo NumberNode(value)
            
        SENÃO SE match(TokenType.TEXT) ENTÃO
            value = advance().lexeme
            RETORNAR novo StringNode(value)
            
        SENÃO SE match(TokenType.NEW) ENTÃO
            advance()
            class_name = expect(TokenType.IDENT).lexeme
            expect(TokenType.LPAREN)
            expect(TokenType.RPAREN)
            RETORNAR novo NewExpressionNode(class_name)
            
        SENÃO SE match(TokenType.THIS) ENTÃO
            name = advance().lexeme
            // LOOKAHEAD: Verifica se há acesso a atributo
            SE match(TokenType.DOT) ENTÃO
                // this.atributo ou this.metodo()
                // ... (implementação)
            FIM SE
            RETORNAR novo IdentifierNode(name)
            
        SENÃO SE match(TokenType.IDENT) ENTÃO
            name = advance().lexeme
            // LOOKAHEAD: Verifica o que vem após o identificador
            SE match(TokenType.LPAREN) ENTÃO
                // Chamada de função
                advance()
                args = parse_arguments()
                expect(TokenType.RPAREN)
                RETORNAR novo FunctionCallNode(name, args)
                
            SENÃO SE match(TokenType.LBRACKET) ENTÃO
                // Acesso a array
                // ... (implementação)
                
            SENÃO SE match(TokenType.DOT) ENTÃO
                // Acesso a atributo ou método de objeto
                // ... (implementação)
            FIM SE
            
            RETORNAR novo IdentifierNode(name)
            
        SENÃO SE match(TokenType.LPAREN) ENTÃO
            advance()
            expr = parse_expression()
            expect(TokenType.RPAREN)
            RETORNAR expr
            
        SENÃO SE match(TokenType.STRLEN, TokenType.SUBSTR, TokenType.CHARAT, 
                       TokenType.INDEXOF, TokenType.PARSEINT) ENTÃO
            name = advance().lexeme
            expect(TokenType.LPAREN)
            args = parse_arguments()
            expect(TokenType.RPAREN)
            RETORNAR novo FunctionCallNode(name, args)
            
        SENÃO SE match(TokenType.MINUS) ENTÃO
            operator = advance().lexeme
            operand = parse_unary()
            RETORNAR novo UnaryOpNode(operator, operand)
            
        SENÃO
            LANÇAR SyntaxError("Unexpected token: " + current_token())
        FIM SE
```

## Características Principais

### 1. **Lookahead LL(k)**
- **LL(k)**: Left-to-right, Leftmost derivation, k-symbol lookahead
- **Lookahead de 1 token** na maioria dos casos: `current_token()`
- **Lookahead de 2+ tokens** quando necessário: `peek(1)`, `peek(2)`
- **Decisões baseadas em lookahead**: Distingue declarações, atribuições, chamadas

### 2. **Descendente Recursivo (Recursive Descent)**
- Um método por não-terminal da gramática
- Chamadas recursivas para processar sub-estruturas
- Suporte a recursão para `else if` aninhados

### 3. **Precedência de Operadores**
- **Menor precedência**: Operadores lógicos (`||`, `&&`)
- **Precedência média**: Operadores relacionais (`==`, `!=`, `>`, `<`, `>=`, `<=`)
- **Precedência alta**: Operadores aditivos (`+`, `-`)
- **Maior precedência**: Operadores multiplicativos (`*`, `/`)
- **Precedência máxima**: Unários e primários (números, identificadores, parênteses)

### 4. **Tratamento de Ambiguidades**
- **Lookahead resolve**: função vs declaração, atribuição vs chamada
- **Peek(2)**: Identifica funções (IDENT + LPAREN)
- **Context-sensitive**: Diferentes interpretações de IDENT baseado no contexto

### 5. **Suporte a Estruturas Aninhadas**
- Blocos SEQ/PAR podem conter outros blocos
- If/else if/else em cadeia
- Arrays multidimensionais
- Objetos com atributos e métodos

### 6. **Recuperação de Erros**
- Mensagens detalhadas com linha e coluna
- Pula comentários automaticamente
- Tratamento de tokens opcio nais (ponto-e-vírgula)

### 7. **Case-Insensitive Keywords**
- Palavras-chave reconhecidas independentemente de case
- Identificadores mantêm case-sensitivity

### 8. **Suporte a Paralelismo**
- Blocos PAR para execução paralela
- Blocos SEQ para execução sequencial
- Aninhamento de blocos permitido

### 9. **Orientação a Objetos**
- Classes com herança (extends)
- Atributos e métodos
- Instanciação com `new`
- Acesso a membros com `.`
- Suporte a `this`

### 10. **Comunicação entre Processos**
- Canais: `C_CHANNEL`
- Operações: `SEND` e `RECEIVE`
- Suporte a múltiplos valores em send/receive
