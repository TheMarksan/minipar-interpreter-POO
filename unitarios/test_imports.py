"""
Script de teste para verificar se todas as dependências estão OK
Execute no Bash Console do PythonAnywhere:
    cd ~/minipar-interpreter-POO
    python3 test_imports.py
"""

import sys
import os

print("=" * 70)
print("🔍 TESTE DE IMPORTAÇÕES - MiniPar Interpreter")
print("=" * 70)

# Teste 1: Python version
print(f"\n1. Python Version: {sys.version}")

# Teste 2: Flask
try:
    import flask
    print(f"✅ Flask {flask.__version__} - OK")
except ImportError as e:
    print(f"❌ Flask - ERRO: {e}")
    print("   Solução: pip3 install --user flask")

# Teste 3: Flask-CORS
try:
    import flask_cors
    print(f"✅ Flask-CORS - OK")
except ImportError as e:
    print(f"❌ Flask-CORS - ERRO: {e}")
    print("   Solução: pip3 install --user flask-cors")

# Teste 4: Adicionar src ao path
project_path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_path, 'src')
sys.path.insert(0, project_path)
sys.path.insert(0, src_path)

print(f"\n2. Project path: {project_path}")
print(f"   Exists: {os.path.exists(project_path)}")

# Teste 5: Módulos do projeto
modules_to_test = [
    'lexer.Lexer',
    'parser.Parser',
    'semantic.SemanticAnalyzer',
    'runtime.Interpreter',
    'utils.ast_printer'
]

print("\n3. Testando módulos do projeto:")
for module_name in modules_to_test:
    try:
        parts = module_name.split('.')
        if len(parts) == 2:
            module = __import__(f'src.{parts[0]}', fromlist=[parts[1]])
            getattr(module, parts[1])
        print(f"   ✅ {module_name} - OK")
    except Exception as e:
        print(f"   ❌ {module_name} - ERRO: {e}")

# Teste 6: Importar server_pythonanywhere
print("\n4. Testando server_pythonanywhere.py:")
try:
    from server_pythonanywhere import app
    print("   ✅ server_pythonanywhere - OK")
    print(f"   ✅ Flask app criado com sucesso!")
    
    # Teste 7: Rotas
    print("\n5. Rotas disponíveis:")
    for rule in app.url_map.iter_rules():
        print(f"   • {rule.endpoint}: {rule.rule}")
    
except Exception as e:
    print(f"   ❌ ERRO ao importar: {e}")
    import traceback
    print("\n   Stack trace completo:")
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Teste concluído!")
print("=" * 70)
