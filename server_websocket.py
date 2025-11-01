#!/usr/bin/env python3
"""
Servidor WebSocket para MiniPar Interpreter
Suporta comunicação em tempo real para execução de código
"""

import asyncio
import json
import sys
import os
import io
from contextlib import redirect_stdout
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("ERRO: websockets não está instalado. Execute: pip install websockets")
    sys.exit(1)

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

try:
    from codegen.TACGenerator import TACGenerator
    TAC_AVAILABLE = True
except ImportError:
    TAC_AVAILABLE = False
    print("⚠️ TACGenerator não disponível")


async def handle_interpret(websocket, path):
    """Handler para mensagens WebSocket"""
    print(f"Nova conexão: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                code = data.get('code', '')
                
                if not code:
                    await websocket.send(json.dumps({
                        'erro': 'Código não fornecido',
                        'success': False
                    }))
                    continue
                
                # Enviar status de início
                await websocket.send(json.dumps({
                    'status': 'processing',
                    'message': 'Analisando código...'
                }))
                
                # Lexer
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                
                # Parser
                parser = Parser(tokens)
                ast = parser.parse()
                
                await websocket.send(json.dumps({
                    'status': 'processing',
                    'message': 'Análise semântica...'
                }))
                
                # Análise Semântica
                analyzer = SemanticAnalyzer()
                semantic_result = analyzer.analyze(ast)
                
                if not semantic_result['success']:
                    await websocket.send(json.dumps({
                        'erro': '\n'.join(semantic_result['errors']),
                        'semantico': semantic_result,
                        'success': False
                    }))
                    continue
                
                await websocket.send(json.dumps({
                    'status': 'processing',
                    'message': 'Executando...'
                }))
                
                # Interpreter - Capturar stdout
                interpreter = Interpreter()
                output_buffer = io.StringIO()
                
                try:
                    with redirect_stdout(output_buffer):
                        interpreter.interpret(ast)
                    output = output_buffer.getvalue()
                except Exception as e:
                    output = f"[Erro na execução]: {e}"
                finally:
                    output_buffer.close()
                
                # Serializar tokens
                tokens_list = []
                lexer2 = Lexer(code)
                for tok in lexer2.tokenize():
                    tokens_list.append({
                        'type': tok.type.name if hasattr(tok.type, 'name') else str(tok.type),
                        'value': tok.lexeme,
                        'line': tok.line,
                        'column': tok.column
                    })
                
                # Obter symbol table
                symbol_table_data = analyzer.symbol_table.to_dict() if hasattr(analyzer, 'symbol_table') else {}
                
                # Gerar TAC (Three-Address Code)
                tac_text = ''
                if TAC_AVAILABLE and ast:
                    try:
                        tac_gen = TACGenerator()
                        tac_gen.generate(ast)
                        tac_text = tac_gen.to_string()
                    except Exception as e:
                        print(f"⚠️ Erro ao gerar TAC: {e}")
                        tac_text = f'Erro ao gerar TAC: {str(e)}'
                
                # Resposta de sucesso
                response = {
                    'success': True,
                    'saida': output,
                    'lexico': tokens_list,
                    'semantico': semantic_result,
                    'ast': ast_to_dict(ast) if ast else None,
                    'symbol_table': symbol_table_data,
                    'tac': tac_text,
                }
                
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'erro': 'JSON inválido',
                    'success': False
                }))
            except Exception as e:
                print(f"Erro ao processar: {e}")
                import traceback
                traceback.print_exc()
                await websocket.send(json.dumps({
                    'erro': f'Erro interno: {str(e)}',
                    'success': False
                }))
    
    except websockets.exceptions.ConnectionClosed:
        print(f"Conexão fechada: {websocket.remote_address}")


def ast_to_dict(node):
    """Converte AST para dicionário serializável"""
    if node is None:
        return None
    
    result = {
        'type': node.__class__.__name__,
    }
    
    # Adicionar atributos relevantes
    if hasattr(node, '__dict__'):
        for key, value in node.__dict__.items():
            if key.startswith('_'):
                continue
            
            if isinstance(value, list):
                result[key] = [ast_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
            elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                result[key] = ast_to_dict(value)
            else:
                result[key] = value
    
    return result


async def main():
    """Inicia o servidor WebSocket"""
    host = os.getenv('WS_HOST', '0.0.0.0')
    port = int(os.getenv('WS_PORT', 8001))
    
    print(f"""
╔══════════════════════════════════════════════╗
║   MiniPar Interpreter - WebSocket Server    ║
╚══════════════════════════════════════════════╝

🚀 Servidor WebSocket iniciado
📡 Host: {host}
🔌 Porta: {port}
🌐 URL: ws://{host}:{port}

⌨️  Pressione CTRL+C para parar
""")
    
    async with serve(handle_interpret, host, port):
        await asyncio.Future()  # Run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Servidor encerrado com sucesso!")
