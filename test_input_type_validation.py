#!/usr/bin/env python3
"""
Teste de validação de tipos no INPUT
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

# Código de teste
codigo = """
SEQ {
    int idade;
    string nome;
    
    print("Digite sua idade: ");
    idade = input();
    print("Você tem ");
    print(idade);
    print(" anos.\\n");
    
    print("Digite seu nome: ");
    nome = input();
    print("Olá, ");
    print(nome);
    print("!\\n");
}
"""

print("=" * 60)
print("TESTE DE VALIDAÇÃO DE TIPOS NO INPUT")
print("=" * 60)

# Lexer
lexer = Lexer(codigo)
tokens = lexer.tokenize()

# Parser
parser = Parser(tokens)
ast = parser.parse()

# Semantic
sa = SemanticAnalyzer()
result = sa.analyze(ast)

if result['warnings']:
    print("\n⚠️  AVISOS SEMÂNTICOS:")
    for warning in result['warnings']:
        print(f"  - {warning}")

if result['errors']:
    print("\n❌ ERROS SEMÂNTICOS:")
    for error in result['errors']:
        print(f"  - {error}")
    sys.exit(1)

# Interpreter com inputs simulados
print("\n" + "=" * 60)
print("EXECUÇÃO COM INPUT VÁLIDO (idade = 25)")
print("=" * 60)

inputs = ["25", "Marco"]
input_index = [0]

def mock_input(prompt=""):
    if prompt:
        print(prompt, end="")
    value = inputs[input_index[0]]
    print(f"[INPUT: {value}]")
    input_index[0] += 1
    return value

interpreter = Interpreter(input_callback=mock_input)
try:
    interpreter.interpret(ast)
    print("✅ Execução bem-sucedida!")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste com input inválido
print("\n" + "=" * 60)
print("EXECUÇÃO COM INPUT INVÁLIDO (idade = 'abc')")
print("=" * 60)

inputs = ["abc", "Marco"]
input_index = [0]

interpreter2 = Interpreter(input_callback=mock_input)
try:
    interpreter2.interpret(ast)
    print("❌ ERRO: Deveria ter falhado!")
except RuntimeError as e:
    print(f"✅ Erro capturado corretamente: {e}")
except Exception as e:
    print(f"⚠️  Erro inesperado: {e}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
