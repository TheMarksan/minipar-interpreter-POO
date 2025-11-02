#!/usr/bin/env python3
"""
Teste de paralelismo com prints intercalados
Agora com lock no print para evitar race conditions
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

# Teste com prints que devem aparecer intercalados
codigo = """
VOID thread1() {
    print("A1\\n");
    print("A2\\n");
    print("A3\\n");
    print("A4\\n");
    print("A5\\n");
}

VOID thread2() {
    print("B1\\n");
    print("B2\\n");
    print("B3\\n");
    print("B4\\n");
    print("B5\\n");
}

SEQ {
    print("=== INICIO DO TESTE ===\\n");
    print("Verificando paralelismo com locks corretos\\n\\n");
    
    PAR {
        thread1();
        thread2();
    }
    
    print("\\n=== FIM DO TESTE ===\\n");
}
"""

print("=" * 70)
print("TESTE DE PARALELISMO - PRINTS COM LOCK")
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

# Interpreter
print("\n" + "=" * 70)
print("SAÍDA:")
print("=" * 70 + "\n")

# Executar múltiplas vezes para ver variação
for i in range(3):
    print(f"\n--- Execução {i+1} ---")
    interpreter = Interpreter()
    interpreter.interpret(ast)

print("\n" + "=" * 70)
print("ANÁLISE:")
print("=" * 70)
print("\n✅ Se você vê A's e B's intercalados = PARALELO")
print("❌ Se você vê todos A's, depois todos B's = SEQUENCIAL")
print("\n💡 Com lock no print, a ordem pode variar entre execuções,")
print("   provando que as threads estão competindo pelo lock!")
