# 🚀 Interpretador MiniPar 2025.1 (Orientado a Objetos)

**Equipe:** Aldary Wanderley, Guilherme Coutinho, Marcos Melo e Ruan <br>
**Disciplina:** Compiladores <br>
**Professor:** Arturo Hernandez Dominguez

---

## ⚡ Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/TheMarksan/minipar-interpreter-POO.git
cd minipar-interpreter-POO

# 2. Inicie o servidor backend (porta 8000)
python3 scripts/interpret_server.py --host 127.0.0.1 --port 8000 &

# 3. Inicie o servidor frontend (porta 8080)
python3 -m http.server 8080 --directory frontend &

# 4. Acesse a IDE no navegador
# http://127.0.0.1:8080
```

**Pronto!** Agora você pode escrever e executar programas MiniPar na interface web! 🎉

---

## 📌 Visão Geral
Este projeto implementa um **interpretador completo** para a linguagem **MiniPar 2025.1**, uma linguagem de programação orientada a objetos com suporte a **execução paralela**, **comunicação entre threads via canais** e **classes**.

O interpretador foi desenvolvido em **Python 3**, seguindo os princípios de **Programação Orientada a Objetos (POO)** e **Engenharia de Software**.

### 🎯 Principais Características
- ✨ **Interface Web Completa** - IDE com editor, syntax highlighting e painéis de resultado
- 🔍 **Análise Completa** - Léxica, Sintática, Semântica e Geração de TAC
- 🧵 **Execução Paralela** - Suporte nativo a threads e comunicação via canais
- 🎨 **POO Completa** - Classes, herança, métodos, atributos e encapsulamento
- 📊 **Arrays Multidimensionais** - Suporte a arrays 1D e 2D
- 🐛 **Validação Robusta** - Detecção de erros em todas as fases da compilação

## ✨ Funcionalidades da Linguagem MiniPar

### Recursos Principais
- ✅ **Execução Sequencial (SEQ)** - Blocos de código executados em sequência
- ✅ **Execução Paralela (PAR)** - Threads para execução concorrente
- ✅ **Canais de Comunicação (C_CHANNEL)** - Comunicação entre threads
- ✅ **Programação Orientada a Objetos** - Classes, herança, métodos e atributos
- ✅ **Arrays Multidimensionais** - Arrays 1D e 2D com suporte completo
- ✅ **Funções Globais** - Definição e chamada de funções

### Tipos de Dados
- `INT` - Números inteiros
- `FLOAT` - Números de ponto flutuante
- `STRING` - Cadeias de caracteres
- `BOOL` - Booleanos (true/false)
- `CHAR` - Caracteres individuais
- `C_CHANNEL` - Canais de comunicação entre threads
- `VOID` - Sem retorno (para métodos/funções)

### Estruturas de Controle
- `if`/`else` - Condicionais
- `while` - Loops com condição
- `for` - Loops com inicialização, condição e incremento

### Operadores
- **Aritméticos:** `+`, `-`, `*`, `/`, `%`
- **Relacionais:** `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Lógicos:** `&&`, `||`, `!`

### Entrada e Saída
- `print(...)` - Impressão na tela
- `input()` - Leitura do teclado
- `canal.send(valor)` - Envio via canal
- `canal.receive(var)` - Recepção via canal

### Outros Recursos
- Comentários com `#`
- Criação de objetos com `new`
- Acesso a atributos e métodos com `.`
- Suporte a `this` para referência ao objeto atual

---

## 🚀 Como Executar o Sistema

### Pré-requisitos
- **Python 3.8+** instalado
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

### 1️⃣ Instalação e Configuração

Clone o repositório e navegue até o diretório:
```bash
git clone https://github.com/TheMarksan/minipar-interpreter-POO.git
cd minipar-interpreter-POO
```

### 2️⃣ Iniciando o Backend (Servidor de Interpretação)

Execute o servidor Python na porta 8000:
```bash
python3 scripts/interpret_server.py --host 127.0.0.1 --port 8000
```

Ou em background com nohup:
```bash
nohup python3 scripts/interpret_server.py --host 127.0.0.1 --port 8000 > server.log 2>&1 &
```

**Verificação:** O servidor deve exibir:
```
Servidor rodando em http://127.0.0.1:8000
```

### 3️⃣ Iniciando o Frontend (Interface Web)

Em outro terminal, inicie o servidor HTTP para a interface:
```bash
python3 -m http.server 8080 --directory frontend
```

Ou em background:
```bash
nohup python3 -m http.server 8080 --directory frontend > http.log 2>&1 &
```

### 4️⃣ Acessando a Interface Web

Abra seu navegador e acesse:
```
http://127.0.0.1:8080
```

Você verá a **IDE MiniPar** com:
- ✏️ Editor de código com syntax highlighting
- ▶️ Botão "Executar" para interpretar o código
- 📊 Painéis de resultados (Léxico, Sintático, Semântico, TAC, Execução)
- 📁 Exemplos prontos para testar

### 5️⃣ Testando o Sistema

**Opção A - Via Interface Web:**
1. Acesse http://127.0.0.1:8080
2. Digite ou carregue um programa MiniPar
3. Clique em "Executar"
4. Veja os resultados nos painéis

**Opção B - Via Linha de Comando:**
```bash
# Testar um programa específico
curl -X POST http://127.0.0.1:8000/interpretar \
  -H "Content-Type: application/json" \
  -d '{"code": "SEQ { INT x; x = 10; print(\"x = \" + x + \"\\n\"); }"}'

# Testar programa de arquivo
curl -X POST http://127.0.0.1:8000/interpretar \
  -H "Content-Type: application/json" \
  -d "{\"code\": $(python3 -c 'import json; print(json.dumps(open("tests/hello_world.minipar").read()))')}"
```

**Opção C - Script Python Direto:**
```bash
cd minipar-interpreter-POO
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

# Seu código MiniPar
code = """
SEQ {
    INT x;
    x = 10;
    print("Valor de x: " + x + "\\n");
}
"""

# Pipeline de compilação
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
analyzer = SemanticAnalyzer()
result = analyzer.analyze(ast)

if result['success']:
    interpreter = Interpreter()
    interpreter.interpret(ast)
else:
    print("Erros encontrados:")
    for error in result['errors']:
        print(f"  - {error}")
EOF
```

### 6️⃣ Parando os Servidores

```bash
# Parar servidor de interpretação
pkill -f "interpret_server.py"

# Parar servidor frontend
pkill -f "http.server 8080"
```

---

## 🏗️ Arquitetura do Interpretador

O interpretador é composto por **componentes de software** independentes:

### Pipeline de Compilação
1. **Analisador Léxico (Lexer)** - Tokenização do código fonte
2. **Analisador Sintático (Parser)** - Construção da AST (Abstract Syntax Tree)
3. **Analisador Semântico** - Validação de tipos, escopo e uso de variáveis
4. **Gerador de TAC** - Código intermediário Three-Address Code
5. **Interpretador/Runtime** - Execução do programa

### Componentes Principais
- **Lexer** (`src/lexer/`) - Análise léxica e tokenização
- **Parser** (`src/parser/`) - Análise sintática e construção da AST
- **SemanticAnalyzer** (`src/semantic/`) - Validações semânticas
- **SymbolTable** (`src/symbol_table/`) - Gerenciamento de escopos e símbolos
- **Interpreter** (`src/runtime/`) - Execução do código
- **ThreadManager** (`src/runtime/`) - Gerenciamento de threads paralelas
- **Channel** (`src/runtime/`) - Comunicação entre threads
- **TACGenerator** (`src/codegen/`) - Geração de código intermediário

### Modelagem UML
Documentação completa disponível em `docs/`:
- Diagramas de **casos de uso**
- **Arquitetura em componentes**
- **Diagrama de classes**
- **Fluxos de execução**

---

## 📂 Estrutura do Repositório
```bash
minipar-interpreter-POO/
├── frontend/          # Interface web (HTML, CSS, JS)
│   ├── index.html     # Página principal da IDE
│   ├── home.css       # Estilos da interface
│   └── home.js        # Lógica da interface
├── scripts/           # Scripts auxiliares
│   └── interpret_server.py  # Servidor HTTP de interpretação
├── src/               # Código-fonte do interpretador
│   ├── lexer/         # Analisador léxico
│   ├── parser/        # Analisador sintático
│   ├── semantic/      # Analisador semântico
│   ├── symbol_table/  # Tabela de símbolos
│   ├── runtime/       # Interpretador e gerenciador de threads
│   ├── codegen/       # Gerador de código TAC
│   └── utils/         # Utilitários (impressão de AST, etc.)
├── tests/             # Programas de teste em MiniPar
│   ├── hello_world.minipar
│   ├── programa1_cliente_servidor.minipar
│   ├── programa2_threads.minipar
│   ├── programa3_neuronio.minipar
│   ├── programa4_xor_cpp.minipar
│   ├── programa5_recomendacao.minipar
│   └── programa6_quicksort.minipar
├── docs/              # Documentação (arquitetura, requisitos, UML)
├── examples/          # Exemplos extras
├── reports/           # Relatórios de execução
└── README.md          # Este arquivo
```

---

## 📝 Exemplos de Código MiniPar

### Exemplo 1: Hello World
```minipar
SEQ {
    print("Hello, MiniPar!\n");
}
```

### Exemplo 2: Variáveis e Operações
```minipar
SEQ {
    INT x;
    INT y;
    INT soma;
    
    x = 10;
    y = 20;
    soma = x + y;
    
    print("x = " + x + "\n");
    print("y = " + y + "\n");
    print("soma = " + soma + "\n");
}
```

### Exemplo 3: Estrutura de Controle
```minipar
SEQ {
    INT i;
    
    print("Contando de 1 a 5:\n");
    for i = 1; i <= 5; i = i + 1 {
        print("i = " + i + "\n");
    }
}
```

### Exemplo 4: Classes e Objetos
```minipar
CLASS Calculadora {
    INT resultado;
    
    VOID somar(INT a, INT b) {
        this.resultado = a + b;
    }
    
    INT obterResultado() {
        return this.resultado;
    }
}

SEQ {
    Calculadora calc;
    INT res;
    
    calc = new Calculadora();
    calc.somar(15, 25);
    res = calc.obterResultado();
    
    print("Resultado: " + res + "\n");
}
```

### Exemplo 5: Threads e Canais
```minipar
C_CHANNEL canal;

VOID thread_produtor() {
    INT i;
    for i = 1; i <= 3; i = i + 1 {
        canal.send(i);
        print("Produtor enviou: " + i + "\n");
    }
}

VOID thread_consumidor() {
    INT valor;
    INT i;
    for i = 1; i <= 3; i = i + 1 {
        canal.receive(valor);
        print("Consumidor recebeu: " + valor + "\n");
    }
}

PAR {
    thread_produtor();
    thread_consumidor();
}
```

### Exemplo 6: Array e Loop
```minipar
SEQ {
    INT numeros[5];
    INT i;
    INT soma;
    
    # Preencher array
    for i = 0; i < 5; i = i + 1 {
        numeros[i] = i * 2;
    }
    
    # Calcular soma
    soma = 0;
    for i = 0; i < 5; i = i + 1 {
        soma = soma + numeros[i];
    }
    
    print("Soma dos elementos: " + soma + "\n");
}
```

---

## 🧪 Programas de Teste Disponíveis

Na pasta `tests/` você encontra programas completos para testar:

| Programa | Descrição | Recursos Demonstrados |
|----------|-----------|----------------------|
| `hello_world.minipar` | Hello World básico | Print básico |
| `programa1_cliente_servidor.minipar` | Cliente-servidor | Threads, canais, comunicação |
| `programa2_threads.minipar` | Threads paralelas | PAR, fatorial, fibonacci |
| `programa3_neuronio.minipar` | Neurônio artificial | Classes, métodos, arrays |
| `programa4_xor_cpp.minipar` | Rede neural XOR | POO avançada, loops, floats |
| `programa5_recomendacao.minipar` | Sistema de recomendação | Classes, herança, arrays 2D |
| `programa6_quicksort.minipar` | Algoritmo Quicksort | Recursão, arrays, parsing |

---

## 🐛 Solução de Problemas

### Servidor não inicia
```bash
# Verificar se a porta está em uso
lsof -i :8000
lsof -i :8080

# Matar processos anteriores
pkill -f "interpret_server.py"
pkill -f "http.server 8080"
```

### Erro "Module not found"
```bash
# Certifique-se de estar no diretório correto
cd minipar-interpreter-POO

# Verifique a estrutura do projeto
ls -la src/
```

### Interface não carrega
- Limpe o cache do navegador (Ctrl+Shift+R ou Cmd+Shift+R)
- Verifique se o servidor frontend está rodando na porta 8080
- Acesse o console do navegador (F12) para ver erros

### Código não executa
- Verifique se há erros de sintaxe no painel "Erros"
- Certifique-se de usar `#` para comentários (não `//`)
- Todo código executável deve estar dentro de blocos `SEQ` ou `PAR`
- Declare todas as variáveis antes de usar

---

## 👥 Equipe de Desenvolvimento

- **Aldary Wanderley**
- **Guilherme Coutinho**
- **Marcos Melo**
- **Ruan**

**Professor Orientador:** Arturo Hernandez Dominguez  
**Disciplina:** Compiladores  
**Instituição:** UFAL - Universidade Federal de Alagoas

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da disciplina de Compiladores.

---

## 🔗 Links Úteis

- [Documentação Completa](docs/)
- [Especificação da Linguagem](src/BNF.md)
- [Arquitetura do Sistema](docs/arquitetura.md)
- [Requisitos](docs/requisitos.md)
- [Testes de Integração](docs/testes_integracao.md)

---

**Desenvolvido com ❤️ pela equipe MiniPar - UFAL 2025.1**
