# Pseudocódigo da Tabela de Símbolos (SymbolTable)

## Visão Geral
A Tabela de Símbolos é responsável por gerenciar identificadores (variáveis, funções, classes) e seus escopos durante a análise semântica e execução do programa MiniPar. Implementa uma estrutura hierárquica de escopos com suporte a thread-safety.

## Estruturas de Dados

### Classe Symbol
```pseudocode
CLASSE Symbol
    """
    Representa um símbolo (variável, função, classe, etc.)
    """
    
    ATRIBUTOS:
        name: String              # Nome do símbolo
        symbol_type: String       # Tipo do símbolo (INT, FLOAT, STRING, etc.)
        value: Qualquer          # Valor atual (None se não inicializado)
        scope_level: Inteiro     # Nível do escopo onde foi declarado
        is_array: Boolean        # Se é um array
        array_size: Inteiro      # Tamanho do array (se aplicável)
        is_function: Boolean     # Se é uma função
        is_class: Boolean        # Se é uma classe
        parameters: Lista        # Parâmetros (se for função)
        return_type: String      # Tipo de retorno (se for função)
    
    CONSTRUTOR __init__(name, symbol_type, value=None, scope_level=0, 
                        is_array=False, array_size=None):
        this.name = name
        this.symbol_type = symbol_type
        this.value = value
        this.scope_level = scope_level
        this.is_array = is_array
        this.array_size = array_size
        this.is_function = False
        this.is_class = False
        this.parameters = []
        this.return_type = None
    FIM CONSTRUTOR
    
    FUNÇÃO __repr__() -> String
        RETORNAR "Symbol(" + this.name + ", " + this.symbol_type + 
                 ", scope=" + this.scope_level + ")"
    FIM FUNÇÃO
FIM CLASSE
```

### Classe Scope
```pseudocode
CLASSE Scope
    """
    Representa um escopo (bloco de código com suas próprias variáveis)
    Implementa encadeamento de escopos (escopo filho → escopo pai)
    """
    
    ATRIBUTOS:
        scope_level: Inteiro     # Nível do escopo (0 = global)
        parent: Scope ou Null    # Escopo pai (null se for global)
        symbols: Dicionário      # Símbolos neste escopo {nome: Symbol}
    
    CONSTRUTOR __init__(scope_level, parent=None):
        this.scope_level = scope_level
        this.parent = parent
        this.symbols = {}
    FIM CONSTRUTOR
FIM CLASSE
```

## Operações da Classe Scope

### Definir Símbolo

```pseudocode
FUNÇÃO define(name: String, symbol: Symbol)
    """
    Define um novo símbolo no escopo atual
    Lança exceção se símbolo já existe
    """
    
    SE name EM this.symbols ENTÃO
        LANÇAR Exception("Symbol '" + name + "' already defined in current scope")
    FIM SE
    
    this.symbols[name] = symbol
FIM FUNÇÃO
```

### Buscar Símbolo (Escopo Atual)

```pseudocode
FUNÇÃO lookup(name: String) -> Symbol ou Null
    """
    Busca símbolo apenas no escopo atual
    Retorna None se não encontrado
    """
    
    SE name EM this.symbols ENTÃO
        RETORNAR this.symbols[name]
    FIM SE
    
    RETORNAR Null
FIM FUNÇÃO
```

### Buscar Símbolo (Recursivo)

```pseudocode
FUNÇÃO lookup_recursive(name: String) -> Symbol ou Null
    """
    Busca símbolo no escopo atual e em escopos pai (recursivamente)
    Implementa a regra de resolução de escopo léxico
    """
    
    # Busca no escopo atual
    symbol = this.lookup(name)
    SE symbol NÃO É Null ENTÃO
        RETORNAR symbol
    FIM SE
    
    # Busca no escopo pai (recursão)
    SE this.parent NÃO É Null ENTÃO
        RETORNAR this.parent.lookup_recursive(name)
    FIM SE
    
    RETORNAR Null
FIM FUNÇÃO
```

### Atualizar Símbolo

```pseudocode
FUNÇÃO update(name: String, value: Qualquer) -> Boolean
    """
    Atualiza o valor de um símbolo
    Busca recursivamente se não estiver no escopo atual
    """
    
    SE name EM this.symbols ENTÃO
        this.symbols[name].value = value
        RETORNAR Verdadeiro
    FIM SE
    
    SE this.parent NÃO É Null ENTÃO
        RETORNAR this.parent.update(name, value)
    FIM SE
    
    RETORNAR Falso
FIM FUNÇÃO
```

### Verificar Existência

```pseudocode
FUNÇÃO exists(name: String) -> Boolean
    """
    Verifica se símbolo existe no escopo atual
    """
    RETORNAR name EM this.symbols
FIM FUNÇÃO

FUNÇÃO exists_recursive(name: String) -> Boolean
    """
    Verifica se símbolo existe no escopo atual ou em escopos pai
    """
    
    SE this.exists(name) ENTÃO
        RETORNAR Verdadeiro
    FIM SE
    
    SE this.parent NÃO É Null ENTÃO
        RETORNAR this.parent.exists_recursive(name)
    FIM SE
    
    RETORNAR Falso
FIM FUNÇÃO
```

## Classe SymbolTable (Principal)

### Estrutura

```pseudocode
CLASSE SymbolTable
    """
    Gerenciador principal de símbolos e escopos
    Thread-safe para suporte a blocos PAR
    """
    
    ATRIBUTOS:
        global_scope: Scope          # Escopo global (nível 0)
        lock: Threading.Lock         # Lock para thread-safety
        current_scope: Scope         # Escopo atual
        scope_level: Inteiro        # Nível do escopo atual
    
    CONSTRUTOR __init__():
        this.global_scope = NOVO Scope(0)
        this.lock = NOVO Threading.Lock()
        this.current_scope = this.global_scope
        this.scope_level = 0
    FIM CONSTRUTOR
FIM CLASSE
```

## Operações da SymbolTable

### Gerenciamento de Escopo

```pseudocode
FUNÇÃO enter_scope() -> Scope
    """
    Entra em um novo escopo (cria escopo filho)
    Usado ao entrar em funções, blocos if/while/for, etc.
    """
    
    this.scope_level = this.scope_level + 1
    new_scope = NOVO Scope(this.scope_level, this.current_scope)
    this.current_scope = new_scope
    
    RETORNAR new_scope
FIM FUNÇÃO

FUNÇÃO exit_scope()
    """
    Sai do escopo atual (volta para escopo pai)
    Usado ao sair de funções, blocos, etc.
    """
    
    SE this.current_scope.parent NÃO É Null ENTÃO
        this.current_scope = this.current_scope.parent
        this.scope_level = this.scope_level - 1
    FIM SE
FIM FUNÇÃO
```

### Definir Símbolo (Variável)

```pseudocode
FUNÇÃO define(name: String, symbol_type: String, value=None, 
              is_array=False, array_size=None) -> Symbol
    """
    Define uma nova variável no escopo atual
    Thread-safe para uso em blocos PAR
    """
    
    ADQUIRIR this.lock
    TENTAR
        # Verifica se já existe no escopo atual
        SE this.current_scope.exists(name) ENTÃO
            RETORNAR this.current_scope.lookup(name)
        FIM SE
        
        # Cria novo símbolo
        symbol = NOVO Symbol(name, symbol_type, value, this.scope_level, 
                            is_array, array_size)
        
        # Define no escopo atual
        this.current_scope.define(name, symbol)
        
        RETORNAR symbol
    
    FINALMENTE
        LIBERAR this.lock
    FIM TENTAR
FIM FUNÇÃO
```

### Definir Função

```pseudocode
FUNÇÃO define_function(name: String, return_type: String, 
                       parameters: Lista) -> Symbol
    """
    Define uma nova função no escopo atual
    """
    
    ADQUIRIR this.lock
    TENTAR
        # Verifica se já existe
        SE this.current_scope.exists(name) ENTÃO
            RETORNAR this.current_scope.lookup(name)
        FIM SE
        
        # Cria símbolo de função
        symbol = NOVO Symbol(name, return_type, None, this.scope_level)
        symbol.is_function = Verdadeiro
        symbol.return_type = return_type
        symbol.parameters = parameters
        
        # Define no escopo atual
        this.current_scope.define(name, symbol)
        
        RETORNAR symbol
    
    FINALMENTE
        LIBERAR this.lock
    FIM TENTAR
FIM FUNÇÃO
```

### Definir Classe

```pseudocode
FUNÇÃO define_class(name: String, attributes: Lista, methods: Lista, 
                    parent=None) -> Symbol
    """
    Define uma nova classe no escopo atual
    """
    
    ADQUIRIR this.lock
    TENTAR
        # Verifica se já existe
        SE this.current_scope.exists(name) ENTÃO
            RETORNAR this.current_scope.lookup(name)
        FIM SE
        
        # Cria símbolo de classe
        symbol = NOVO Symbol(name, "class", None, this.scope_level)
        symbol.is_class = Verdadeiro
        symbol.value = {
            'attributes': attributes,
            'methods': methods,
            'parent': parent
        }
        
        # Define no escopo atual
        this.current_scope.define(name, symbol)
        
        RETORNAR symbol
    
    FINALMENTE
        LIBERAR this.lock
    FIM TENTAR
FIM FUNÇÃO
```

### Buscar Símbolo

```pseudocode
FUNÇÃO lookup(name: String) -> Symbol ou Null
    """
    Busca símbolo no escopo atual e escopos pai
    """
    RETORNAR this.current_scope.lookup_recursive(name)
FIM FUNÇÃO
```

### Atualizar Valor

```pseudocode
FUNÇÃO update(name: String, value: Qualquer) -> Boolean
    """
    Atualiza o valor de um símbolo existente
    """
    
    symbol = this.lookup(name)
    SE symbol NÃO É Null ENTÃO
        symbol.value = value
        RETORNAR Verdadeiro
    FIM SE
    
    RETORNAR Falso
FIM FUNÇÃO
```

### Verificar Existência

```pseudocode
FUNÇÃO exists(name: String) -> Boolean
    """
    Verifica se símbolo existe
    """
    RETORNAR this.current_scope.exists_recursive(name)
FIM FUNÇÃO
```

### Obter Valor

```pseudocode
FUNÇÃO get_value(name: String) -> Qualquer
    """
    Obtém o valor de um símbolo
    """
    
    symbol = this.lookup(name)
    SE symbol NÃO É Null ENTÃO
        RETORNAR symbol.value
    FIM SE
    
    RETORNAR Null
FIM FUNÇÃO
```

### Obter Todos os Símbolos

```pseudocode
FUNÇÃO get_all_symbols(scope=None) -> Lista[Symbol]
    """
    Retorna todos os símbolos visíveis do escopo especificado
    (incluindo símbolos dos escopos pai)
    """
    
    SE scope É Null ENTÃO
        scope = this.current_scope
    FIM SE
    
    symbols = []
    current = scope
    
    ENQUANTO current NÃO É Null FAÇA
        PARA CADA name, symbol EM current.symbols FAÇA
            symbols.ADICIONAR(symbol)
        FIM PARA
        current = current.parent
    FIM ENQUANTO
    
    RETORNAR symbols
FIM FUNÇÃO
```

### Imprimir Tabela

```pseudocode
FUNÇÃO print_table()
    """
    Imprime a tabela de símbolos formatada (para debug)
    """
    
    IMPRIMIR "=== Symbol Table ==="
    
    symbols = this.get_all_symbols()
    PARA CADA symbol EM symbols FAÇA
        IMPRIMIR FORMATADO(
            "  %-20s | Type: %-10s | Scope: %d | Value: %s",
            symbol.name,
            symbol.symbol_type,
            symbol.scope_level,
            symbol.value
        )
    FIM PARA
    
    IMPRIMIR "=" * 80
FIM FUNÇÃO
```

## Exemplo de Uso

```pseudocode
PROCEDIMENTO exemplo_uso()
    # Criar tabela de símbolos
    st = NOVO SymbolTable()
    
    # Escopo global
    st.define("x", "INT", 10)
    st.define("y", "FLOAT", 3.14)
    
    # Entrar em escopo de função
    st.enter_scope()
    st.define("z", "STRING", "hello")
    st.define("x", "INT", 20)  # Sobrescreve x local
    
    IMPRIMIR st.lookup("x").value  # 20 (escopo local)
    IMPRIMIR st.lookup("y").value  # 3.14 (escopo global)
    IMPRIMIR st.lookup("z").value  # "hello" (escopo local)
    
    # Sair do escopo
    st.exit_scope()
    
    IMPRIMIR st.lookup("x").value  # 10 (escopo global)
    IMPRIMIR st.lookup("z")        # None (não existe mais)
    
    # Imprimir tabela
    st.print_table()
FIM PROCEDIMENTO
```

## Fluxo de Execução

```pseudocode
PROCEDIMENTO fluxo_completo()
    """
    Exemplo de fluxo completo com funções e classes
    """
    
    st = NOVO SymbolTable()
    
    # 1. Declarações globais
    st.define("global_var", "INT", 0)
    st.define_class("MinhaClasse", ["attr1", "attr2"], ["metodo1"])
    st.define_function("minha_funcao", "VOID", [{"type": "INT", "name": "param"}])
    
    # 2. Entrar em função
    st.enter_scope()
    st.define("local_var", "STRING", "abc")
    
    # 3. Entrar em bloco if
    st.enter_scope()
    st.define("temp", "BOOL", Verdadeiro)
    
    # 4. Sair de bloco if
    st.exit_scope()
    
    # 5. Sair de função
    st.exit_scope()
    
    # 6. Verificar símbolos
    AFIRMAR st.exists("global_var") == Verdadeiro
    AFIRMAR st.exists("local_var") == Falso
    AFIRMAR st.exists("temp") == Falso
FIM PROCEDIMENTO
```

## Thread-Safety para Blocos PAR

```pseudocode
PROCEDIMENTO exemplo_par()
    """
    Exemplo de uso com blocos PAR (threads)
    """
    
    st = NOVO SymbolTable()
    
    # Variável compartilhada
    st.define("contador", "INT", 0)
    
    # Duas threads acessando a tabela
    THREAD thread1:
        PARA i = 0 ATÉ 100 FAÇA
            valor = st.get_value("contador")
            st.update("contador", valor + 1)  # Thread-safe com lock
        FIM PARA
    FIM THREAD
    
    THREAD thread2:
        PARA i = 0 ATÉ 100 FAÇA
            valor = st.get_value("contador")
            st.update("contador", valor + 1)  # Thread-safe com lock
        FIM PARA
    FIM THREAD
    
    AGUARDAR thread1, thread2
    
    IMPRIMIR st.get_value("contador")  # Pode não ser 200 devido a condições de corrida
                                       # mas a tabela permanece consistente
FIM PROCEDIMENTO
```

## Notas de Implementação

### Características Principais
- ✅ Estrutura hierárquica de escopos
- ✅ Resolução de escopo léxico
- ✅ Thread-safe com locks
- ✅ Suporte a variáveis, funções e classes
- ✅ Suporte a arrays
- ✅ Impressão formatada para debug

### Escopo Léxico vs. Dinâmico
MiniPar usa **escopo léxico** (estático):
- Símbolos são resolvidos baseado na estrutura do código
- Função busca variáveis no escopo onde foi **definida**
- Não no escopo onde foi **chamada**

### Complexidade
- `define()`: O(1)
- `lookup()`: O(n) onde n = profundidade do escopo
- `update()`: O(n) onde n = profundidade do escopo
- `exists()`: O(n) onde n = profundidade do escopo
- `enter_scope()`: O(1)
- `exit_scope()`: O(1)
