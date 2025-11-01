#!/bin/bash

# ============================================================================
# Test Local - Servidor Flask para PythonAnywhere
# ============================================================================
# Este script testa o servidor Flask localmente antes de fazer deploy
# ============================================================================

echo "╔══════════════════════════════════════════════╗"
echo "║   MiniPar - Teste Servidor Flask            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Verificar se Flask está instalado
echo "🔍 Verificando dependências..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask não instalado!"
    echo "📦 Instalando Flask e Flask-CORS..."
    pip3 install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências"
        exit 1
    fi
fi

python3 -c "import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando Flask-CORS..."
    pip3 install flask-cors
fi

echo "✅ Dependências OK"
echo ""

# Verificar se o arquivo do servidor existe
if [ ! -f "server_pythonanywhere.py" ]; then
    echo "❌ Arquivo server_pythonanywhere.py não encontrado!"
    exit 1
fi

echo "🚀 Iniciando servidor Flask..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📡 Servidor: http://localhost:5000"
echo "  🌐 Interface: http://localhost:5000"
echo "  🔗 API: http://localhost:5000/interpretar"
echo "  ❤️  Health: http://localhost:5000/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏹️  Para parar: Ctrl+C"
echo ""

# Iniciar servidor
python3 server_pythonanywhere.py --host 0.0.0.0 --port 5000
