# Pseudocódigo do Interpretador (Interpreter)

## Visão Geral
O Interpretador executa a AST (Abstract Syntax Tree) gerada pelo Parser, implementando todas as funcionalidades de runtime do MiniPar, incluindo:
- Orientação a Objetos (classes, herança, instanciação)
- Concorrência com blocos PAR (threads)
- Comunicação entre threads via canais (Channels)
- Arrays 1D e 2D
- Funções nativas de string
- Tabela de símbolos thread-safe

## Estruturas de Dados

### Classe ReturnException
```pseudocode
CLASSE ReturnException HERDA DE Exception
    """
    Exceção especial usada para implementar RETURN em funções
    Permite sair de uma função com um valor de retorno
    """
    
    ATRIBUTOS:
        value: Qualquer  # Valor a ser retornado
    
    CONSTRUTOR __init__(value):
        this.value = value
    FIM CONSTRUTOR
FIM CLASSE
```

### Classe ObjectInstance
```pseudocode
CLASSE ObjectInstance
    """
    Representa uma instância de objeto em runtime
    Armazena atributos e referências aos métodos da classe
    """
    
    ATRIBUTOS:
        class_name: String            # Nome da classe
        class_def: ClassNode          # Definição da classe (AST)
        parent_classes: Dicionário    # Classes pai (para herança)
        attributes: Dicionário        # Valores dos atributos {nome: valor}
    
    CONSTRUTOR __init__(class_name, class_def, parent_classes=None):
        this.class_name = class_name
        this.class_def = class_def
        this.parent_classes = parent_classes OU {}
        this.attributes = {}
        
        # Inicializa atributos com valores padrão
        PARA CADA attr EM class_def.attributes FAÇA
            SE attr É Array 2D ENTÃO
                dim1 = attr.array_dimensions[0]
                dim2 = attr.array_dimensions[1]
                this.attributes[attr.name] = CRIAR_ARRAY_2D(dim1, dim2, attr.type_name)
            
            SENÃO SE attr É Array 1D ENTÃO
                size = attr.array_size
                this.attributes[attr.name] = CRIAR_ARRAY_1D(size, attr.type_name)
            
            SENÃO
                this.attributes[attr.name] = None
            FIM SE
        FIM PARA
    FIM CONSTRUTOR
    
    FUNÇÃO get_attribute(name: String) -> Qualquer
        """
        Obtém valor de um atributo (busca na hierarquia de herança)
        """
        SE name EM this.attributes ENTÃO
            RETORNAR this.attributes[name]
        FIM SE
        
        # Busca em classes pai
        SE this.class_def.parent E this.class_def.parent EM this.parent_classes ENTÃO
            parent_def = this.parent_classes[this.class_def.parent]
            PARA CADA attr EM parent_def.attributes FAÇA
                SE attr.name == name ENTÃO
                    RETORNAR this.attributes.get(name)
                FIM SE
            FIM PARA
        FIM SE
        
        RETORNAR None
    FIM FUNÇÃO
    
    FUNÇÃO set_attribute(name: String, value: Qualquer)
        """
        Define valor de um atributo
        """
        this.attributes[name] = value
    FIM FUNÇÃO
    
    FUNÇÃO get_method(name: String) -> MethodNode ou None
        """
        Obtém definição de um método (busca na hierarquia de herança)
        """
        # Busca na classe atual
        PARA CADA method EM this.class_def.methods FAÇA
            SE method.name == name ENTÃO
                RETORNAR method
            FIM SE
        FIM PARA
        
        # Busca em classes pai
        SE this.class_def.parent E this.class_def.parent EM this.parent_classes ENTÃO
            parent_def = this.parent_classes[this.class_def.parent]
            PARA CADA method EM parent_def.methods FAÇA
                SE method.name == name ENTÃO
                    RETORNAR method
                FIM SE
            FIM PARA
        FIM SE
        
        RETORNAR None
    FIM FUNÇÃO
FIM CLASSE
```

### Classe Interpreter (Principal)
```pseudocode
CLASSE Interpreter
    """
    Interpretador principal que executa a AST
    Gerencia escopos, threads, classes e execução
    """
    
    ATRIBUTOS:
        symbol_table: SymbolTable         # Tabela de símbolos thread-safe
        global_scope: Dicionário          # Escopo global
        local_storage: ThreadLocal        # Armazenamento local por thread
        classes: Dicionário               # Classes definidas {nome: ClassNode}
        functions: Dicionário             # Funções definidas {nome: FunctionNode}
        thread_manager: ThreadManager     # Gerenciador de threads PAR
        return_value: Qualquer           # Valor de retorno atual
        print_lock: Threading.Lock        # Lock para print thread-safe
    
    CONSTRUTOR __init__():
        this.symbol_table = NOVO SymbolTable()
        this.global_scope = {}
        this.local_storage = NOVO ThreadLocal()
        this.classes = {}
        this.functions = {}
        this.thread_manager = NOVO ThreadManager()
        this.return_value = None
        this.print_lock = NOVO Threading.Lock()
    FIM CONSTRUTOR
    
    PROPRIEDADE local_scope:
        OBTER:
            SE NOT this.local_storage TEM 'scope' ENTÃO
                this.local_storage.scope = {}
            FIM SE
            RETORNAR this.local_storage.scope
        
        DEFINIR(value):
            this.local_storage.scope = value
    FIM PROPRIEDADE
FIM CLASSE
```

## Método Principal de Interpretação

```pseudocode
FUNÇÃO interpret(ast: AST_Node)
    """
    Ponto de entrada principal para interpretar um programa
    """
    
    SE ast É ProgramNode ENTÃO
        # Fase 1: Coletar definições (classes, funções)
        this.collect_definitions(ast)
        
        # Fase 2: Executar programa
        this.execute_program(ast)
    FIM SE
FIM FUNÇÃO
```

## Coleta de Definições

```pseudocode
FUNÇÃO collect_definitions(program: ProgramNode)
    """
    Primeira passada: coleta todas as classes e funções
    Permite que sejam usadas antes de sua definição
    """
    
    PARA CADA node EM program.children FAÇA
        SE node É ClassNode ENTÃO
            # Armazena definição da classe
            this.classes[node.name] = node
            
            # Registra na symbol table
            this.symbol_table.define_class(
                node.name,
                [attr.name PARA CADA attr EM node.attributes],
                [method.name PARA CADA method EM node.methods],
                node.parent
            )
        
        SENÃO SE node É FunctionNode ENTÃO
            # Armazena definição da função
            this.functions[node.name] = node
            
            # Registra na symbol table
            this.symbol_table.define_function(
                node.name,
                node.return_type,
                node.parameters
            )
        
        SENÃO SE node É DeclarationNode ENTÃO
            # Executa declarações globais
            this.execute_declaration(node, this.global_scope)
        FIM SE
    FIM PARA
FIM FUNÇÃO
```

## Execução do Programa

```pseudocode
FUNÇÃO execute_program(program: ProgramNode)
    """
    Executa o corpo do programa (statements globais)
    """
    
    PARA CADA node EM program.children FAÇA
        SE node NÃO É ClassNode E node NÃO É FunctionNode ENTÃO
            this.execute_statement(node)
        FIM SE
    FIM PARA
FIM FUNÇÃO
```

## Execução de Blocos

```pseudocode
FUNÇÃO execute_block(node: BlockNode)
    """
    Executa bloco SEQ ou PAR
    """
    
    SE node.block_type == "SEQ" ENTÃO
        # Bloco sequencial: executa statements em ordem
        PARA CADA stmt EM node.statements FAÇA
            this.execute_statement(stmt)
        FIM PARA
    
    SENÃO SE node.block_type == "PAR" ENTÃO
        # Bloco paralelo: executa em threads separadas
        this.execute_parallel_block(node)
    FIM SE
FIM FUNÇÃO

FUNÇÃO execute_parallel_block(node: BlockNode)
    """
    Executa bloco PAR criando threads para cada statement
    """
    
    threads = []
    
    PARA CADA stmt EM node.statements FAÇA
        SE stmt É FunctionCallNode ENTÃO
            # Cria thread para executar função
            func_name = stmt.name
            func = this.functions[func_name]
            arguments = [this.evaluate_expression(arg) PARA CADA arg EM stmt.arguments]
            
            thread = NOVO Thread(
                target=this.execute_function_in_thread,
                args=(func, arguments)
            )
            thread.start()
            threads.ADICIONAR(thread)
            this.thread_manager.register_thread(thread)
        
        SENÃO
            # Cria thread para executar statement
            thread = NOVO Thread(
                target=this.execute_statement,
                args=(stmt,)
            )
            thread.start()
            threads.ADICIONAR(thread)
            this.thread_manager.register_thread(thread)
        FIM SE
    FIM PARA
    
    # Aguarda todas as threads terminarem (join)
    PARA CADA thread EM threads FAÇA
        thread.join()
    FIM PARA
FIM FUNÇÃO

FUNÇÃO execute_function_in_thread(func: FunctionNode, arguments: Lista)
    """
    Executa uma função em uma thread separada
    Cria escopo local para a thread
    """
    
    # Cria escopo local para esta thread
    this.local_scope = {}
    
    # Liga parâmetros aos argumentos
    PARA i = 0 ATÉ TAMANHO(func.parameters) - 1 FAÇA
        param = func.parameters[i]
        value = arguments[i]
        this.local_scope[param.name] = value
        this.symbol_table.define(param.name, param.type_name, value)
    FIM PARA
    
    # Executa corpo da função
    TENTAR
        PARA CADA stmt EM func.body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    CAPTURAR ReturnException COMO e
        # Função retornou um valor
        this.return_value = e.value
    FIM TENTAR
FIM FUNÇÃO
```

## Execução de Statements

```pseudocode
FUNÇÃO execute_statement(node: AST_Node)
    """
    Executa um statement individual
    Delega para funções específicas baseado no tipo do nó
    """
    
    SE node É DeclarationNode ENTÃO
        this.execute_declaration(node, this.local_scope)
    
    SENÃO SE node É AssignmentNode ENTÃO
        this.execute_assignment(node)
    
    SENÃO SE node É AttributeAssignmentNode ENTÃO
        this.execute_attribute_assignment(node)
    
    SENÃO SE node É ArrayAssignmentNode ENTÃO
        this.execute_array_assignment(node)
    
    SENÃO SE node É IfNode ENTÃO
        this.execute_if(node)
    
    SENÃO SE node É WhileNode ENTÃO
        this.execute_while(node)
    
    SENÃO SE node É ForNode ENTÃO
        this.execute_for(node)
    
    SENÃO SE node É PrintNode ENTÃO
        this.execute_print(node)
    
    SENÃO SE node É InputNode ENTÃO
        this.execute_input(node)
    
    SENÃO SE node É FunctionCallNode ENTÃO
        this.execute_function_call(node)
    
    SENÃO SE node É MethodCallNode ENTÃO
        this.execute_method_call(node)
    
    SENÃO SE node É SendNode ENTÃO
        this.execute_send(node)
    
    SENÃO SE node É ReceiveNode ENTÃO
        this.execute_receive(node)
    
    SENÃO SE node É ReturnNode ENTÃO
        this.execute_return(node)
    
    SENÃO SE node É InstantiationNode ENTÃO
        this.execute_instantiation(node)
    
    SENÃO SE node É BlockNode ENTÃO
        this.execute_block(node)
    FIM SE
FIM FUNÇÃO
```

## Declaração de Variáveis

```pseudocode
FUNÇÃO execute_declaration(node: DeclarationNode, scope: Dicionário)
    """
    Executa declaração de variável
    Suporta: variáveis simples, arrays 1D e 2D, inicialização
    """
    
    identifier = node.identifier
    type_name = node.type_name
    
    # Determina valor inicial
    SE node TEM initialization ENTÃO
        value = this.evaluate_expression(node.initialization)
    SENÃO
        SE node.is_2d_array ENTÃO
            # Array 2D
            dim1 = node.array_dimensions[0]
            dim2 = node.array_dimensions[1]
            value = CRIAR_ARRAY_2D(dim1, dim2, type_name)
        
        SENÃO SE node.is_array ENTÃO
            # Array 1D
            size = node.array_size
            value = CRIAR_ARRAY_1D(size, type_name)
        
        SENÃO
            # Valor padrão para tipo
            value = VALOR_PADRAO(type_name)
        FIM SE
    FIM SE
    
    # Armazena no escopo apropriado
    scope[identifier] = value
    this.symbol_table.define(identifier, type_name, value, node.is_array, node.array_size)
FIM FUNÇÃO
```

## Atribuições

```pseudocode
FUNÇÃO execute_assignment(node: AssignmentNode)
    """
    Executa atribuição simples: x = expr
    """
    
    identifier = node.identifier
    value = this.evaluate_expression(node.expression)
    
    # Busca variável em escopos (local → global)
    SE identifier EM this.local_scope ENTÃO
        this.local_scope[identifier] = value
    SENÃO SE identifier EM this.global_scope ENTÃO
        this.global_scope[identifier] = value
    SENÃO
        LANÇAR RuntimeError("Variável '" + identifier + "' não declarada")
    FIM SE
    
    this.symbol_table.update(identifier, value)
FIM FUNÇÃO

FUNÇÃO execute_attribute_assignment(node: AttributeAssignmentNode)
    """
    Executa atribuição de atributo: obj.attr = expr
    """
    
    object_name = node.object_name
    attribute_name = node.attribute_name
    value = this.evaluate_expression(node.expression)
    
    # Obtém objeto
    obj = this.get_variable(object_name)
    
    SE obj É None OU obj NÃO É ObjectInstance ENTÃO
        LANÇAR RuntimeError("'" + object_name + "' não é um objeto")
    FIM SE
    
    # Define atributo
    obj.set_attribute(attribute_name, value)
FIM FUNÇÃO

FUNÇÃO execute_array_assignment(node: ArrayAssignmentNode)
    """
    Executa atribuição em array: arr[i] = expr ou arr[i][j] = expr
    """
    
    identifier = node.identifier
    value = this.evaluate_expression(node.expression)
    
    # Obtém array
    array = this.get_variable(identifier)
    
    SE node.is_2d ENTÃO
        # Array 2D: arr[i][j] = value
        index1 = this.evaluate_expression(node.index)
        index2 = this.evaluate_expression(node.index2)
        array[index1][index2] = value
    SENÃO
        # Array 1D: arr[i] = value
        index = this.evaluate_expression(node.index)
        array[index] = value
    FIM SE
FIM FUNÇÃO
```

## Estruturas de Controle

```pseudocode
FUNÇÃO execute_if(node: IfNode)
    """
    Executa estrutura if/else
    """
    
    condition = this.evaluate_condition(node.condition)
    
    SE condition ENTÃO
        PARA CADA stmt EM node.then_body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    SENÃO SE node TEM else_body ENTÃO
        PARA CADA stmt EM node.else_body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    FIM SE
FIM FUNÇÃO

FUNÇÃO execute_while(node: WhileNode)
    """
    Executa laço while
    """
    
    ENQUANTO this.evaluate_condition(node.condition) FAÇA
        PARA CADA stmt EM node.body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    FIM ENQUANTO
FIM FUNÇÃO

FUNÇÃO execute_for(node: ForNode)
    """
    Executa laço for: for i = start; cond; i = update { body }
    """
    
    # Inicialização
    this.execute_statement(node.init)
    
    # Loop
    ENQUANTO this.evaluate_condition(node.condition) FAÇA
        # Executa corpo
        PARA CADA stmt EM node.body FAÇA
            this.execute_statement(stmt)
        FIM PARA
        
        # Incremento
        this.execute_statement(node.increment)
    FIM ENQUANTO
FIM FUNÇÃO
```

## I/O

```pseudocode
FUNÇÃO execute_print(node: PrintNode)
    """
    Executa comando print (thread-safe)
    Interpreta sequências de escape (\n, \t)
    """
    
    value = this.evaluate_expression(node.expression)
    output = CONVERTER_PARA_STRING(value)
    
    # Interpreta sequências de escape
    output = output.replace("\\n", "\n")
    output = output.replace("\\t", "\t")
    
    # Print thread-safe
    ADQUIRIR this.print_lock
    IMPRIMIR output
    LIBERAR this.print_lock
FIM FUNÇÃO

FUNÇÃO execute_input(node: InputNode)
    """
    Executa comando input()
    """
    
    SE node TEM prompt ENTÃO
        prompt_value = this.evaluate_expression(node.prompt)
        IMPRIMIR prompt_value
    FIM SE
    
    value = LER_LINHA_ENTRADA()
    
    SE node TEM identifier ENTÃO
        this.set_variable(node.identifier, value)
    FIM SE
    
    RETORNAR value
FIM FUNÇÃO
```

## Chamadas de Função e Método

```pseudocode
FUNÇÃO execute_function_call(node: FunctionCallNode) -> Qualquer
    """
    Executa chamada de função
    """
    
    func_name = node.name
    
    # Funções nativas de string
    SE func_name EM ["strlen", "substr", "charat", "indexof", "parseint"] ENTÃO
        arguments = [this.evaluate_expression(arg) PARA CADA arg EM node.arguments]
        RETORNAR this.execute_native_string_function(func_name, arguments)
    FIM SE
    
    # Função definida pelo usuário
    SE func_name NÃO EM this.functions ENTÃO
        LANÇAR RuntimeError("Função '" + func_name + "' não encontrada")
    FIM SE
    
    func = this.functions[func_name]
    
    # Avalia argumentos
    arguments = [this.evaluate_expression(arg) PARA CADA arg EM node.arguments]
    
    # Salva escopo atual
    old_scope = this.local_scope
    this.local_scope = {}
    
    # Entra em novo escopo na symbol table
    this.symbol_table.enter_scope()
    
    # Liga parâmetros aos argumentos
    PARA i = 0 ATÉ TAMANHO(func.parameters) - 1 FAÇA
        param = func.parameters[i]
        value = arguments[i]
        this.local_scope[param.name] = value
        this.symbol_table.define(param.name, param.type_name, value)
    FIM PARA
    
    # Executa corpo da função
    return_value = None
    TENTAR
        PARA CADA stmt EM func.body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    CAPTURAR ReturnException COMO e
        return_value = e.value
    FIM TENTAR
    
    # Restaura escopo
    this.symbol_table.exit_scope()
    this.local_scope = old_scope
    
    RETORNAR return_value
FIM FUNÇÃO

FUNÇÃO execute_method_call(node: MethodCallNode) -> Qualquer
    """
    Executa chamada de método: obj.method(args)
    """
    
    object_name = node.object_name
    method_name = node.method_name
    
    # Obtém objeto
    obj = this.get_variable(object_name)
    
    SE obj É None ENTÃO
        LANÇAR RuntimeError("Objeto '" + object_name + "' não encontrado")
    FIM SE
    
    SE obj NÃO É ObjectInstance ENTÃO
        LANÇAR RuntimeError("'" + object_name + "' não é um objeto")
    FIM SE
    
    # Obtém método
    method = obj.get_method(method_name)
    
    SE method É None ENTÃO
        LANÇAR RuntimeError("Método '" + method_name + "' não encontrado")
    FIM SE
    
    # Avalia argumentos
    arguments = [this.evaluate_expression(arg) PARA CADA arg EM node.arguments]
    
    # Salva escopo atual
    old_scope = this.local_scope
    this.local_scope = {}
    this.local_scope["this"] = obj  # Define 'this'
    
    # Entra em novo escopo
    this.symbol_table.enter_scope()
    
    # Liga parâmetros aos argumentos
    PARA i = 0 ATÉ TAMANHO(method.parameters) - 1 FAÇA
        param = method.parameters[i]
        value = arguments[i]
        this.local_scope[param.name] = value
        this.symbol_table.define(param.name, param.type_name, value)
    FIM PARA
    
    # Executa corpo do método
    return_value = None
    TENTAR
        PARA CADA stmt EM method.body FAÇA
            this.execute_statement(stmt)
        FIM PARA
    CAPTURAR ReturnException COMO e
        return_value = e.value
    FIM TENTAR
    
    # Restaura escopo
    this.symbol_table.exit_scope()
    this.local_scope = old_scope
    
    RETORNAR return_value
FIM FUNÇÃO
```

## Comunicação via Canais

```pseudocode
FUNÇÃO execute_send(node: SendNode)
    """
    Executa operação send em canal
    """
    
    channel_name = node.channel_name
    channel = this.get_variable(channel_name)
    
    SE channel É None OU channel NÃO É Channel ENTÃO
        LANÇAR RuntimeError("'" + channel_name + "' não é um canal")
    FIM SE
    
    # Avalia e envia valores
    values = [this.evaluate_expression(arg) PARA CADA arg EM node.arguments]
    channel.send(*values)
FIM FUNÇÃO

FUNÇÃO execute_receive(node: ReceiveNode)
    """
    Executa operação receive em canal
    Bloqueia até receber dados
    """
    
    channel_name = node.channel_name
    channel = this.get_variable(channel_name)
    
    SE channel É None OU channel NÃO É Channel ENTÃO
        LANÇAR RuntimeError("'" + channel_name + "' não é um canal")
    FIM SE
    
    # Recebe valores (bloqueia se necessário)
    values = channel.receive(TAMANHO(node.identifiers))
    
    # Atribui valores às variáveis
    PARA i = 0 ATÉ TAMANHO(node.identifiers) - 1 FAÇA
        identifier = node.identifiers[i]
        value = values[i]
        this.set_variable(identifier, value)
    FIM PARA
FIM FUNÇÃO
```

## Instanciação de Objetos

```pseudocode
FUNÇÃO execute_instantiation(node: InstantiationNode)
    """
    Executa instanciação de objeto: Tipo obj = new Tipo()
    """
    
    identifier = node.identifier
    class_name = node.class_name
    
    SE class_name NÃO EM this.classes ENTÃO
        LANÇAR RuntimeError("Classe '" + class_name + "' não encontrada")
    FIM SE
    
    class_def = this.classes[class_name]
    
    # Cria instância do objeto
    obj = NOVO ObjectInstance(class_name, class_def, this.classes)
    
    # Armazena no escopo
    this.set_variable(identifier, obj)
    this.symbol_table.define(identifier, class_name, obj)
FIM FUNÇÃO

FUNÇÃO execute_return(node: ReturnNode)
    """
    Executa return - lança exceção especial para sair da função
    """
    
    value = this.evaluate_expression(node.expression)
    LANÇAR ReturnException(value)
FIM FUNÇÃO
```

## Avaliação de Expressões

```pseudocode
FUNÇÃO evaluate_expression(node: AST_Node) -> Qualquer
    """
    Avalia uma expressão e retorna seu valor
    """
    
    SE node É NumberNode ENTÃO
        RETORNAR node.value
    
    SENÃO SE node É StringNode ENTÃO
        RETORNAR node.value
    
    SENÃO SE node É IdentifierNode ENTÃO
        RETORNAR this.get_variable(node.name)
    
    SENÃO SE node É BinaryOpNode ENTÃO
        left = this.evaluate_expression(node.left)
        right = this.evaluate_expression(node.right)
        RETORNAR this.apply_binary_operator(node.operator, left, right)
    
    SENÃO SE node É UnaryOpNode ENTÃO
        operand = this.evaluate_expression(node.operand)
        RETORNAR this.apply_unary_operator(node.operator, operand)
    
    SENÃO SE node É FunctionCallNode ENTÃO
        RETORNAR this.execute_function_call(node)
    
    SENÃO SE node É MethodCallNode ENTÃO
        RETORNAR this.execute_method_call(node)
    
    SENÃO SE node É AttributeAccessNode ENTÃO
        RETORNAR this.evaluate_attribute_access(node)
    
    SENÃO SE node É ArrayAccessNode ENTÃO
        RETORNAR this.evaluate_array_access(node)
    
    SENÃO SE node É InstantiationNode ENTÃO
        this.execute_instantiation(node)
        RETORNAR this.get_variable(node.identifier)
    
    SENÃO
        RETORNAR None
    FIM SE
FIM FUNÇÃO

FUNÇÃO evaluate_attribute_access(node: AttributeAccessNode) -> Qualquer
    """
    Avalia acesso a atributo: obj.attr ou this.attr
    """
    
    SE node.object_name == "this" ENTÃO
        obj = this.local_scope["this"]
    SENÃO
        obj = this.get_variable(node.object_name)
    FIM SE
    
    SE obj É None OU obj NÃO É ObjectInstance ENTÃO
        LANÇAR RuntimeError("'" + node.object_name + "' não é um objeto")
    FIM SE
    
    RETORNAR obj.get_attribute(node.attribute_name)
FIM FUNÇÃO

FUNÇÃO evaluate_array_access(node: ArrayAccessNode) -> Qualquer
    """
    Avalia acesso a array: arr[i] ou arr[i][j]
    """
    
    array = this.get_variable(node.identifier)
    
    SE node.is_2d ENTÃO
        # Array 2D
        index1 = this.evaluate_expression(node.index)
        index2 = this.evaluate_expression(node.index2)
        RETORNAR array[index1][index2]
    SENÃO
        # Array 1D
        index = this.evaluate_expression(node.index)
        RETORNAR array[index]
    FIM SE
FIM FUNÇÃO

FUNÇÃO evaluate_condition(node: AST_Node) -> Boolean
    """
    Avalia uma condição (para if, while)
    Suporta operadores relacionais e lógicos
    """
    
    SE node É BinaryOpNode ENTÃO
        left = this.evaluate_expression(node.left)
        right = this.evaluate_expression(node.right)
        
        operador = node.operator
        SE operador == "==" ENTÃO RETORNAR left == right
        SENÃO SE operador == "!=" ENTÃO RETORNAR left != right
        SENÃO SE operador == "<" ENTÃO RETORNAR left < right
        SENÃO SE operador == ">" ENTÃO RETORNAR left > right
        SENÃO SE operador == "<=" ENTÃO RETORNAR left <= right
        SENÃO SE operador == ">=" ENTÃO RETORNAR left >= right
        SENÃO SE operador == "&&" ENTÃO
            RETORNAR this.evaluate_condition(node.left) E 
                     this.evaluate_condition(node.right)
        SENÃO SE operador == "||" ENTÃO
            RETORNAR this.evaluate_condition(node.left) OU 
                     this.evaluate_condition(node.right)
        FIM SE
    FIM SE
    
    # Expressão não booleana - converte para booleano
    RETORNAR BOOLEANO(this.evaluate_expression(node))
FIM FUNÇÃO
```

## Funções Auxiliares

```pseudocode
FUNÇÃO get_variable(name: String) -> Qualquer
    """
    Obtém valor de variável (busca em escopos: local → global → symbol table)
    """
    
    SE name EM this.local_scope ENTÃO
        RETORNAR this.local_scope[name]
    FIM SE
    
    SE name EM this.global_scope ENTÃO
        RETORNAR this.global_scope[name]
    FIM SE
    
    value = this.symbol_table.get_value(name)
    SE value NÃO É None ENTÃO
        RETORNAR value
    FIM SE
    
    LANÇAR RuntimeError("Variável '" + name + "' não encontrada")
FIM FUNÇÃO

FUNÇÃO set_variable(name: String, value: Qualquer)
    """
    Define valor de variável no escopo apropriado
    """
    
    SE name EM this.local_scope ENTÃO
        this.local_scope[name] = value
    SENÃO SE name EM this.global_scope ENTÃO
        this.global_scope[name] = value
    SENÃO
        this.local_scope[name] = value
    FIM SE
    
    this.symbol_table.update(name, value)
FIM FUNÇÃO

FUNÇÃO apply_binary_operator(operator: String, left: Qualquer, right: Qualquer) -> Qualquer
    """
    Aplica operador binário
    """
    
    SE operator == "+" ENTÃO RETORNAR left + right
    SENÃO SE operator == "-" ENTÃO RETORNAR left - right
    SENÃO SE operator == "*" ENTÃO RETORNAR left * right
    SENÃO SE operator == "/" ENTÃO
        SE right == 0 ENTÃO
            LANÇAR RuntimeError("Divisão por zero")
        FIM SE
        RETORNAR left / right
    SENÃO
        LANÇAR RuntimeError("Operador desconhecido: " + operator)
    FIM SE
FIM FUNÇÃO

FUNÇÃO execute_native_string_function(func_name: String, arguments: Lista) -> Qualquer
    """
    Executa funções nativas de string
    """
    
    SE func_name == "strlen" ENTÃO
        RETORNAR TAMANHO(arguments[0])
    
    SENÃO SE func_name == "substr" ENTÃO
        string = arguments[0]
        start = arguments[1]
        length = arguments[2]
        RETORNAR string[start : start + length]
    
    SENÃO SE func_name == "charat" ENTÃO
        string = arguments[0]
        index = arguments[1]
        RETORNAR string[index]
    
    SENÃO SE func_name == "indexof" ENTÃO
        string = arguments[0]
        substring = arguments[1]
        RETORNAR string.index(substring)
    
    SENÃO SE func_name == "parseint" ENTÃO
        RETORNAR CONVERTER_PARA_INT(arguments[0])
    FIM SE
FIM FUNÇÃO
```

## Fluxo Completo de Execução

```pseudocode
PROCEDIMENTO interpretacao_completa(ast: AST_Node)
    """
    Fluxo completo de interpretação
    """
    
    # 1. Criar interpretador
    interpreter = NOVO Interpreter()
    
    # 2. Interpretar AST
    TENTAR
        interpreter.interpret(ast)
    CAPTURAR RuntimeError COMO e
        IMPRIMIR "❌ Erro de Execução: " + e.mensagem
        IMPRIMIR e.stack_trace
        SAIR(1)
    CAPTURAR Exception COMO e
        IMPRIMIR "❌ Erro Inesperado: " + e.mensagem
        IMPRIMIR e.stack_trace
        SAIR(1)
    FIM TENTAR
    
    # 3. Aguardar threads terminarem
    interpreter.thread_manager.wait_all()
    
    IMPRIMIR "✅ Execução concluída com sucesso"
FIM PROCEDIMENTO
```

## Características Principais

### Thread-Safety
- Cada thread PAR tem seu próprio `local_scope`
- `print_lock` garante impressões atômicas
- `symbol_table` usa locks internos
- Canais implementam sincronização thread-safe

### Orientação a Objetos
- Suporte completo a classes e herança
- `this` para acesso a membros
- Métodos com escopo próprio
- Atributos públicos (sem encapsulamento por enquanto)

### Concorrência
- Blocos PAR criam threads Python reais
- Comunicação via canais (send/receive)
- Join automático ao final de bloco PAR
- ThreadManager gerencia ciclo de vida

### Arrays
- Suporte a 1D e 2D
- Inicialização com valores padrão
- Acesso via índices
- Arrays de objetos suportados

### Escopo
- Resolução: local → global → symbol table
- Funções/métodos criam escopo próprio
- Parâmetros são copiados (pass-by-value)
- Symbol table hierárquica para nested scopes
