#!/bin/bash
# Script de Deploy para MiniPar Interpreter

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   MiniPar Interpreter - Deploy Script       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se está no diretório correto
if [ ! -f "README.md" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Configurar ambiente virtual
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Ambiente virtual criado"
fi

# Ativar ambiente virtual
source venv/bin/activate

echo -e "${BLUE}📦 Instalando dependências...${NC}"
pip install -q -r requirements.txt || {
    echo "⚠️  Aviso: Algumas dependências podem já estar instaladas"
}

echo -e "${GREEN}✓${NC} Dependências instaladas"
echo ""

# Criar diretório de logs
mkdir -p logs

# Parar servidores existentes
echo -e "${BLUE}🔄 Parando servidores existentes...${NC}"
pkill -f "interpret_server.py" 2>/dev/null || true
pkill -f "server_websocket.py" 2>/dev/null || true
pkill -f "python.*http.server.*8080" 2>/dev/null || true
sleep 1
echo -e "${GREEN}✓${NC} Servidores anteriores encerrados"
echo ""

# Iniciar servidor HTTP (frontend)
echo -e "${BLUE}🌐 Iniciando servidor HTTP (frontend)...${NC}"
nohup python -m http.server 8080 --bind 0.0.0.0 --directory frontend > logs/http.log 2>&1 &
HTTP_PID=$!
echo -e "${GREEN}✓${NC} Servidor HTTP iniciado (PID: $HTTP_PID)"
echo "   📁 Frontend: http://0.0.0.0:8080"
echo ""

# Iniciar servidor REST API
echo -e "${BLUE}🔌 Iniciando servidor REST API...${NC}"
nohup python scripts/interpret_server.py --host 0.0.0.0 --port 8000 > logs/rest.log 2>&1 &
REST_PID=$!
echo -e "${GREEN}✓${NC} Servidor REST iniciado (PID: $REST_PID)"
echo "   🔗 API REST: http://0.0.0.0:8000"
echo ""

# Iniciar servidor WebSocket
echo -e "${BLUE}⚡ Iniciando servidor WebSocket...${NC}"
nohup python server_websocket.py > logs/websocket.log 2>&1 &
WS_PID=$!
echo -e "${GREEN}✓${NC} Servidor WebSocket iniciado (PID: $WS_PID)"
echo "   📡 WebSocket: ws://0.0.0.0:8001"
echo ""

# Salvar PIDs
echo "$HTTP_PID" > logs/http.pid
echo "$REST_PID" > logs/rest.pid
echo "$WS_PID" > logs/websocket.pid

# Aguardar inicialização
echo -e "${BLUE}⏳ Aguardando inicialização dos servidores...${NC}"
sleep 3

# Verificar se os servidores estão rodando
RUNNING=0
if ps -p $HTTP_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} HTTP Server: Rodando"
    RUNNING=$((RUNNING + 1))
else
    echo -e "${YELLOW}⚠${NC} HTTP Server: Falhou ao iniciar (verifique logs/http.log)"
fi

if ps -p $REST_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} REST API: Rodando"
    RUNNING=$((RUNNING + 1))
else
    echo -e "${YELLOW}⚠${NC} REST API: Falhou ao iniciar (verifique logs/rest.log)"
fi

if ps -p $WS_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} WebSocket: Rodando"
    RUNNING=$((RUNNING + 1))
else
    echo -e "${YELLOW}⚠${NC} WebSocket: Falhou ao iniciar (verifique logs/websocket.log)"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           🚀 Deploy Concluído!               ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Servidores ativos: $RUNNING/3${NC}"
echo ""
echo "📊 URLs de Acesso:"
echo "   🌐 Frontend:"
echo "      • Local:  http://localhost:8080"
echo "      • Rede:   http://<SEU_IP>:8080"
echo "   🔗 REST API:"
echo "      • Local:  http://localhost:8000"
echo "      • Rede:   http://<SEU_IP>:8000"
echo "   📡 WebSocket:"
echo "      • Local:  ws://localhost:8001"
echo "      • Rede:   ws://<SEU_IP>:8001"
echo ""
echo "💡 Para descobrir seu IP local, execute: hostname -I | awk '{print \$1}'"
echo ""
echo "📝 Logs:"
echo "   tail -f logs/http.log"
echo "   tail -f logs/rest.log"
echo "   tail -f logs/websocket.log"
echo ""
echo "⏹️  Para parar os servidores:"
echo "   ./stop_servers.sh"
echo ""
