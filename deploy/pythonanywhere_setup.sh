#!/bin/bash
# Script para executar NO BASH CONSOLE do PythonAnywhere
# Copie e cole estes comandos no console do PythonAnywhere

echo "🚀 Configurando MiniPar Interpreter no PythonAnywhere"
echo ""

# Descompactar arquivo
echo "📦 Descompactando arquivo..."
cd ~
mkdir -p minipar-interpreter
tar -xzf minipar-pythonanywhere.tar.gz -C minipar-interpreter
cd minipar-interpreter

# Criar virtualenv com Python 3.10 (importante para PythonAnywhere!)
echo "🐍 Criando ambiente virtual com Python 3.10..."
python3.10 -m venv venv

# Ativar virtualenv
echo "✅ Ativando ambiente virtual..."
source venv/bin/activate

# Verificar versão
echo "🔍 Verificando versão do Python..."
python --version

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup completo!"
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║          Próximos Passos                     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "1. Vá na aba 'Web'"
echo "2. Clique 'Add a new web app'"
echo "3. Escolha 'Manual configuration'"
echo "4. Python version: 3.10"
echo "5. Siga as instruções em: PYTHONANYWHERE.md"
echo ""
