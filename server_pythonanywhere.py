#!/usr/bin/env python3
"""
Servidor Flask unificado para PythonAnywhere
Serve o frontend e o backend REST API em um único servidor.

Este arquivo substitui deploy.sh quando rodando no PythonAnywhere.

Uso no PythonAnywhere:
1. Configure uma Web App
2. Aponte o WSGI file para este arquivo
3. Configure static files: /static -> /home/seu_usuario/minipar-interpreter-POO/frontend

Ou rode localmente:
  python3 server_pythonanywhere.py
"""

import sys
import os
import json
import io
from contextlib import redirect_stdout
import threading
import queue
import time
import uuid

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Importar componentes do interpretador
from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter
from utils.ast_printer import print_ast

# ============================================================================
# Configuração Flask
# ============================================================================

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Habilitar CORS para todas as rotas

# Dicionário para gerenciar sessões de input
input_sessions = {}
input_lock = threading.Lock()

# ============================================================================
# Rotas do Frontend
# ============================================================================

@app.route('/')
def index():
    """Serve a página principal"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve arquivos estáticos do frontend"""
    return send_from_directory('frontend', path)

@app.route('/tests/<path:path>')
def test_files(path):
    """Serve arquivos de teste"""
    return send_from_directory('tests', path)

# ============================================================================
# Rota do Backend - Interpretação
# ============================================================================

@app.route('/interpretar', methods=['POST', 'OPTIONS'])
def interpretar():
    """
    Endpoint principal para interpretar código MiniPar.
    
    Request JSON:
        {
            "codigo": "SEQ { print(\"Hello\"); }",
            "session_id": "opcional-para-input",
            "input_value": "opcional-valor-de-input"
        }
    
    Response JSON:
        {
            "lexico": [...tokens...],
            "semantico": {...análise...},
            "ast": "string da AST",
            "ast_json": {...AST em JSON...},
            "symbol_table": {...tabela de símbolos...},
            "saida": "output do programa",
            "erros": [...],
            "status": "success" | "error",
            "aguardando_input": true/false,
            "session_id": "id-da-sessao"
        }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        if not data or 'codigo' not in data:
            return jsonify({'error': 'Código não fornecido'}), 400
        
        codigo = data['codigo']
        session_id = data.get('session_id', str(uuid.uuid4()))
        input_value = data.get('input_value', None)
        
        # ============================================================================
        # 1. ANÁLISE LÉXICA
        # ============================================================================
        lexer = Lexer(codigo)
        tokens = lexer.tokenize()
        
        # Serializar tokens para JSON
        tokens_list = []
        for tok in tokens:
            tokens_list.append({
                'type': tok.type,
                'lexeme': tok.lexeme,
                'line': tok.line,
                'column': tok.column
            })
        
        # ============================================================================
        # 2. ANÁLISE SINTÁTICA (Parser)
        # ============================================================================
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Gerar representação textual da AST
        buf_ast = io.StringIO()
        with redirect_stdout(buf_ast):
            print_ast(ast, label='Árvore de Sintaxe Abstrata (AST)')
        ast_text = buf_ast.getvalue()
        
        # Serializar AST para JSON
        ast_json = None
        symbol_table_data = None
        
        try:
            from parser.AST import ast_to_dict
            ast_json = ast_to_dict(ast)
        except Exception as e:
            ast_json = None
        
        response = {
            'lexico': tokens_list,
            'semantico': None,
            'ast': ast_text,
            'ast_json': ast_json,
            'symbol_table': symbol_table_data,
            'saida': '',
            'erros': [],
            'status': 'success',
            'aguardando_input': False,
            'session_id': session_id
        }
        
        # ============================================================================
        # 3. ANÁLISE SEMÂNTICA
        # ============================================================================
        sa = SemanticAnalyzer()
        semantic_result = sa.analyze(ast)
        
        response['semantico'] = semantic_result
        
        if semantic_result and semantic_result.get('errors'):
            response['erros'].extend(semantic_result['errors'])
        
        # Capturar tabela de símbolos
        try:
            symbol_table_data = sa.symbol_table.to_dict() if hasattr(sa, 'symbol_table') else None
            response['symbol_table'] = symbol_table_data
        except Exception as e:
            pass
        
        # Se houver erros semânticos críticos, não executar
        if semantic_result and not semantic_result.get('success'):
            response['status'] = 'error'
            return jsonify(response), 200
        
        # ============================================================================
        # 4. INTERPRETAÇÃO/EXECUÇÃO
        # ============================================================================
        try:
            # Buffer para capturar saída do programa
            output_buffer = io.StringIO()
            
            # Queue para comunicação de input
            input_queue = queue.Queue()
            
            # Se há um valor de input pendente, colocá-lo na fila
            if input_value is not None:
                input_queue.put(input_value)
            
            # Função de callback para input
            def input_callback(prompt=None):
                # Verificar se há input na fila
                try:
                    value = input_queue.get_nowait()
                    return value
                except queue.Empty:
                    # Não há input disponível, solicitar ao frontend
                    raise InterruptedError("INPUT_REQUIRED")
            
            # Criar interpretador
            interpreter = Interpreter(output_stream=output_buffer, input_callback=input_callback)
            
            # Executar programa
            try:
                with redirect_stdout(output_buffer):
                    interpreter.interpret(ast)
                
                response['saida'] = output_buffer.getvalue()
                response['status'] = 'success'
                
            except InterruptedError as ie:
                if str(ie) == "INPUT_REQUIRED":
                    # Programa aguardando input
                    response['saida'] = output_buffer.getvalue()
                    response['aguardando_input'] = True
                    response['status'] = 'waiting_input'
                    
                    # Armazenar estado da sessão
                    with input_lock:
                        input_sessions[session_id] = {
                            'interpreter': interpreter,
                            'output_buffer': output_buffer,
                            'ast': ast
                        }
                else:
                    raise
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            response['erros'].append(f"Erro na execução: {str(e)}")
            response['erros'].append(f"Traceback: {error_trace}")
            response['status'] = 'error'
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            'error': f'Erro no servidor: {str(e)}',
            'traceback': error_trace,
            'status': 'error'
        }), 500

# ============================================================================
# Rota de Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'MiniPar Interpreter',
        'version': '2.0'
    })

# ============================================================================
# Execução Local (desenvolvimento)
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Servidor Flask para MiniPar Interpreter')
    parser.add_argument('--host', default='0.0.0.0', help='Host para bind (padrão: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Porta (padrão: 5000)')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 MiniPar Interpreter - Servidor Flask")
    print("=" * 60)
    print(f"📡 Servidor rodando em: http://{args.host}:{args.port}")
    print(f"🌐 Acesse: http://localhost:{args.port}")
    print("=" * 60)
    
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)

# ============================================================================
# Para PythonAnywhere WSGI
# ============================================================================
# No arquivo WSGI do PythonAnywhere, adicione:
#
# import sys
# path = '/home/seu_usuario/minipar-interpreter-POO'
# if path not in sys.path:
#     sys.path.insert(0, path)
#
# from server_pythonanywhere import app as application
# ============================================================================
