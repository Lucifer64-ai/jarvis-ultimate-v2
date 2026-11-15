export default class WebSocketService {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.onConnect = null;
    this.onDisconnect = null;
    this.onMessage = null;
    this.onError = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket подключен');
          this.reconnectAttempts = 0;
          if (this.onConnect) this.onConnect();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (this.onMessage) this.onMessage(data);
          } catch (e) {
            console.error('Ошибка парсинга сообщения:', e);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket отключен');
          if (this.onDisconnect) this.onDisconnect();
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket ошибка:', error);
          if (this.onError) this.onError(error);
          reject(error);
        };
      } catch (e) {
        reject(e);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket не подключен');
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => {
        this.connect().catch(() => {});
      }, this.reconnectDelay);
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}
