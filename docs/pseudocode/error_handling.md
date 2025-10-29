# Pseudocódigo de Tratamento de Erros

## Visão Geral
O sistema de tratamento de erros do MiniPar é distribuído em várias camadas: Lexer, Parser, Semantic Analyzer e Interpreter. Cada camada detecta tipos específicos de erros e os reporta de forma clara ao usuário.

## Tipos de Erros

### 1. Erros Léxicos (Lexer)
```pseudocode
ERROS LÉXICOS:
    - Caractere inválido
    - String não fechada
    - Número mal formado
    - Token desconhecido
```

### 2. Erros Sintáticos (Parser)
```pseudocode
ERROS SINTÁTICOS:
    - Token inesperado
    - Estrutura gramatical inválida
    - Falta de delimitadores (, ), {, }, ;
    - Expressão mal formada
    - Declaração incompleta
```

### 3. Erros Semânticos (Semantic Analyzer)
```pseudocode
ERROS SEMÂNTICOS:
    - Variável não declarada
    - Variável declarada mais de uma vez no mesmo escopo
    - Tipo inválido
    - Incompatibilidade de tipos
    - Função não declarada
    - Classe não declarada
    - Número errado de parâmetros
```

### 4. Erros de Execução (Interpreter)
```pseudocode
ERROS DE EXECUÇÃO:
    - Divisão por zero
    - Acesso a índice de array inválido
    - Acesso a atributo inexistente
    - Chamada de método inexistente
    - Valor null/None em operação
    - Deadlock em canais
    - Timeout em comunicação
```

## Estratégias de Tratamento

### Lexer - Erros Léxicos

```pseudocode
CLASSE Lexer
    ATRIBUTOS:
        source: String
        position: Inteiro
        line: Inteiro
        column: Inteiro
        errors: Lista[String]
    
    FUNÇÃO report_error(message: String)
        """
        Reporta erro léxico com informações de localização
        """
        error_msg = FORMATAR(
            "Erro Léxico [Linha %d, Coluna %d]: %s",
            this.line,
            this.column,
            message
        )
        this.errors.ADICIONAR(error_msg)
        IMPRIMIR error_msg
    FIM FUNÇÃO
    
    FUNÇÃO tokenize() -> Lista[Token]
        """
        Tokeniza o código fonte, coletando erros
        """
        tokens = []
        
        ENQUANTO NOT this.is_at_end() FAÇA
            TENTAR
                token = this.scan_token()
                SE token NÃO É Null ENTÃO
                    tokens.ADICIONAR(token)
                FIM SE
            CAPTURAR Exception COMO e
                this.report_error(e.mensagem)
                # Recuperação: pula caractere inválido
                this.advance()
            FIM TENTAR
        FIM ENQUANTO
        
        # Verifica se houveram erros
        SE this.errors NÃO ESTÁ VAZIO ENTÃO
            IMPRIMIR "\n❌ Erros Léxicos Encontrados:"
            PARA CADA error EM this.errors FAÇA
                IMPRIMIR "  • " + error
            FIM PARA
            LANÇAR Exception("Análise léxica falhou")
        FIM SE
        
        RETORNAR tokens
    FIM FUNÇÃO
    
    FUNÇÃO scan_token() -> Token
        """
        Escaneia próximo token, detectando erros
        """
        char = this.advance()
        
        SE char É LETRA ENTÃO
            RETORNAR this.scan_identifier()
        
        SENÃO SE char É DIGITO ENTÃO
            RETORNAR this.scan_number()
        
        SENÃO SE char == '"' ENTÃO
            RETORNAR this.scan_string()
        
        SENÃO SE char EM OPERADORES ENTÃO
            RETORNAR this.scan_operator()
        
        SENÃO
            this.report_error("Caractere inválido: '" + char + "'")
            RETORNAR Null
        FIM SE
    FIM FUNÇÃO
    
    FUNÇÃO scan_string() -> Token
        """
        Escaneia string literal, detectando string não fechada
        """
        start = this.position - 1
        
        ENQUANTO NOT this.is_at_end() E this.peek() != '"' FAÇA
            SE this.peek() == '\n' ENTÃO
                this.line++
            FIM SE
            this.advance()
        FIM ENQUANTO
        
        # String não fechada
        SE this.is_at_end() ENTÃO
            this.report_error("String não fechada")
            RETORNAR Null
        FIM SE
        
        # Fecha string
        this.advance()  # Consome "
        
        value = this.source[start+1 : this.position-1]
        RETORNAR NOVO Token(TOKEN_STRING, value, this.line)
    FIM FUNÇÃO
FIM CLASSE
```

### Parser - Erros Sintáticos

```pseudocode
CLASSE Parser
    ATRIBUTOS:
        tokens: Lista[Token]
        current: Inteiro
        errors: Lista[String]
    
    FUNÇÃO report_error(message: String, token: Token)
        """
        Reporta erro sintático com contexto
        """
        error_msg = FORMATAR(
            "Erro Sintático [Linha %d]: %s\n  Token: %s '%s'",
            token.line,
            message,
            token.type,
            token.lexeme
        )
        this.errors.ADICIONAR(error_msg)
        IMPRIMIR error_msg
    FIM FUNÇÃO
    
    FUNÇÃO parse() -> AST
        """
        Faz parsing do código, coletando erros
        """
        ast = Null
        
        TENTAR
            ast = this.programa_minipar()
        CAPTURAR ParseError COMO e
            this.report_error(e.mensagem, this.current_token())
            # Modo pânico: sincroniza até próximo statement
            this.synchronize()
        FIM TENTAR
        
        # Verifica se houveram erros
        SE this.errors NÃO ESTÁ VAZIO ENTÃO
            IMPRIMIR "\n❌ Erros Sintáticos Encontrados:"
            PARA CADA error EM this.errors FAÇA
                IMPRIMIR "  • " + error
            FIM PARA
            LANÇAR Exception("Análise sintática falhou")
        FIM SE
        
        RETORNAR ast
    FIM FUNÇÃO
    
    FUNÇÃO expect(token_type: TokenType, message: String) -> Token
        """
        Consome token esperado ou reporta erro
        """
        SE this.check(token_type) ENTÃO
            RETORNAR this.advance()
        FIM SE
        
        this.report_error(message, this.peek())
        LANÇAR ParseError(message)
    FIM FUNÇÃO
    
    FUNÇÃO synchronize()
        """
        Modo pânico: sincroniza até próximo statement válido
        Recupera de erros para continuar parsing
        """
        this.advance()
        
        ENQUANTO NOT this.is_at_end() FAÇA
            # Encontrou fim de statement
            SE this.previous().type == SEMICOLON ENTÃO
                RETORNAR
            FIM SE
            
            # Próximo token é início de statement
            SE this.peek().type EM [CLASS, VOID, INT, FLOAT, IF, WHILE, FOR, RETURN] ENTÃO
                RETORNAR
            FIM SE
            
            this.advance()
        FIM ENQUANTO
    FIM FUNÇÃO
    
    FUNÇÃO parse_function() -> FunctionNode
        """
        Exemplo de parsing com tratamento de erro
        """
        TENTAR
            return_type = this.expect(IDENTIFIER, "Esperado tipo de retorno")
            name = this.expect(IDENTIFIER, "Esperado nome da função")
            this.expect(LPAREN, "Esperado '(' após nome da função")
            
            parameters = []
            SE NOT this.check(RPAREN) ENTÃO
                parameters = this.parse_parameters()
            FIM SE
            
            this.expect(RPAREN, "Esperado ')' após parâmetros")
            this.expect(LBRACE, "Esperado '{' para iniciar corpo da função")
            
            body = this.parse_block()
            
            this.expect(RBRACE, "Esperado '}' para fechar corpo da função")
            
            RETORNAR NOVO FunctionNode(return_type, name, parameters, body)
            
        CAPTURAR ParseError COMO e
            # Erro já foi reportado
            this.synchronize()
            RETORNAR Null
        FIM TENTAR
    FIM FUNÇÃO
FIM CLASSE
```

### Semantic Analyzer - Erros Semânticos

```pseudocode
CLASSE SemanticAnalyzer
    ATRIBUTOS:
        symbol_table: SymbolTable
        errors: Lista[String]
    
    FUNÇÃO report_error(message: String)
        """
        Reporta erro semântico
        """
        this.errors.ADICIONAR(message)
        IMPRIMIR "Erro Semântico: " + message
    FIM FUNÇÃO
    
    FUNÇÃO analyze(ast: AST) -> Lista[String]
        """
        Analisa AST, coletando erros semânticos
        Não lança exceção - coleta todos os erros
        """
        this.errors = []
        
        TENTAR
            this.collect_global_declarations(ast)
            this.analyze_node(ast)
        CAPTURAR Exception COMO e
            this.report_error("Erro durante análise: " + e.mensagem)
        FIM TENTAR
        
        RETORNAR this.errors
    FIM FUNÇÃO
    
    FUNÇÃO analyze_variable_declaration(node: AST_Node)
        """
        Valida declaração de variável
        """
        type_name = node.type_name
        identifier = node.identifier
        
        # Tipo inválido
        SE NOT this.is_valid_type(type_name) ENTÃO
            this.report_error("Tipo '" + type_name + "' não é válido")
            RETORNAR
        FIM SE
        
        # Variável já declarada no escopo atual
        SE this.symbol_table_exists_current_scope(identifier) ENTÃO
            this.report_error(
                "Variável '" + identifier + "' já declarada neste escopo"
            )
            RETORNAR
        FIM SE
        
        # Registra variável
        this.symbol_table.define(identifier, type_name)
    FIM FUNÇÃO
    
    FUNÇÃO analyze_assignment(node: AST_Node)
        """
        Valida atribuição
        """
        identifier = node.identifier
        
        # Variável não declarada
        SE NOT this.symbol_table.exists(identifier) ENTÃO
            this.report_error(
                "Variável '" + identifier + "' não foi declarada"
            )
            RETORNAR
        FIM SE
        
        # TODO: Verificação de tipos
        # expected_type = this.symbol_table.lookup(identifier).type
        # actual_type = this.infer_type(node.expression)
        # SE expected_type != actual_type ENTÃO
        #     this.report_error("Incompatibilidade de tipos")
        # FIM SE
    FIM FUNÇÃO
FIM CLASSE
```

### Interpreter - Erros de Execução

```pseudocode
CLASSE Interpreter
    FUNÇÃO report_runtime_error(message: String, context: String)
        """
        Reporta erro de execução com contexto
        """
        error_msg = FORMATAR(
            "\n❌ Erro de Execução: %s\n   Contexto: %s",
            message,
            context
        )
        IMPRIMIR error_msg
        LANÇAR RuntimeError(error_msg)
    FIM FUNÇÃO
    
    FUNÇÃO execute_binary_operation(left, operator, right)
        """
        Executa operação binária com tratamento de erro
        """
        TENTAR
            SE operator == "+" ENTÃO
                RETORNAR left + right
            
            SENÃO SE operator == "-" ENTÃO
                RETORNAR left - right
            
            SENÃO SE operator == "*" ENTÃO
                RETORNAR left * right
            
            SENÃO SE operator == "/" ENTÃO
                SE right == 0 ENTÃO
                    this.report_runtime_error(
                        "Divisão por zero",
                        "Operação: " + left + " / " + right
                    )
                FIM SE
                RETORNAR left / right
            
            SENÃO
                this.report_runtime_error(
                    "Operador inválido: " + operator,
                    "Operandos: " + left + " e " + right
                )
            FIM SE
            
        CAPTURAR TypeError COMO e
            this.report_runtime_error(
                "Incompatibilidade de tipos na operação",
                "Operação: " + left + " " + operator + " " + right
            )
        FIM TENTAR
    FIM FUNÇÃO
    
    FUNÇÃO execute_array_access(array, index)
        """
        Acessa array com verificação de bounds
        """
        SE array É Null ENTÃO
            this.report_runtime_error(
                "Tentativa de acessar array null",
                "Índice: " + index
            )
        FIM SE
        
        SE index < 0 OU index >= TAMANHO(array) ENTÃO
            this.report_runtime_error(
                "Índice de array fora dos limites",
                "Índice: " + index + ", Tamanho: " + TAMANHO(array)
            )
        FIM SE
        
        RETORNAR array[index]
    FIM FUNÇÃO
    
    FUNÇÃO execute_method_call(object, method_name, arguments)
        """
        Chama método com verificação de existência
        """
        SE object É Null ENTÃO
            this.report_runtime_error(
                "Tentativa de chamar método em objeto null",
                "Método: " + method_name
            )
        FIM SE
        
        class_def = object.__class__
        SE NOT class_def.has_method(method_name) ENTÃO
            this.report_runtime_error(
                "Método '" + method_name + "' não existe",
                "Classe: " + class_def.name
            )
        FIM SE
        
        method = class_def.get_method(method_name)
        
        # Verifica número de argumentos
        SE TAMANHO(arguments) != TAMANHO(method.parameters) ENTÃO
            this.report_runtime_error(
                "Número incorreto de argumentos",
                "Esperado: " + TAMANHO(method.parameters) + 
                ", Recebido: " + TAMANHO(arguments)
            )
        FIM SE
        
        RETORNAR this.execute_method(method, arguments)
    FIM FUNÇÃO
FIM CLASSE
```

## Mensagens de Erro Formatadas

```pseudocode
CLASSE ErrorFormatter
    """
    Formata mensagens de erro de forma legível
    """
    
    FUNÇÃO format_error(type: String, message: String, 
                       line: Inteiro, column: Inteiro,
                       source_line: String) -> String
        """
        Formata erro com contexto do código fonte
        """
        
        output = []
        output.ADICIONAR("\n" + "="*60)
        output.ADICIONAR("❌ ERRO " + type)
        output.ADICIONAR("="*60)
        output.ADICIONAR("")
        output.ADICIONAR("Linha " + line + ", Coluna " + column)
        output.ADICIONAR("")
        output.ADICIONAR("Código:")
        output.ADICIONAR("  " + source_line)
        output.ADICIONAR("  " + " "*column + "^")
        output.ADICIONAR("")
        output.ADICIONAR("Mensagem: " + message)
        output.ADICIONAR("="*60)
        
        RETORNAR JUNTAR(output, "\n")
    FIM FUNÇÃO
FIM CLASSE
```

## Fluxo Completo de Tratamento

```pseudocode
FUNÇÃO main(source_file: String)
    """
    Pipeline completo com tratamento de erros em cada etapa
    """
    
    TENTAR
        # 1. Ler código fonte
        codigo = LER_ARQUIVO(source_file)
        
        # 2. Análise Léxica
        IMPRIMIR "Análise Léxica..."
        lexer = NOVO Lexer(codigo)
        tokens = lexer.tokenize()
        IMPRIMIR "✅ Análise Léxica concluída"
        
        # 3. Análise Sintática
        IMPRIMIR "Análise Sintática..."
        parser = NOVO Parser(tokens)
        ast = parser.parse()
        IMPRIMIR "✅ Análise Sintática concluída"
        
        # 4. Análise Semântica
        IMPRIMIR "Análise Semântica..."
        semantic = NOVO SemanticAnalyzer()
        errors = semantic.analyze(ast)
        
        SE errors NÃO ESTÁ VAZIO ENTÃO
            IMPRIMIR "❌ Erros Semânticos Encontrados:"
            PARA CADA error EM errors FAÇA
                IMPRIMIR "  • " + error
            FIM PARA
            SAIR(1)
        FIM SE
        IMPRIMIR "✅ Análise Semântica concluída"
        
        # 5. Execução
        IMPRIMIR "Executando..."
        interpreter = NOVO Interpreter()
        interpreter.interpret(ast)
        IMPRIMIR "✅ Execução concluída"
        
    CAPTURAR FileNotFoundError COMO e
        IMPRIMIR "❌ Erro: Arquivo não encontrado: " + source_file
        SAIR(1)
    
    CAPTURAR LexerError COMO e
        IMPRIMIR "❌ Erro Léxico: " + e.mensagem
        SAIR(1)
    
    CAPTURAR ParserError COMO e
        IMPRIMIR "❌ Erro Sintático: " + e.mensagem
        SAIR(1)
    
    CAPTURAR RuntimeError COMO e
        IMPRIMIR "❌ Erro de Execução: " + e.mensagem
        IMPRIMIR "\nStack Trace:"
        IMPRIMIR e.stack_trace
        SAIR(1)
    
    CAPTURAR Exception COMO e
        IMPRIMIR "❌ Erro Inesperado: " + e.mensagem
        IMPRIMIR e.stack_trace
        SAIR(1)
    FIM TENTAR
FIM FUNÇÃO
```

## Resumo das Estratégias

### 1. **Detecção Precoce**
- Erros são detectados o mais cedo possível
- Lexer → Parser → Semantic → Runtime

### 2. **Recuperação de Erros**
- Lexer: pula caractere inválido
- Parser: modo pânico até próximo statement
- Semantic: coleta todos os erros (não para no primeiro)

### 3. **Mensagens Claras**
- Localização exata (linha, coluna)
- Contexto do erro
- Sugestão de correção (quando possível)

### 4. **Falha Rápida**
- Erros léxicos/sintáticos param execução
- Erros semânticos são coletados mas impedem execução
- Erros de runtime param execução imediatamente

### 5. **Thread-Safety**
- Erros em threads PAR são isolados
- Cada thread reporta seus próprios erros
- Sistema de logging thread-safe
