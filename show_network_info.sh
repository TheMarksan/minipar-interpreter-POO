#!/bin/bash
# Script para mostrar informações de rede do deploy

echo "╔══════════════════════════════════════════════╗"
echo "║   MiniPar - Informações de Acesso na Rede   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Detectar IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Não foi possível detectar o IP local"
    echo "💡 Execute manualmente: ip addr show ou ifconfig"
    exit 1
fi

echo "🖥️  IP Local: $LOCAL_IP"
echo ""
echo "📊 URLs de Acesso na Rede:"
echo ""
echo "   🌐 Frontend (Interface Web):"
echo "      http://$LOCAL_IP:8080"
echo ""
echo "   🔗 REST API (Backend):"
echo "      http://$LOCAL_IP:8000"
echo ""
echo "   📡 WebSocket (Comunicação em Tempo Real):"
echo "      ws://$LOCAL_IP:8001"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Para acessar de outros dispositivos:"
echo "   1. Certifique-se que estão na mesma rede (WiFi/LAN)"
echo "   2. Abra o navegador e acesse: http://$LOCAL_IP:8080"
echo "   3. Verifique se o firewall permite conexões nas portas 8000, 8001 e 8080"
echo ""
echo "🔥 Comandos para liberar portas no firewall (se necessário):"
echo "   sudo ufw allow 8080/tcp"
echo "   sudo ufw allow 8000/tcp"
echo "   sudo ufw allow 8001/tcp"
echo ""
echo "🔍 Verificar status dos servidores:"
echo "   ps aux | grep -E 'python.*8080|python.*8000|python.*8001'"
echo ""
