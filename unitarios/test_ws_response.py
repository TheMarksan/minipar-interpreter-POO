#!/usr/bin/env python3
"""Script para testar resposta completa do WebSocket"""
import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect("ws://localhost:8001") as websocket:
            code = """
SEQ {
    int x
    x = 10
    print(x)
}
"""
            print("📤 Enviando código...\n")
            await websocket.send(json.dumps({"code": code}))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if "status" in data:
                    print(f"📡 Status: {data['status']}")
                
                if "success" in data:
                    print("\n" + "="*60)
                    if data.get("success"):
                        print("✓ SUCESSO!")
                        print("\n📊 Dados recebidos:")
                        for key in data.keys():
                            if key == 'success':
                                continue
                            value = data[key]
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                print(f"  • {key}: {type(value).__name__} (tamanho: {len(value) if isinstance(value, (list, dict)) else 'N/A'})")
                            else:
                                print(f"  • {key}: {value}")
                        
                        # Verificar especificamente TAC e symbol_table
                        print("\n🔍 Verificações específicas:")
                        print(f"  • TAC presente: {'tac' in data or 'tac_code' in data}")
                        print(f"  • Symbol Table presente: {'symbol_table' in data}")
                        
                        if 'symbol_table' in data:
                            st = data['symbol_table']
                            print(f"    - Tipo: {type(st).__name__}")
                            if isinstance(st, dict):
                                print(f"    - Chaves: {list(st.keys())}")
                        
                    else:
                        print(f"✗ ERRO: {data.get('erro', 'unknown')}")
                    print("="*60)
                    break
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
