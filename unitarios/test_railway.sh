#!/bin/bash
# Testar servidor unificado localmente

echo "🧪 Testando railway_start.py localmente..."
echo ""

# Exportar variável para modo simples
export DEPLOY_MODE=simple
export PORT=9000

echo "📡 Iniciando servidor em http://localhost:9000"
echo "⚠️  Use CTRL+C para parar"
echo ""

python3 railway_start.py
