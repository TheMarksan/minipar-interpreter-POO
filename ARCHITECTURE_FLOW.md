# MiniPar Interpreter - Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MiniPar Source Code (.minipar)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         LEXER PHASE                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Lexer.py                                                  │  │
│  │  - Tokenizes source code                                   │  │
│  │  - Identifies keywords, operators, literals, identifiers   │  │
│  │  - Produces token stream                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼ Token Stream
┌─────────────────────────────────────────────────────────────────┐
│                        PARSER PHASE                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Parser.py                                                 │  │
│  │  - Builds Abstract Syntax Tree (AST)                       │  │
│  │  - Validates syntax against BNF grammar                    │  │
│  │  - Generates structured representation                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼ AST (utils/AST.py)
┌─────────────────────────────────────────────────────────────────┐
│                      INTERPRETER PHASE                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Interpreter.py                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  1. Collect Definitions                             │  │  │
│  │  │     - Classes, Functions, Global Variables          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  2. Execute Program                                 │  │  │
│  │  │     - SEQ blocks: Sequential execution              │  │  │
│  │  │     - PAR blocks: Parallel execution via threads    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Runtime Components:                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Channel    │  │ ThreadManager│  │  Thread-Local Scopes │  │
│  │              │  │              │  │                      │  │
│  │ - send()     │  │ - create()   │  │ - Global variables   │  │
│  │ - receive()  │  │ - start_all()│  │ - Local variables    │  │
│  │              │  │ - join_all() │  │   per thread         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          EXECUTION                               │
│  - Print output to console                                       │
│  - Handle user input                                             │
│  - Manage thread synchronization via channels                    │
│  - Execute parallel computations                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Parallel Execution

```
Source: PAR { worker1(); worker2(); }
    │
    ▼ Lexer
Tokens: [PAR, LBRACE, IDENT(worker1), LPAREN, RPAREN, ...]
    │
    ▼ Parser
AST: BlockNode(type="par", statements=[
       FunctionCallNode("worker1"),
       FunctionCallNode("worker2")
     ])
    │
    ▼ Interpreter
ThreadManager:
    │
    ├─► Thread 1: execute worker1()
    │   ├─ Local scope isolated
    │   └─ Shares global scope & channels
    │
    └─► Thread 2: execute worker2()
        ├─ Local scope isolated
        └─ Shares global scope & channels
    │
    ▼ join_all()
Continue sequential execution
```

## Channel Communication Flow

```
Thread A              Channel              Thread B
   │                    │                     │
   │ send(value)        │                     │
   ├───────────────────►│                     │
   │                    │ queue.put(value)    │
   │                    │                     │
   │                    │ receive(value)      │
   │                    │◄────────────────────┤
   │                    │ queue.get(block=True)
   │                    ├────────────────────►│
   │                    │      value          │
   │                    │                     │
```

## Key Components

### Lexer
- **Input**: Raw source code string
- **Output**: List of tokens
- **Responsibility**: Character-level analysis

### Parser
- **Input**: Token stream
- **Output**: AST
- **Responsibility**: Syntax validation and structure building

### AST
- **Input**: None (data structure)
- **Output**: Tree representation
- **Responsibility**: Program structure representation

### Interpreter
- **Input**: AST
- **Output**: Program execution (side effects)
- **Responsibility**: Code execution, variable management, thread coordination

### Channel
- **Input**: Values from any thread
- **Output**: Values to any thread
- **Responsibility**: Thread-safe communication

### ThreadManager
- **Input**: Thread targets and arguments
- **Output**: Managed thread execution
- **Responsibility**: Thread lifecycle management
