#!/usr/bin/env python3
"""
Testar se valores aparecem na tabela de símbolos após execução
"""

import requests
import json

codigo = '''SEQ {
    INT x;
    FLOAT y;
    STRING nome;
    
    x = 42;
    y = 3.14;
    nome = "MiniPar";
    
    print("X = " + x + "\\n");
    print("Y = " + y + "\\n");
    print("Nome = " + nome + "\\n");
}'''

print("=" * 70)
print("TESTANDO VALORES NA TABELA DE SÍMBOLOS")
print("=" * 70)

response = requests.post("http://localhost:8000/interpretar", json={"codigo": codigo})

if response.status_code == 200:
    data = response.json()
    
    symbol_table = data.get('symbol_table', {})
    
    print("\n✅ Resposta recebida!")
    
    # Variáveis
    variables = symbol_table.get('variables', [])
    print(f"\n📦 VARIÁVEIS ({len(variables)}):")
    print(f"{'Nome':<15} {'Tipo':<10} {'Valor':<20}")
    print("-" * 45)
    for v in variables:
        valor = v.get('value', 'None')
        if valor is None or valor == 'None':
            valor = '(não atribuído)'
        print(f"{v['name']:<15} {v['type']:<10} {str(valor):<20}")
    
    # Blocos
    blocks = symbol_table.get('blocks', [])
    print(f"\n🔷 BLOCOS ({len(blocks)}):")
    block_count = {}
    for block in blocks:
        block_count[block['type']] = block_count.get(block['type'], 0) + 1
    for btype, count in sorted(block_count.items()):
        print(f"  {btype}: {count}x")
    
    # Instruções
    statements = symbol_table.get('statements', [])
    print(f"\n📝 INSTRUÇÕES ({len(statements)}):")
    stmt_count = {}
    for stmt in statements:
        stmt_count[stmt['type']] = stmt_count.get(stmt['type'], 0) + 1
    for stype, count in sorted(stmt_count.items()):
        print(f"  {stype}: {count}x")
    
    print("\n" + "=" * 70)
    print("OUTPUT:")
    print("=" * 70)
    print(data.get('saida', 'Sem output'))
    
else:
    print(f"\n❌ Erro: {response.status_code}")
