
---

## 📄 docs/backlog/product_backlog.md

```markdown
# 📌 Product Backlog – Interpretador MiniPar 2025.1

## Épicos
1. **Modelagem e Documentação**
   - Definir requisitos do interpretador
   - Criar diagramas UML (casos de uso, classes, arquitetura, sequência)
   - Elaborar pseudocódigos dos analisadores

2. **Componentes do Interpretador**
   - Implementar analisador léxico (Lexer)
   - Implementar analisador sintático (Parser)
   - Implementar analisador semântico
   - Implementar tabela de símbolos
   - Integrar os componentes ao runtime

3. **Execução da Linguagem MiniPar**
   - Implementar execução SEQ (sequencial)
   - Implementar execução PAR (threads)
   - Implementar canais de comunicação (c_channel) com sockets
   - Implementar chamadas de funções e métodos
   - Implementar suporte a objetos

4. **Testes**
   - Criar testes unitários dos analisadores
   - Realizar testes de integração do interpretador
   - Executar os programas de exemplo fornecidos (6 testes)

5. **Entrega Final**
   - Gerar relatório do projeto
   - Documentar passo a passo da execução dos programas de teste
   - Publicar o repositório no GitHub

---

## User Stories (Exemplos)

- **Como aluno**, quero modelar os componentes do interpretador em UML, para documentar a arquitetura.  
- **Como desenvolvedor**, quero implementar o analisador léxico, para identificar tokens do código-fonte MiniPar.  
- **Como usuário**, quero rodar um programa MiniPar com SEQ, para que seja executado de forma sequencial.  
- **Como usuário avançado**, quero rodar um programa MiniPar com PAR, para que múltiplas threads executem em paralelo.  
- **Como professor**, quero rodar os programas de teste oficiais, para validar o interpretador.  

---

## Critérios de Aceite
- O interpretador deve reconhecer corretamente a gramática MiniPar 2025.1.  
- O interpretador deve executar os programas de teste fornecidos no enunciado.  
- O repositório deve conter: documentação, código-fonte, testes e relatório final.  
