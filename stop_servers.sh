#!/bin/bash
# Script para parar os servidores MiniPar Interpreter

echo "╔══════════════════════════════════════════════╗"
echo "║   MiniPar Interpreter - Stop Servers        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Função para parar um servidor
stop_server() {
    local name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null
            sleep 1
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null
            fi
            echo -e "${GREEN}✓${NC} $name parado (PID: $PID)"
        else
            echo -e "${RED}⚠${NC} $name não estava rodando"
        fi
        rm -f "$pidfile"
    else
        echo -e "${RED}⚠${NC} $name: PID file não encontrado"
    fi
}

# Parar servidores usando PIDs salvos
if [ -d "logs" ]; then
    stop_server "HTTP Server" "logs/http.pid"
    stop_server "REST API" "logs/rest.pid"
    stop_server "WebSocket" "logs/websocket.pid"
fi

# Garantir que todos foram parados (por nome do processo)
echo ""
echo "🔍 Verificando processos remanescentes..."
pkill -f "interpret_server.py" 2>/dev/null && echo "  • interpret_server.py finalizado"
pkill -f "server_websocket.py" 2>/dev/null && echo "  • server_websocket.py finalizado"
pkill -f "python.*http.server.*8080" 2>/dev/null && echo "  • HTTP server (8080) finalizado"

echo ""
echo -e "${GREEN}✅ Todos os servidores foram parados!${NC}"
echo ""
