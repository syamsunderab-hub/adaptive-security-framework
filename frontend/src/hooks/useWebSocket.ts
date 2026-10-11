import { useState, useEffect } from "react";
import { wsClient } from "../services/websocket";

export function useWebSocket() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    wsClient.connect();
    const unsub = wsClient.onStatusChange(setConnected);
    return () => unsub();
  }, []);

  return { connected, wsClient };
}
