#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para o analisador semântico
Identifica inconsistências entre o analisador semântico e o interpretador
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

def test_case(name, code, should_pass_semantic=True):
    print(f'\n{"="*60}')
    print(f'TESTE: {name}')
    print(f'{"="*60}')
    print(f'Código:\n{code}')
    print('-' * 60)
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Análise semântica
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        print(f'Análise Semântica: {"✅ OK" if result["success"] else "❌ FALHOU"}')
        if result['errors']:
            print('Erros semânticos:')
            for error in result['errors']:
                print(f'  - {error}')
        if result['warnings']:
            print('Avisos:')
            for warning in result['warnings']:
                print(f'  - {warning}')
        
        # Interpretação (apenas se passou na semântica)
        if result['success']:
            print('\nExecutando interpretador...')
            interpreter = Interpreter()
            try:
                interpreter.interpret(ast)
                print('✅ Interpretação bem-sucedida')
            except Exception as e:
                print(f'❌ Erro de runtime: {e}')
        
        if should_pass_semantic and not result['success']:
            print('\n⚠️  INCONSISTÊNCIA: O código deveria passar na análise semântica!')
        elif not should_pass_semantic and result['success']:
            print('\n⚠️  INCONSISTÊNCIA: O código NÃO deveria passar na análise semântica!')
        
    except Exception as e:
        print(f'❌ Erro durante teste: {e}')
        import traceback
        traceback.print_exc()

# ============================================================================
# TESTES
# ============================================================================

# Teste 1: Concatenação de string com número (deveria passar)
test_case(
    "Concatenação string + número",
    '''
SEQ {
    INT x;
    x = 10;
    print("Valor: " + x + "\\n");
}
''',
    should_pass_semantic=True
)

# Teste 2: Operações aritméticas INT + FLOAT (deveria passar)
test_case(
    "INT + FLOAT (conversão implícita)",
    '''
SEQ {
    INT x;
    FLOAT y;
    x = 10;
    y = 3.14;
    print(x + y);
}
''',
    should_pass_semantic=True
)

# Teste 3: Input retorna STRING
test_case(
    "Input (retorna STRING)",
    '''
SEQ {
    STRING entrada;
    entrada = input();
    print(entrada);
}
''',
    should_pass_semantic=True
)

# Teste 4: Variável não declarada (NÃO deveria passar)
test_case(
    "Variável não declarada",
    '''
SEQ {
    print(x);
}
''',
    should_pass_semantic=False
)

# Teste 5: Função não declarada (NÃO deveria passar)
test_case(
    "Função não declarada",
    '''
SEQ {
    funcao_inexistente();
}
''',
    should_pass_semantic=False
)

# Teste 6: Tipo incompatível na atribuição (NÃO deveria passar se strict)
test_case(
    "Atribuição de STRING para INT",
    '''
SEQ {
    INT x;
    x = "texto";
}
''',
    should_pass_semantic=False
)

# Teste 7: Array com índice não inteiro (NÃO deveria passar)
test_case(
    "Array com índice string",
    '''
SEQ {
    INT arr[10];
    STRING idx;
    idx = "abc";
    print(arr[idx]);
}
''',
    should_pass_semantic=False
)

# Teste 8: Return fora de função (NÃO deveria passar)
test_case(
    "Return fora de função",
    '''
SEQ {
    return 10;
}
''',
    should_pass_semantic=False
)

# Teste 9: Funções nativas de string (deveria passar)
test_case(
    "Funções nativas strlen, charat, parseint",
    '''
SEQ {
    STRING texto;
    INT tamanho;
    STRING char;
    INT numero;
    
    texto = "Hello";
    tamanho = strlen(texto);
    char = charat(texto, 0);
    numero = parseint("42");
    
    print(tamanho);
    print(char);
    print(numero);
}
''',
    should_pass_semantic=True
)

# Teste 10: Classe e instanciação (deveria passar)
test_case(
    "Classe com atributos e métodos",
    '''
class Pessoa {
    STRING nome;
    INT idade;
    
    VOID setNome(STRING n) {
        this.nome = n;
    }
    
    STRING getNome() {
        return this.nome;
    }
}

SEQ {
    Pessoa p;
    p = new Pessoa();
    p.setNome("João");
    print(p.getNome());
}
''',
    should_pass_semantic=True
)

# Teste 11: Array bidimensional (deveria passar)
test_case(
    "Array 2D",
    '''
SEQ {
    INT matriz[3][3];
    matriz[0][0] = 1;
    matriz[1][1] = 5;
    print(matriz[0][0]);
    print(matriz[1][1]);
}
''',
    should_pass_semantic=True
)

# Teste 12: Condição não booleana em IF (NÃO deveria passar em análise estrita)
test_case(
    "Condição IF com tipo não booleano",
    '''
SEQ {
    INT x;
    x = 10;
    if x {
        print("ok");
    }
}
''',
    should_pass_semantic=False
)

print(f'\n{"="*60}')
print('TESTES CONCLUÍDOS')
print(f'{"="*60}')
