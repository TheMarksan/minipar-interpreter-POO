#!/usr/bin/env python3
"""
Teste final: Paralelismo com simulação de I/O
Loops vazios para simular operações que demoram
"""

import sys
import os
import time

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

# Teste com loops que demoram (simula I/O)
codigo = """
VOID tarefa_A() {
    print("[A] Iniciando\\n");
    INT i;
    for i = 0; i < 100000; i = i + 1 {
        # Trabalho pesado
    }
    print("[A] Meio do caminho\\n");
    for i = 0; i < 100000; i = i + 1 {
        # Mais trabalho
    }
    print("[A] Finalizando\\n");
}

VOID tarefa_B() {
    print("[B] Iniciando\\n");
    INT j;
    for j = 0; j < 100000; j = j + 1 {
        # Trabalho pesado
    }
    print("[B] Meio do caminho\\n");
    for j = 0; j < 100000; j = j + 1 {
        # Mais trabalho
    }
    print("[B] Finalizando\\n");
}

SEQ {
    print("\\n╔════════════════════════════════════════╗\\n");
    print("║  TESTE DEFINITIVO DE PARALELISMO      ║\\n");
    print("╚════════════════════════════════════════╝\\n\\n");
    
    PAR {
        tarefa_A();
        tarefa_B();
    }
    
    print("\\n✅ Ambas as tarefas concluídas!\\n");
}
"""

print("=" * 70)
print("TESTE DEFINITIVO - PARALELISMO COM TRABALHO PESADO")
print("=" * 70)

# Lexer
lexer = Lexer(codigo)
tokens = lexer.tokenize()

# Parser
parser = Parser(tokens)
ast = parser.parse()

# Semantic
sa = SemanticAnalyzer()
result = sa.analyze(ast)

if result['errors']:
    print("\n❌ ERROS:")
    for error in result['errors']:
        print(f"  - {error}")
    sys.exit(1)

# Interpreter - executar 5 vezes
print("\n" + "=" * 70)
print("EXECUTANDO 5 VEZES PARA VERIFICAR VARIAÇÃO NA ORDEM")
print("=" * 70)

for run in range(5):
    print(f"\n{'='*70}")
    print(f"EXECUÇÃO #{run + 1}")
    print(f"{'='*70}")
    
    start = time.time()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Tempo: {elapsed*1000:.2f}ms")

print("\n" + "=" * 70)
print("CONCLUSÃO")
print("=" * 70)
print("""
📊 ANÁLISE DOS RESULTADOS:

✅ PARALELO se:
   - Prints de [A] e [B] aparecem intercalados
   - Ordem varia entre execuções
   - Nem sempre é: A-iniciando, A-meio, A-fim, B-iniciando, B-meio, B-fim
   - Exemplo: [A] Iniciando, [B] Iniciando, [A] Meio, [B] Meio, etc.

❌ SEQUENCIAL se:
   - Sempre a mesma ordem em todas as execuções
   - Sempre: todos [A], depois todos [B]
   - Nunca há intercalação

🔍 O QUE OBSERVAMOS:
""")
