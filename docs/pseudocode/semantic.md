# Pseudocódigo do Analisador Semântico (SemanticAnalyzer)

## Visão Geral
O Analisador Semântico é responsável por validar a correção semântica do programa MiniPar após a análise sintática. Ele verifica tipos, escopos, declarações duplicadas e outras regras semânticas.

## Estrutura de Dados

```pseudocode
CLASSE SemanticAnalyzer
    ATRIBUTOS:
        symbol_table: SymbolTable        # Tabela de símbolos
        errors: Lista[String]            # Lista de erros encontrados
        current_function: String ou Null # Função atualmente sendo analisada
        return_type_stack: Lista[String] # Pilha de tipos de retorno
        functions: Dicionário            # Funções declaradas {nome: nó}
        classes: Dicionário              # Classes declaradas {nome: nó}
FIM CLASSE
```

## Algoritmo Principal

```pseudocode
FUNÇÃO analyze(ast: AST_Node) -> Lista[String]
    """
    Analisa a árvore AST e retorna lista de erros semânticos
    Realiza duas passadas:
    1. Coleta declarações globais (funções, classes, variáveis)
    2. Análise semântica completa
    """
    
    # Inicialização
    errors = []
    functions = {}
    classes = {}
    
    TENTAR
        # Primeira passada: coletar declarações globais
        collect_global_declarations(ast)
        
        # Segunda passada: análise semântica completa
        SE ast TEM ATRIBUTO children ENTÃO
            analyze_children(ast.children)
        SENÃO SE ast TEM ATRIBUTO declarations ENTÃO
            analyze_children(ast.declarations)
        SENÃO
            analyze_node(ast)
        FIM SE
        
    CAPTURAR Exception COMO e
        errors.ADICIONAR("Erro durante análise: " + e.mensagem)
    FIM TENTAR
    
    RETORNAR errors
FIM FUNÇÃO
```

## Coleta de Declarações Globais

```pseudocode
FUNÇÃO collect_global_declarations(ast: AST_Node)
    """
    Primeira passada: coleta funções, classes e variáveis globais
    Isso permite que funções/classes sejam chamadas antes de sua definição
    """
    
    children = []
    SE ast TEM ATRIBUTO children ENTÃO
        children = ast.children
    SENÃO SE ast TEM ATRIBUTO declarations ENTÃO
        children = ast.declarations
    FIM SE
    
    PARA CADA child EM children FAÇA
        # Declarações de variáveis globais
        SE is_variable_declaration(child) ENTÃO
            type_name = child.type_name OU child.type
            identifier = child.identifier
            
            SE type_name E identifier EXISTEM ENTÃO
                SE NOT is_valid_type(type_name) ENTÃO
                    errors.ADICIONAR("Tipo '" + type_name + "' não é válido")
                    CONTINUAR
                FIM SE
                
                SE symbol_table_exists_current_scope(identifier) ENTÃO
                    errors.ADICIONAR("Variável '" + identifier + "' já declarada")
                SENÃO
                    symbol_table.define(identifier, type_name)
                    IMPRIMIR "✓ Variável global declarada: " + identifier + " : " + type_name
                FIM SE
            FIM SE
        
        # Declarações de funções
        SENÃO SE is_function_declaration(child) ENTÃO
            func_name = child.name OU child.identifier
            SE func_name EXISTE ENTÃO
                functions[func_name] = child
                IMPRIMIR "✓ Função declarada: " + func_name
            FIM SE
        
        # Declarações de classes
        SENÃO SE is_class_declaration(child) ENTÃO
            class_name = child.name OU child.identifier
            SE class_name EXISTE ENTÃO
                classes[class_name] = child
                IMPRIMIR "✓ Classe declarada: " + class_name
            FIM SE
        FIM SE
    FIM PARA
FIM FUNÇÃO
```

## Análise de Nós

```pseudocode
FUNÇÃO analyze_node(node: AST_Node)
    """
    Analisa um nó individual da AST
    Delega para funções específicas baseado no tipo do nó
    """
    
    SE is_variable_declaration(node) ENTÃO
        analyze_variable_declaration(node)
    
    SENÃO SE is_function_declaration(node) ENTÃO
        analyze_function_declaration(node)
    
    SENÃO SE is_class_declaration(node) ENTÃO
        analyze_class_declaration(node)
    
    SENÃO SE is_assignment(node) ENTÃO
        analyze_assignment(node)
    
    SENÃO SE is_expression_statement(node) ENTÃO
        analyze_expression_statement(node)
    
    SENÃO SE is_channel_operation(node) ENTÃO
        analyze_channel_operation(node)
    
    SENÃO SE is_if_statement(node) ENTÃO
        analyze_if_statement(node)
    
    SENÃO SE is_while_statement(node) ENTÃO
        analyze_while_statement(node)
    
    SENÃO SE is_for_statement(node) ENTÃO
        analyze_for_statement(node)
    
    SENÃO SE is_block_statement(node) ENTÃO
        analyze_block_statement(node)
    
    SENÃO SE is_function_call(node) ENTÃO
        analyze_function_call(node)
    
    SENÃO SE node TEM ATRIBUTO children ENTÃO
        analyze_children(node.children)
    
    SENÃO SE node TEM ATRIBUTO declarations ENTÃO
        analyze_children(node.declarations)
    
    SENÃO SE node TEM ATRIBUTO statements ENTÃO
        analyze_children(node.statements)
    FIM SE
FIM FUNÇÃO
```

## Análise de Declaração de Variável

```pseudocode
FUNÇÃO analyze_variable_declaration(node: AST_Node)
    """
    Valida declaração de variável:
    - Tipo válido
    - Não redeclarada no mesmo escopo
    - Registra na tabela de símbolos
    """
    
    type_name = node.type_name OU node.type
    identifier = node.identifier
    
    SE NOT type_name OU NOT identifier ENTÃO
        errors.ADICIONAR("Declaração de variável incompleta")
        RETORNAR
    FIM SE
    
    # Verifica tipo válido
    SE NOT is_valid_type(type_name) ENTÃO
        errors.ADICIONAR("Tipo '" + type_name + "' não é válido")
        RETORNAR
    FIM SE
    
    # Verifica redeclaração no escopo atual
    existing = symbol_table.lookup(identifier)
    SE existing E symbol_table_exists_current_scope(identifier) ENTÃO
        SE symbol_table.current_scope.scope_level > 0 ENTÃO
            errors.ADICIONAR("Variável '" + identifier + "' já declarada neste escopo")
        FIM SE
    SENÃO
        SE NOT existing ENTÃO
            symbol_table.define(identifier, type_name)
            IMPRIMIR "  ✓ Variável declarada: " + identifier + " : " + type_name
        FIM SE
    FIM SE
FIM FUNÇÃO
```

## Análise de Declaração de Função

```pseudocode
FUNÇÃO analyze_function_declaration(node: AST_Node)
    """
    Valida declaração de função:
    - Tipo de retorno válido
    - Parâmetros válidos
    - Corpo da função
    """
    
    func_name = node.name OU node.identifier
    return_type = node.return_type
    parameters = node.parameters OU []
    body = node.body OU node.children OU []
    
    SE NOT func_name ENTÃO
        errors.ADICIONAR("Função sem nome")
        RETORNAR
    FIM SE
    
    IMPRIMIR "Analisando função: " + func_name
    
    # Verifica tipo de retorno
    SE return_type E NOT is_valid_type(return_type) ENTÃO
        errors.ADICIONAR("Tipo de retorno '" + return_type + "' inválido")
    FIM SE
    
    # Contexto da função
    current_function = func_name
    SE return_type ENTÃO
        return_type_stack.ADICIONAR(return_type)
    SENÃO
        return_type_stack.ADICIONAR("VOID")
    FIM SE
    
    # Entra em novo escopo
    symbol_table.enter_scope()
    
    # Registra parâmetros
    PARA CADA param EM parameters FAÇA
        param_type = param.type_name OU param.type
        param_name = param.identifier OU param.name
        
        SE param_type E param_name ENTÃO
            SE is_valid_type(param_type) ENTÃO
                symbol_table.define(param_name, param_type)
                IMPRIMIR "  ✓ Parâmetro: " + param_name + " : " + param_type
            SENÃO
                errors.ADICIONAR("Tipo de parâmetro inválido: " + param_type)
            FIM SE
        FIM SE
    FIM PARA
    
    # Analisa corpo da função
    SE body É Lista ENTÃO
        analyze_children(body)
    SENÃO
        analyze_node(body)
    FIM SE
    
    # Sai do escopo
    symbol_table.exit_scope()
    return_type_stack.REMOVER_ULTIMO()
    current_function = Null
FIM FUNÇÃO
```

## Análise de Declaração de Classe

```pseudocode
FUNÇÃO analyze_class_declaration(node: AST_Node)
    """
    Valida declaração de classe:
    - Atributos válidos
    - Métodos válidos
    - Herança (se houver)
    """
    
    class_name = node.name
    attributes = node.attributes OU []
    methods = node.methods OU []
    parent = node.parent OU Null
    
    SE NOT class_name ENTÃO
        errors.ADICIONAR("Classe sem nome")
        RETORNAR
    FIM SE
    
    IMPRIMIR "Analisando classe: " + class_name
    
    # Verifica herança
    SE parent E NOT symbol_table.exists(parent) ENTÃO
        errors.ADICIONAR("Classe pai '" + parent + "' não encontrada")
    FIM SE
    
    # Entra em novo escopo para a classe
    symbol_table.enter_scope()
    
    # Analisa atributos
    PARA CADA attr EM attributes FAÇA
        attr_type = attr.type_name OU attr.type
        attr_name = attr.identifier
        
        SE attr_type E attr_name ENTÃO
            SE is_valid_type(attr_type) ENTÃO
                symbol_table.define(attr_name, attr_type)
                IMPRIMIR "  ✓ Atributo: " + attr_name + " : " + attr_type
            SENÃO
                errors.ADICIONAR("Tipo de atributo inválido: " + attr_type)
            FIM SE
        FIM SE
    FIM PARA
    
    # Analisa métodos
    PARA CADA method EM methods FAÇA
        analyze_function_declaration(method)
    FIM PARA
    
    # Sai do escopo
    symbol_table.exit_scope()
FIM FUNÇÃO
```

## Análise de Atribuição

```pseudocode
FUNÇÃO analyze_assignment(node: AST_Node)
    """
    Valida atribuição:
    - Variável declarada
    - Compatibilidade de tipos
    """
    
    identifier = node.identifier
    expression = node.expression
    
    # Verifica se variável existe
    SE NOT symbol_table.exists(identifier) ENTÃO
        errors.ADICIONAR("Variável '" + identifier + "' não declarada")
        RETORNAR
    FIM SE
    
    # Analisa expressão
    SE expression EXISTE ENTÃO
        analyze_expression(expression)
    FIM SE
    
    # TODO: Verificação de tipos (se implementado)
FIM FUNÇÃO
```

## Análise de Estruturas de Controle

```pseudocode
FUNÇÃO analyze_if_statement(node: AST_Node)
    """
    Analisa estrutura if/else
    """
    
    condition = node.condition
    then_body = node.then_body
    else_body = node.else_body OU Null
    
    # Analisa condição
    analyze_expression(condition)
    
    # Analisa bloco then
    symbol_table.enter_scope()
    analyze_children(then_body)
    symbol_table.exit_scope()
    
    # Analisa bloco else (se houver)
    SE else_body ENTÃO
        symbol_table.enter_scope()
        analyze_children(else_body)
        symbol_table.exit_scope()
    FIM SE
FIM FUNÇÃO

FUNÇÃO analyze_while_statement(node: AST_Node)
    """
    Analisa laço while
    """
    
    condition = node.condition
    body = node.body
    
    # Analisa condição
    analyze_expression(condition)
    
    # Analisa corpo
    symbol_table.enter_scope()
    analyze_children(body)
    symbol_table.exit_scope()
FIM FUNÇÃO

FUNÇÃO analyze_for_statement(node: AST_Node)
    """
    Analisa laço for
    """
    
    init = node.init
    condition = node.condition
    increment = node.increment
    body = node.body
    
    symbol_table.enter_scope()
    
    # Analisa inicialização
    analyze_node(init)
    
    # Analisa condição
    analyze_expression(condition)
    
    # Analisa incremento
    analyze_node(increment)
    
    # Analisa corpo
    analyze_children(body)
    
    symbol_table.exit_scope()
FIM FUNÇÃO
```

## Análise de Blocos SEQ/PAR

```pseudocode
FUNÇÃO analyze_block_statement(node: AST_Node)
    """
    Analisa blocos SEQ e PAR
    Blocos PAR requerem verificações adicionais de concorrência
    """
    
    block_type = node.block_type  # "SEQ" ou "PAR"
    statements = node.statements
    
    IMPRIMIR "  Analisando bloco " + block_type
    
    SE block_type == "PAR" ENTÃO
        # Verifica uso seguro de variáveis compartilhadas
        # TODO: Implementar análise de condições de corrida
        PASSAR
    FIM SE
    
    # Analisa statements do bloco
    analyze_children(statements)
FIM FUNÇÃO
```

## Funções Auxiliares

```pseudocode
FUNÇÃO is_valid_type(type_name: String) -> Boolean
    """
    Verifica se um tipo é válido
    """
    
    tipos_basicos = ["INT", "FLOAT", "STRING", "BOOL", "VOID", "C_CHANNEL"]
    
    # Tipo básico
    SE type_name EM tipos_basicos ENTÃO
        RETORNAR Verdadeiro
    FIM SE
    
    # Classe definida
    SE type_name EM classes ENTÃO
        RETORNAR Verdadeiro
    FIM SE
    
    # Verifica na symbol table
    SE symbol_table.exists(type_name) ENTÃO
        symbol = symbol_table.lookup(type_name)
        SE symbol.is_class ENTÃO
            RETORNAR Verdadeiro
        FIM SE
    FIM SE
    
    RETORNAR Falso
FIM FUNÇÃO

FUNÇÃO is_variable_declaration(node: AST_Node) -> Boolean
    """
    Verifica se nó é declaração de variável
    """
    RETORNAR (node TEM type_name OU node TEM type) E 
             (node TEM identifier) E 
             (node NÃO TEM return_type)
FIM FUNÇÃO

FUNÇÃO is_function_declaration(node: AST_Node) -> Boolean
    """
    Verifica se nó é declaração de função
    """
    RETORNAR (node TEM return_type) E
             (node TEM name OU node TEM identifier) E
             (node TEM body OU node TEM children)
FIM FUNÇÃO

FUNÇÃO is_class_declaration(node: AST_Node) -> Boolean
    """
    Verifica se nó é declaração de classe
    """
    RETORNAR (node TEM name) E 
             (node TEM attributes) E 
             (node TEM methods)
FIM FUNÇÃO

FUNÇÃO symbol_table_exists_current_scope(identifier: String) -> Boolean
    """
    Verifica se símbolo existe no escopo atual (não em escopos pai)
    """
    RETORNAR symbol_table.current_scope.exists(identifier)
FIM FUNÇÃO
```

## Fluxo Completo

```pseudocode
PROCEDIMENTO análise_semântica_completa(ast: AST_Node)
    """
    Fluxo completo de análise semântica
    """
    
    # 1. Criar analisador
    analyzer = NOVO SemanticAnalyzer()
    
    # 2. Executar análise
    errors = analyzer.analyze(ast)
    
    # 3. Verificar erros
    SE errors NÃO ESTÁ VAZIO ENTÃO
        IMPRIMIR "❌ ERROS SEMÂNTICOS ENCONTRADOS:"
        PARA CADA error EM errors FAÇA
            IMPRIMIR "  - " + error
        FIM PARA
        IMPRIMIR "Total: " + TAMANHO(errors) + " erro(s)"
        ABORTAR_EXECUÇÃO()
    SENÃO
        IMPRIMIR "✅ Análise semântica concluída sem erros"
    FIM SE
    
    # 4. Retornar tabela de símbolos preenchida
    RETORNAR analyzer.symbol_table
FIM PROCEDIMENTO
```

## Notas de Implementação

### Checagens Implementadas
- ✅ Declaração de variáveis duplicadas
- ✅ Tipos válidos
- ✅ Escopo de variáveis
- ✅ Declaração de funções e classes
- ✅ Parâmetros de funções

### Checagens Futuras (TODO)
- ⏳ Verificação de tipos em atribuições
- ⏳ Verificação de tipos em expressões
- ⏳ Verificação de return em funções não-void
- ⏳ Análise de condições de corrida em blocos PAR
- ⏳ Verificação de acesso a atributos de classe
- ⏳ Verificação de chamadas de método

### Integração com Interpretador
O analisador semântico é executado após o parser e antes do interpretador:
```
Código Fonte → Lexer → Parser → SemanticAnalyzer → Interpreter
```

Atualmente o SemanticAnalyzer é executado de forma informativa, mas pode ser configurado para bloquear a execução em caso de erros.
