# Resumo da Atualização da Documentação - MiniPar Interpreter

## Data: 8 de Outubro de 2025

### Documentos Atualizados

1. **BNF.md** (`src/BNF.md`)
2. **Pseudocódigo do Lexer** (`docs/pseudocode/lexer.md`)
3. **Pseudocódigo do Parser** (`docs/pseudocode/parser.md`)

---

## Principais Mudanças e Correções

### 1. BNF (Backus-Naur Form)

#### Adicionado:
- ✅ Suporte completo a **arrays 1D e 2D** com sintaxe detalhada
- ✅ **Funções de string** nativas: `strlen`, `substr`, `charat`, `indexof`, `parseint`
- ✅ **Operadores lógicos** (`&&`, `||`) com precedência correta
- ✅ **Palavra-chave `this`** para acesso a membros da classe
- ✅ **Parâmetros de função** com suporte a arrays
- ✅ **Inicialização de arrays** com `[]` e `{}`
- ✅ **Blocos aninhados** SEQ/PAR
- ✅ **Comentários** preservados como tokens

#### Corrigido:
- ✅ Sintaxe de **SEND/RECEIVE** com uso correto de maiúsculas
- ✅ **Else if** em cadeia com recursão correta
- ✅ **Ponto-e-vírgula opcional** em várias construções
- ✅ **Case-insensitive keywords** documentado
- ✅ Operador de **divisão** (`/`) adicionado

---

### 2. Pseudocódigo do Lexer

#### Características Implementadas:

**Técnica de Análise:**
- **Lookahead LL(1)**: Examina 1 caractere à frente sem consumir
- **Método `peek()`**: Lookahead fundamental para decisões
- **Método `match()`**: Consome caractere apenas se corresponder

**Funcionalidades:**
- ✅ Reconhecimento de **comentários** (#)
- ✅ **Strings** delimitadas por aspas duplas
- ✅ **Números** inteiros e decimais (lookahead para detectar `.`)
- ✅ **Identificadores** e palavras-chave (case-insensitive)
- ✅ **Operadores compostos** usando lookahead:
  - `==`, `!=`, `>=`, `<=`, `&&`, `||`
- ✅ Todos os **símbolos** da linguagem

**Lookahead Crítico:**
```pseudocode
// Exemplo: Distinguir >= de >
SE char == '>' ENTÃO
    SE peek() == '=' ENTÃO  // Lookahead
        consumir '='
        token = '>='
    SENÃO
        token = '>'
    FIM SE
FIM SE
```

---

### 3. Pseudocódigo do Parser

#### Características Implementadas:

**Técnica de Análise:**
- **Descendente Recursivo**: Um método por não-terminal
- **Lookahead LL(k)**: Examina 1-2 tokens à frente
- **Métodos de lookahead**:
  - `current_token()`: Token atual (lookahead de 0)
  - `peek(1)`: Próximo token (lookahead de 1)
  - `peek(2)`: Token após o próximo (lookahead de 2)

**Decisões com Lookahead:**
```pseudocode
// Exemplo: Distinguir função de declaração
SE match(TokenType.INT) ENTÃO
    SE peek().type == TokenType.IDENT E peek(2).type == TokenType.LPAREN ENTÃO
        // É uma função: int func()
        parse_function()
    SENÃO
        // É uma declaração: int x;
        parse_declaration()
    FIM SE
FIM SE
```

**Precedência de Operadores:**
1. **Menor precedência**: `||` (OR lógico)
2. `&&` (AND lógico)
3. `==`, `!=`, `>`, `<`, `>=`, `<=` (Relacionais)
4. `+`, `-` (Aditivos)
5. `*`, `/` (Multiplicativos)
6. **Maior precedência**: Unários, números, identificadores

**Estruturas Suportadas:**
- ✅ Classes com herança (`extends`)
- ✅ Métodos e atributos
- ✅ Funções com parâmetros
- ✅ Blocos SEQ/PAR aninhados
- ✅ If/Else If/Else em cadeia
- ✅ Loops (while, for)
- ✅ Arrays 1D e 2D
- ✅ Objetos e `this`
- ✅ Canais de comunicação

---

## Exemplos de Uso Correto

### 1. Comentários
```minipar
# Este é um comentário de linha
C_CHANNEL canal;  # Comentário inline
```

### 2. Funções com Parâmetros
```minipar
INT calcular(INT a, INT b) {
    RETURN a + b;
}
```

### 3. If/Else If/Else
```minipar
if operacao == "+" {
    resultado = a + b;
} else if operacao == "-" {
    resultado = a - b;
} else {
    resultado = 0;
}
```

### 4. Arrays
```minipar
INT arr[5];                    # Array 1D
INT matriz[3][3];              # Array 2D
INT nums[] = [1, 2, 3];        # Inicialização
```

### 5. Blocos SEQ/PAR
```minipar
PAR {
    funcao1();
    funcao2();
}

SEQ {
    PRINT("Finalizado");
}
```

### 6. Canais
```minipar
C_CHANNEL canal;

VOID sender() {
    canal.SEND(valor1, valor2);
}

VOID receiver() {
    INT v1, v2;
    canal.RECEIVE(v1, v2);
}
```

### 7. Classes e Objetos
```minipar
class Pessoa {
    STRING nome;
    INT idade;
    
    VOID apresentar() {
        PRINT("Nome: " + this.nome);
    }
}

SEQ {
    Pessoa p = new Pessoa();
    p.nome = "João";
    p.apresentar();
}
```

---

## Características Importantes

### Case-Insensitivity
```minipar
IF x == 5 {      # Válido
    PRINT(x);
}

if x == 5 {      # Também válido
    print(x);
}
```

### Ponto-e-vírgula Opcional
```minipar
INT x = 5;       # Com ponto-e-vírgula
INT y = 10       # Sem ponto-e-vírgula (também válido)
```

### Operadores Lógicos
```minipar
if (a > 0 && b < 10) || c == 5 {
    PRINT("Condição satisfeita");
}
```

---

## Análise de Lookahead

### Lexer (LL(1))
- **1 caractere de lookahead**
- Resolve ambiguidades entre operadores simples e compostos
- Detecta fim de strings e comentários

### Parser (LL(k))
- **1-2 tokens de lookahead** na maioria dos casos
- Distingue entre:
  - Função vs declaração
  - Atribuição vs chamada de função
  - Atributo vs método
  - Array 1D vs 2D

---

## Conformidade com Implementação

✅ **BNF** reflete exatamente o que o código implementa
✅ **Pseudocódigo do Lexer** corresponde ao `src/lexer/Lexer.py`
✅ **Pseudocódigo do Parser** corresponde ao `src/parser/Parser.py`
✅ **Exemplos** validados com programas de teste funcionais

---

## Programas de Teste Validados

1. ✅ **programa1_cliente_servidor.minipar** - Comunicação cliente/servidor
2. ✅ **programa2_threads.minipar** - Threads com canais
3. ✅ **programa3_neuronio.minipar** - Classes e objetos
4. ✅ **teste_if_minusculo.minipar** - Case-insensitivity
5. ✅ **teste_else_if_seq.minipar** - Else if em cadeia
6. ✅ **teste_dois_canais.minipar** - Comunicação com canais

---

## Conclusão

A documentação está agora **100% alinhada** com a implementação do interpretador MiniPar. Todos os recursos implementados estão devidamente documentados na BNF e nos pseudocódigos, facilitando:

- **Manutenção** do código
- **Desenvolvimento** de novos recursos
- **Ensino** da linguagem MiniPar
- **Debugging** e resolução de problemas

As técnicas de **Lookahead LL(1)** no lexer e **LL(k)** no parser estão claramente explicadas, mostrando como o interpretador resolve ambiguidades e toma decisões de parsing.
