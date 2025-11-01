#!/usr/bin/env python3
"""Servidor HTTP mínimo para atender a rota /interpretar usada pelo frontend.

Não requer FastAPI. Usa a Lexer/Parser/SemanticAnalyzer do projeto para
retornar tokens, relatório semântico e uma representação em texto da AST.

Uso:
  python3 scripts/interpret_server.py [--host HOST] [--port PORT]

Exemplo:
  python3 scripts/interpret_server.py --host 127.0.0.1 --port 8000

Resposta JSON:
  {
    "lexico": [ {"type": "IDENT", "lexeme": "var"}, ... ],
    "semantico": { ... },
    "ast": "<string representation>"
  }
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import argparse
import io
import threading
import queue
import time
import uuid

# Active runs registry: run_id -> run state dict
RUNS = {}


HERE = os.path.dirname(os.path.dirname(__file__))
# Ensure 'src' is on sys.path so imports like `from lexer.Lexer import Lexer` work
SRC_PATH = os.path.join(HERE, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer
from utils.ast_printer import print_ast
from runtime.Interpreter import Interpreter
from codegen.TACGenerator import TACGenerator
from contextlib import redirect_stdout


class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        # Allow CORS from localhost (frontend served on a different port)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        # route: start interpretation
        if parsed.path == '/interpretar':
            pass
        elif parsed.path == '/interpretar/input':
            # POST to supply input for a running interpretation
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            run_id = data.get('run_id')
            supplied = data.get('input', '')
            if not run_id or run_id not in RUNS:
                self._set_headers(400)
                self.wfile.write(json.dumps({'erro': 'run_id inválido ou execução não encontrada'}).encode())
                return

            run = RUNS[run_id]
            # Put the supplied input into the run's queue so interpreter can resume
            run['queue'].put(supplied)

            # Wait a little bit for the interpreter to proceed and update buffer/state
            time.sleep(0.05)

            resp = {
                'run_id': run_id,
                'exec': run['buf'].getvalue(),
                'waiting_for_input': run['waiting'],
                'prompt': run.get('prompt'),
                'finished': run['finished'],
                'error': run.get('error')
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'erro': 'Rota não encontrada'}).encode())
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        code = data.get('code') or data.get('codigo') or ''

        # Run lexer
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            lex_out = []
            has_error = False
            error_messages = []
            
            for t in tokens:
                ttype = getattr(t.type, 'name', str(t.type))
                lex_out.append({'type': ttype, 'lexeme': t.lexeme, 'line': t.line})
                
                # Verificar se há token de erro
                if ttype == 'ERROR':
                    has_error = True
                    error_messages.append(t.lexeme)
            
            # Se há erro léxico, retornar imediatamente com mensagem clara
            if has_error:
                self._set_headers(400)
                error_text = '\n'.join(error_messages)
                self.wfile.write(json.dumps({'erro': error_text, 'lexico': lex_out}).encode())
                return
                
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'erro': f'Erro no lexer: {e}'}).encode())
            return

        # Parse to AST
        try:
            parser = Parser(tokens)
            ast = parser.parse()
            # print AST to string by capturing stdout from print_ast
            try:
                buf_ast = io.StringIO()
                with redirect_stdout(buf_ast):
                    print_ast(ast, label='Árvore de Sintaxe Abstrata (AST)')
                ast_text = buf_ast.getvalue()
            except Exception:
                # fallback: simple summary of top-level node types
                try:
                    ast_summary_lines = [type(child).__name__ for child in ast.children]
                    ast_text = '\n'.join(ast_summary_lines)
                except Exception as e:
                    ast_text = f'Erro ao gerar AST: {e}'
        except Exception as e:
            ast = None
            ast_text = f'Erro ao gerar AST: {e}'

        # Semantic analysis (best-effort)
        try:
            sa = SemanticAnalyzer()
            sem_res = sa.analyze(ast) if ast is not None else {'success': False, 'errors': ['AST inválida']}
        except Exception as e:
            sem_res = {'success': False, 'errors': [f'Erro semântico: {e}']}

        response = {
            'lexico': lex_out,
            'semantico': sem_res,
            'ast': ast_text
        }

        # Attempt to generate TAC (three-address code) from the AST if available
        try:
            if ast is not None:
                tac_gen = TACGenerator()
                tac_gen.generate(ast)
                tac_text = tac_gen.to_string()
                response['tac'] = tac_text
                # debug helpers
                response['tac_len'] = len(tac_text)
                response['tac_generated'] = True if tac_text else False
                print(f"[TAC] Generated length={len(tac_text)}")
            else:
                response['tac'] = ''
                response['tac_len'] = 0
                response['tac_generated'] = False
        except Exception as e:
            response['tac'] = f'Erro ao gerar TAC: {e}'
            response['tac_len'] = 0
            response['tac_generated'] = False
            print(f"[TAC] Error generating TAC: {e}")

        # Try to execute the AST using the Interpreter and capture stdout.
        # To support interactive `input()` we run execution in a background thread
        # and expose a small run registry (RUNS) where the frontend can POST input
        
        # NÃO EXECUTAR SE HOUVER ERROS SEMÂNTICOS
        if not sem_res.get('success', False) or sem_res.get('errors'):
            response['run_id'] = None
            response['exec'] = ''
            response['execucao'] = '# Execução não realizada devido a erros semânticos'
            response['stdout'] = ''
            response['waiting_for_input'] = False
            response['prompt'] = None
            
            self._set_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        try:
            interp = Interpreter()

            run_id = uuid.uuid4().hex
            run = {
                'id': run_id,
                'interp': interp,
                'queue': queue.Queue(),
                'buf': io.StringIO(),
                'waiting': False,
                'prompt': None,
                'finished': False,
                'error': None,
            }

            # input provider that the Interpreter will call
            def run_input_provider(prompt):
                run['waiting'] = True
                run['prompt'] = prompt
                # block until frontend supplies input via /interpretar/input
                try:
                    val = run['queue'].get()
                except Exception:
                    val = ''
                run['waiting'] = False
                run['prompt'] = None
                return val

            interp.input_provider = run_input_provider

            def runner():
                try:
                    with redirect_stdout(run['buf']):
                        interp.interpret(ast)
                except Exception as e:
                    try:
                        run['buf'].write(f"\n[Erro na execução]: {e}\n")
                    except Exception:
                        pass
                    run['error'] = str(e)
                finally:
                    run['finished'] = True

            th = threading.Thread(target=runner, daemon=True)
            run['thread'] = th
            RUNS[run_id] = run
            th.start()

            # Give the interpreter a tiny moment to start and possibly request input
            time.sleep(0.02)

            # Prepare response: include run_id and current buffered output, and whether it is waiting for input
            response['run_id'] = run_id
            response['exec'] = run['buf'].getvalue()
            response['execucao'] = response['exec']
            response['stdout'] = response['exec']
            response['waiting_for_input'] = run['waiting']
            response['prompt'] = run['prompt']

        except Exception as e:
            # If interpreter import/instantiation fails, still return what we have
            response['exec'] = f'[Execução não disponível: {e}]'
            response['execucao'] = response['exec']
            response['stdout'] = response['exec']

        self._set_headers(200)
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    addr = (args.host, args.port)
    print(f'Serving HTTP on {args.host}:{args.port} ...')
    httpd = HTTPServer(addr, SimpleHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        httpd.server_close()


if __name__ == '__main__':
    main()
