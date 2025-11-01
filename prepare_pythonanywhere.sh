#!/bin/bash
# Script para preparar deploy no PythonAnywhere

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   Preparar Deploy PythonAnywhere            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Criar arquivo tar.gz sem arquivos desnecessários
echo "📦 Criando arquivo minipar-pythonanywhere.tar.gz..."
echo ""

# Excluir arquivos desnecessários
tar -czf minipar-pythonanywhere.tar.gz \
    --exclude='minipar-pythonanywhere.tar.gz' \
    --exclude='minipar-pythonanywhere.zip' \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.log' \
    --exclude='*.pid' \
    --exclude='nohup.out' \
    --exclude='test_*.py' \
    . 2>/dev/null

echo ""
echo "✅ Arquivo criado: minipar-pythonanywhere.tar.gz"
echo ""

# Mostrar tamanho
SIZE=$(du -h minipar-pythonanywhere.tar.gz | cut -f1)
echo "📊 Tamanho: $SIZE"
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║          Próximos Passos                     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "1. Acesse: https://www.pythonanywhere.com"
echo "2. Crie conta gratuita (ou faça login)"
echo "3. Vá em 'Files' → Upload a file"
echo "4. Faça upload de: minipar-pythonanywhere.tar.gz"
echo "5. Abra um 'Bash console'"
echo "6. Execute: tar -xzf minipar-pythonanywhere.tar.gz -C minipar-interpreter"
echo "7. Siga os passos em: PYTHONANYWHERE.md"
echo ""
echo "📚 Guia completo: PYTHONANYWHERE.md"
echo ""
