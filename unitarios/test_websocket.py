#!/usr/bin/env python3
"""Script de teste do WebSocket"""
import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect("ws://localhost:8001") as websocket:
            code = """
SEQ {
    print("Hello WebSocket!")
}
"""
            await websocket.send(json.dumps({"code": code}))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if "status" in data:
                    print(f"📡 Status: {data['status']}")
                
                if "success" in data:
                    if data.get("success"):
                        print("✓ WebSocket funcionando perfeitamente!")
                        print(f"📤 Saída: {data.get('saida', '')}")
                    else:
                        print(f"✗ Erro: {data.get('erro', 'unknown')}")
                    break
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")

if __name__ == "__main__":
    asyncio.run(test())
