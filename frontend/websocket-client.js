/**
 * Cliente WebSocket para MiniPar Interpreter
 * Conexão em tempo real com feedback de progresso
 */

class MiniParWebSocketClient {
  constructor(url = 'ws://localhost:8001') {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.messageHandlers = [];
    this.statusHandlers = [];
    this.errorHandlers = [];
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket conectado:', this.url);
          this.reconnectAttempts = 0;
          this.notifyStatus('connected', 'Conectado ao servidor');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.messageHandlers.forEach(handler => handler(data));
          } catch (e) {
            console.error('Erro ao processar mensagem:', e);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ Erro WebSocket:', error);
          this.notifyError('Erro de conexão WebSocket');
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('🔌 WebSocket desconectado');
          this.notifyStatus('disconnected', 'Desconectado');
          this.attemptReconnect();
        };
        
      } catch (error) {
        console.error('Erro ao criar WebSocket:', error);
        reject(error);
      }
    });
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Tentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.notifyStatus('reconnecting', `Reconectando... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(e => {
          console.error('Falha ao reconectar:', e);
        });
      }, this.reconnectDelay);
    } else {
      this.notifyError('Falha ao reconectar após múltiplas tentativas');
    }
  }

  send(code) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ code }));
      return true;
    } else {
      this.notifyError('WebSocket não está conectado');
      return false;
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  onStatus(handler) {
    this.statusHandlers.push(handler);
  }

  onError(handler) {
    this.errorHandlers.push(handler);
  }

  notifyStatus(status, message) {
    this.statusHandlers.forEach(handler => handler(status, message));
  }

  notifyError(error) {
    this.errorHandlers.forEach(handler => handler(error));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
  window.MiniParWebSocketClient = MiniParWebSocketClient;
}
