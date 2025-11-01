"""
WSGI Configuration for PythonAnywhere
Copie este conteúdo para o arquivo WSGI no PythonAnywhere
Caminho: /var/www/yourusername_pythonanywhere_com_wsgi.py
"""

import sys
import os
from pathlib import Path

# ===== CONFIGURAÇÃO - AJUSTE SEU USERNAME =====
USERNAME = 'm4rksan7'  
# ==============================================

# Adicionar projeto ao path
project_home = f'/home/{USERNAME}/minipar-interpreter-POO'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Adicionar src ao path
sys.path.insert(0, os.path.join(project_home, 'src'))

# Ativar virtualenv
venv_path = os.path.join(project_home, 'venv')
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')

# Criar activate_this.py se não existir (compatibilidade)
if not os.path.exists(activate_this):
    # Usar método alternativo de ativação
    import site
    site.addsitedir(os.path.join(venv_path, 'lib', 'python3.10', 'site-packages'))

# Imports do projeto
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import io
from contextlib import redirect_stdout

# Importar módulos do interpreter
from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from runtime.Interpreter import Interpreter

try:
    from codegen.TACGenerator import TACGenerator
    TAC_AVAILABLE = True
except ImportError:
    TAC_AVAILABLE = False


class WSGIHandler:
    """Handler WSGI para PythonAnywhere"""
    
    def __init__(self):
        self.frontend_dir = os.path.join(project_home, 'frontend')
    
    def serve_static(self, path):
        """Servir arquivo estático"""
        if path == '/':
            path = '/index.html'
        
        file_path = os.path.join(self.frontend_dir, path.lstrip('/'))
        
        if not os.path.exists(file_path):
            return ('404 Not Found', [('Content-Type', 'text/plain')], b'Not Found')
        
        # Detectar tipo de conteúdo
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }
        
        ext = os.path.splitext(file_path)[1]
        content_type = content_types.get(ext, 'application/octet-stream')
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return ('200 OK', [('Content-Type', content_type)], content)
    
    def handle_interpret(self, body):
        """Processar requisição de interpretação"""
        try:
            data = json.loads(body)
            code = data.get('code', '')
            
            # Lexer
            lexer = Lexer(code)
            tokens = list(lexer.tokenize())
            
            # Parser
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Semantic Analysis
            analyzer = SemanticAnalyzer()
            semantic_result = analyzer.analyze(ast)
            
            if not semantic_result['success']:
                return {
                    'erro': '\n'.join(semantic_result['errors']),
                    'semantico': semantic_result,
                    'success': False
                }
            
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
            for tok in tokens:
                tokens_list.append({
                    'type': tok.type.name if hasattr(tok.type, 'name') else str(tok.type),
                    'value': tok.lexeme,
                    'line': tok.line,
                    'column': tok.column
                })
            
            # Symbol table
            symbol_table_data = analyzer.symbol_table.to_dict() if hasattr(analyzer, 'symbol_table') else {}
            
            # TAC
            tac_text = ''
            if TAC_AVAILABLE and ast:
                try:
                    tac_gen = TACGenerator()
                    tac_gen.generate(ast)
                    tac_text = tac_gen.to_string()
                except Exception as e:
                    tac_text = f'Erro ao gerar TAC: {str(e)}'
            
            # AST serialization
            def ast_to_dict(node):
                if node is None:
                    return None
                result = {'type': node.__class__.__name__}
                for key, value in node.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [ast_to_dict(item) for item in value]
                    elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                        result[key] = ast_to_dict(value)
                    else:
                        result[key] = value
                return result
            
            return {
                'success': True,
                'saida': output,
                'lexico': tokens_list,
                'semantico': semantic_result,
                'ast': ast_to_dict(ast) if ast else None,
                'symbol_table': symbol_table_data,
                'tac': tac_text,
            }
            
        except Exception as e:
            return {
                'erro': f'Erro interno: {str(e)}',
                'success': False
            }


def application(environ, start_response):
    """WSGI application entry point"""
    
    handler = WSGIHandler()
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # CORS headers
    cors_headers = [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type'),
    ]
    
    # OPTIONS (preflight)
    if method == 'OPTIONS':
        start_response('200 OK', cors_headers)
        return [b'']
    
    # POST /interpretar
    if method == 'POST' and path == '/interpretar':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
            
            result = handler.handle_interpret(body)
            response_body = json.dumps(result, ensure_ascii=False).encode('utf-8')
            
            headers = cors_headers + [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ]
            
            start_response('200 OK', headers)
            return [response_body]
            
        except Exception as e:
            error_response = json.dumps({
                'erro': f'Erro ao processar requisição: {str(e)}',
                'success': False
            }).encode('utf-8')
            
            headers = cors_headers + [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_response)))
            ]
            
            start_response('500 Internal Server Error', headers)
            return [error_response]
    
    # GET - Servir arquivos estáticos
    if method == 'GET':
        status, headers, content = handler.serve_static(path)
        headers = headers + cors_headers
        start_response(status, headers)
        return [content]
    
    # 404
    start_response('404 Not Found', cors_headers + [('Content-Type', 'text/plain')])
    return [b'Not Found']
