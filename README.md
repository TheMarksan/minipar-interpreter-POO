# Interpretador MiniPar 2025.1 (Orientado a Objetos)

**Equipe:** Aldary Wanderley, Guilherme Coutinho, Marcos Melo e Ruan <br>
**Disciplina:** Compiladores <br>
**Professor:** Arturo Hernandez Dominguez

## 📌 Visão Geral
Este projeto tem como objetivo desenvolver um **interpretador** para a linguagem **MiniPar 2025.1**, orientada a objetos, utilizando conceitos de **Engenharia de Software** e **Componentes de Software**.  

O interpretador será implementado em **Python**, seguindo práticas de **Programação Orientada a Objetos (POO)**.

## Funcionalidades da Linguagem MiniPar
- **Execução Sequencial (SEQ)**
- **Execução Paralela (PAR)** com **Threads**
- **Canais de Comunicação (c_channel)** usando **sockets**
- Tipos de variáveis: `Bool`, `Int`, `String`, `c_channel`
- Entrada e saída: `Input` (teclado) e `Output` (tela)
- Comentários via `#`
- Suporte a **funções**, **objetos** e **métodos**
- Estruturas de controle: `if`, `else`, `while`, (possível extensão para `do`, `for`)
- Precedência de operadores `+`, `-`, `*`, `/`

---

## Arquitetura do Interpretador
O interpretador será composto por **componentes de software** independentes:
- **Analisador Léxico (Lexer)**
- **Analisador Sintático (Parser)**
- **Analisador Semântico**
- **Tabela de Símbolos**
- **Interpretador/Runtime**
  - Execução sequencial (SEQ)
  - Execução paralela (PAR)
  - Comunicação via canais (`c_channel`)

Cada componente será modelado utilizando **UML**:
- Diagramas de **casos de uso**
- **Arquitetura em componentes**
- **Diagrama de classes**

---

## 📂 Estrutura do Repositório
```bash
minipar-interpreter-POO/
├── docs/              # Documentação (backlog, pseudocódigos, UML, testes)
├── src/               # Código-fonte do interpretador
├── tests/             # Programas de teste em MiniPar
├── reports/           # Relatórios de execução
├── examples/          # Exemplos extras (ex: Relógio)
└── README.md          # Este arquivo
