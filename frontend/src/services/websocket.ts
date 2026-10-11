type MessageHandler = (data: any) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private listeners: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: any = null;
  private isConnected = false;
  private onStatusChangeCallbacks: Set<(connected: boolean) => void> = new Set();

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        this.notifyStatus(true);
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const type = payload.type;
          const data = payload.data;

          if (this.listeners.has(type)) {
            this.listeners.get(type)!.forEach((handler) => handler(data));
          }
          if (this.listeners.has("*")) {
            this.listeners.get("*")!.forEach((handler) => handler(payload));
          }
        } catch (err) {
          console.error("Failed to parse WS payload:", err);
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.notifyStatus(false);
        this.scheduleReconnect();
      };

      this.socket.onerror = () => {
        this.isConnected = false;
        this.notifyStatus(false);
      };
    } catch (e) {
      console.error("WS connection error:", e);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (!this.reconnectTimer) {
      this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null;
        this.connect();
      }, 2000);
    }
  }

  subscribe(eventType: string, handler: MessageHandler) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(handler);

    return () => {
      this.listeners.get(eventType)?.delete(handler);
    };
  }

  onStatusChange(cb: (connected: boolean) => void) {
    this.onStatusChangeCallbacks.add(cb);
    cb(this.isConnected);
    return () => {
      this.onStatusChangeCallbacks.delete(cb);
    };
  }

  private notifyStatus(status: boolean) {
    this.onStatusChangeCallbacks.forEach((cb) => cb(status));
  }

  send(data: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    }
  }
}

export const wsClient = new WebSocketClient();
