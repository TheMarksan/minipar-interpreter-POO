#!/bin/bash
# Script para atualizar versão do cache dos arquivos frontend

set -e

GREEN='\033[0;32m'
NC='\033[0m'

NEW_VERSION="2025.11.01.$(date +%H%M)"

echo "🔄 Atualizando versão do cache para: $NEW_VERSION"

# Atualizar versões no HTML
sed -i "s/v=[0-9.]\+/v=$NEW_VERSION/g" frontend/index.html

echo -e "${GREEN}✓${NC} Versões atualizadas!"
echo "   Nova versão: $NEW_VERSION"
echo ""
echo "💡 Recarregue o navegador (CTRL+SHIFT+R) para ver as mudanças"
