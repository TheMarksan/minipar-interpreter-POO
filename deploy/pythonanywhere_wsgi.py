"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  WSGI Configuration for PythonAnywhere                       ║
║                      MiniPar Interpreter - v2.0                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTRUÇÕES:
1. No PythonAnywhere, vá em Web > WSGI configuration file
2. APAGUE todo o conteúdo do arquivo
3. COLE este arquivo COMPLETO
4. Clique em SAVE
5. Clique em RELOAD m4rksan7.pythonanywhere.com

"""

import sys
import os

# ============================================================================
# CONFIGURAÇÃO DO CAMINHO
# ============================================================================

# Username do PythonAnywhere
USERNAME = 'm4rksan7'

# Caminho completo do projeto
project_path = f'/home/{USERNAME}/minipar-interpreter-POO'

# ============================================================================
# DEBUG - Verificações Iniciais
# ============================================================================

print("=" * 70)
print("🔍 MINIPAR INTERPRETER - WSGI INITIALIZATION")
print("=" * 70)
print(f"📂 Project path: {project_path}")
print(f"✅ Path exists: {os.path.exists(project_path)}")

# Verificar arquivo server_pythonanywhere.py
server_file = os.path.join(project_path, 'server_pythonanywhere.py')
print(f"📄 server_pythonanywhere.py exists: {os.path.exists(server_file)}")

# Adicionar ao sys.path
if project_path not in sys.path:
    sys.path.insert(0, project_path)
    print(f"✅ Added to sys.path")

# Adicionar src ao path (para imports internos)
src_path = os.path.join(project_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"✅ Added src to sys.path")

# ============================================================================
# IMPORTAR A APLICAÇÃO FLASK
# ============================================================================

# Verificar Flask
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError:
    print("❌ Flask not installed! Run: pip3 install --user flask flask-cors")
    raise

try:
    import flask_cors
    print(f"✅ Flask-CORS installed")
except ImportError:
    print("⚠️  Flask-CORS not installed (optional)")

# Importar a aplicação
try:
    print("⏳ Importing server_pythonanywhere...")
    from server_pythonanywhere import app as application
    print("✅ SUCCESS! MiniPar Interpreter loaded!")
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print(f"   File exists: {os.path.exists(server_file)}")
    print(f"   sys.path: {sys.path[:3]}")
    print("=" * 70)
    
    # Criar aplicação de erro para debug
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MiniPar - Erro de Configuração</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #e74c3c; }}
                code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .check {{ color: #27ae60; }}
                .cross {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Erro ao Carregar MiniPar Interpreter</h1>
                
                <h2>Erro Encontrado:</h2>
                <pre>{str(e)}</pre>
                
                <h2>📋 Checklist de Verificação:</h2>
                <ul>
                    <li><span class="{'check' if os.path.exists(project_path) else 'cross'}">
                        {'✅' if os.path.exists(project_path) else '❌'}
                    </span> Projeto existe em: <code>{project_path}</code></li>
                    
                    <li><span class="{'check' if os.path.exists(server_file) else 'cross'}">
                        {'✅' if os.path.exists(server_file) else '❌'}
                    </span> Arquivo <code>server_pythonanywhere.py</code> existe</li>
                    
                    <li>Flask instalado? Execute: <code>pip3 install --user flask flask-cors</code></li>
                </ul>
                
                <h2>🔧 Como Resolver:</h2>
                <ol>
                    <li><strong>No Bash Console do PythonAnywhere:</strong></li>
                    <pre>cd ~/minipar-interpreter-POO
pip3 install --user flask flask-cors
ls -la server_pythonanywhere.py</pre>
                    
                    <li><strong>Se o arquivo não existir:</strong></li>
                    <pre>git pull origin main</pre>
                    
                    <li><strong>Depois recarregue:</strong> Web > Reload m4rksan7.pythonanywhere.com</li>
                </ol>
                
                <h2>📊 Informações de Debug:</h2>
                <pre>Project Path: {project_path}
Server File: {server_file}
File Exists: {os.path.exists(server_file)}
Python Version: {sys.version}
sys.path (first 3): {sys.path[:3]}</pre>
                
                <hr>
                <p><small>Error.log: <code>/var/log/m4rksan7.pythonanywhere.com.error.log</code></small></p>
            </div>
        </body>
        </html>
        """
    
    @application.route('/health')
    def health():
        return {{'status': 'error', 'message': str(e)}}

except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("=" * 70)
    raise

# ============================================================================
# FIM DO WSGI
# ============================================================================
# O PythonAnywhere usa automaticamente a variável 'application'
# Não adicione mais código abaixo!
# ============================================================================
