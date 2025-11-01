"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WSGI Configuration File                                   ║
║                    Para PythonAnywhere                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Este arquivo deve ser configurado no PythonAnywhere Web App.

INSTRUÇÕES:
1. Vá em "Web" no dashboard do PythonAnywhere
2. Clique no link "WSGI configuration file"
3. Apague TODO o conteúdo
4. Cole este arquivo COMPLETO
5. Substitua "SEU_USUARIO" pelo seu username do PythonAnywhere
6. Clique em "Save"
7. Clique em "Reload SEU_USUARIO.pythonanywhere.com"

EXEMPLO:
Se seu username é "joaosilva", o caminho será:
path = '/home/joaosilva/minipar-interpreter-POO'

"""

import sys
import os

# ============================================================================
# CONFIGURAÇÃO DO PATH
# ============================================================================
# ⚠️ ATENÇÃO: Substitua "SEU_USUARIO" pelo seu username do PythonAnywhere!
# ============================================================================

# Caminho do projeto
path = '/home/SEU_USUARIO/minipar-interpreter-POO'

# Adicionar ao sys.path se ainda não estiver
if path not in sys.path:
    sys.path.insert(0, path)

# ============================================================================
# IMPORTAR A APLICAÇÃO FLASK
# ============================================================================

try:
    from server_pythonanywhere import app as application
    
    # Log de sucesso (aparece no error.log)
    print("✅ MiniPar Interpreter carregado com sucesso!")
    print(f"📂 Projeto em: {path}")
    
except Exception as e:
    # Se houver erro na importação, registrar no log
    print(f"❌ ERRO ao carregar MiniPar Interpreter:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Criar uma aplicação Flask básica para mostrar o erro
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return f"""
        <html>
        <head><title>Erro - MiniPar Interpreter</title></head>
        <body>
            <h1>❌ Erro ao Carregar Aplicação</h1>
            <p><strong>Erro:</strong> {str(e)}</p>
            <p>Verifique o error.log para mais detalhes.</p>
            <hr>
            <h2>Checklist de Verificação:</h2>
            <ul>
                <li>✅ Flask instalado? (<code>pip3 install --user flask flask-cors</code>)</li>
                <li>✅ Caminho correto no WSGI? (substitua SEU_USUARIO)</li>
                <li>✅ Projeto existe em: <code>{path}</code>?</li>
                <li>✅ Arquivo <code>server_pythonanywhere.py</code> existe?</li>
            </ul>
        </body>
        </html>
        """, 500

# ============================================================================
# CONFIGURAÇÕES ADICIONAIS (Opcional)
# ============================================================================

# Se quiser adicionar logging customizado:
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ============================================================================
# FIM DA CONFIGURAÇÃO
# ============================================================================
# Não precisa adicionar mais nada aqui!
# O PythonAnywhere vai usar a variável "application" automaticamente.
# ============================================================================
