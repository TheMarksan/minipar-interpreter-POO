#!/usr/bin/env python3
"""Teste completo de todas as funcionalidades do WebSocket"""
import asyncio
import websockets
import json

async def test_full():
    try:
        async with websockets.connect("ws://localhost:8001") as websocket:
            # Código com função e classe
            code = """
SEQ {
    // Função simples
    function soma(a, b) {
        return a + b
    }
    
    // Classe
    class Pessoa {
        string nome
        int idade
        
        function init(n, i) {
            nome = n
            idade = i
        }
    }
    
    // Uso
    int resultado
    resultado = soma(5, 3)
    print(resultado)
    
    Pessoa p
    p = new Pessoa("João", 25)
}
"""
            print("📤 Enviando código completo...\n")
            await websocket.send(json.dumps({"code": code}))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if "status" in data:
                    print(f"📡 {data['status']}: {data.get('message', '')}")
                
                if "success" in data:
                    print("\n" + "="*70)
                    if data.get("success"):
                        print("✓ TESTE COMPLETO - SUCESSO!")
                        print("\n📊 Componentes Verificados:")
                        
                        # Verificar lexico
                        if 'lexico' in data and data['lexico']:
                            print(f"  ✓ Léxico: {len(data['lexico'])} tokens")
                        else:
                            print("  ✗ Léxico: FALHOU")
                        
                        # Verificar semantico
                        if 'semantico' in data and data['semantico']:
                            sem = data['semantico']
                            if sem.get('success'):
                                print(f"  ✓ Semântico: OK")
                            else:
                                print(f"  ✗ Semântico: {sem.get('errors', [])}")
                        else:
                            print("  ✗ Semântico: FALHOU")
                        
                        # Verificar AST
                        if 'ast' in data and data['ast']:
                            print(f"  ✓ AST: Gerada")
                        else:
                            print("  ✗ AST: FALHOU")
                        
                        # Verificar Symbol Table
                        if 'symbol_table' in data and data['symbol_table']:
                            st = data['symbol_table']
                            print(f"  ✓ Symbol Table:")
                            print(f"    - Variáveis: {len(st.get('variables', []))}")
                            print(f"    - Funções: {len(st.get('functions', []))}")
                            print(f"    - Classes: {len(st.get('classes', []))}")
                            print(f"    - Blocos: {len(st.get('blocks', []))}")
                            print(f"    - Instruções: {len(st.get('statements', []))}")
                        else:
                            print("  ✗ Symbol Table: VAZIA")
                        
                        # Verificar TAC
                        if 'tac' in data and data['tac']:
                            tac_lines = data['tac'].split('\n')
                            print(f"  ✓ TAC: {len(tac_lines)} linhas geradas")
                        else:
                            print("  ✗ TAC: NÃO GERADO")
                        
                        # Verificar saída
                        if 'saida' in data:
                            print(f"  ✓ Saída: {data['saida']}")
                        
                    else:
                        print(f"✗ ERRO: {data.get('erro', 'unknown')}")
                    print("="*70)
                    break
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full())
