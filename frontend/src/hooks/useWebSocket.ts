import { useEffect, useRef, useState } from 'react';
import { ConnectionStatus, WebSocketMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useWebSocket({ url, onMessage, onError }: UseWebSocketOptions) {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    wsRef.current = new WebSocket(url);

    wsRef.current.onopen = () => {
      console.log('Connected to WebSocket server');
      setConnectionStatus('connected');
    };

    wsRef.current.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('Received message:', message);

        // Handle different message types for mock server compatibility
        if (message.type === 'connected') {
          console.log('Server acknowledgment:', message.message);
        } else if (message.type === 'auth_success') {
          // Convert to expected format
          onMessage?.({
            type: 'auth_success',
            token: message.token,
            message: message.message
          });
        } else if (message.type === 'auth_failed') {
          // Convert to expected format
          onMessage?.({
            type: 'auth_failed',
            message: message.message || 'Authentication failed'
          });
        } else {
          // Pass through other messages
          onMessage?.(message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError?.(new Error('Failed to parse WebSocket message'));
      }
    };

    wsRef.current.onclose = () => {
      console.log('Disconnected from WebSocket server');
      setConnectionStatus('disconnected');
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('disconnected');
      onError?.(new Error('WebSocket connection error'));
    };
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return;
    }

    if (message instanceof ArrayBuffer) {
      // Send binary video frame data
      console.log('Sending binary frame data, size:', message.byteLength, 'bytes');
      wsRef.current.send(message);
      return;
    }

    if (message instanceof Blob) {
      // Handle blob data - convert to ArrayBuffer
      message.arrayBuffer().then(buffer => {
        console.log('Sending blob as binary data, size:', buffer.byteLength, 'bytes');
        wsRef.current?.send(buffer);
      });
      return;
    }

    // Send JSON messages (auth challenges, metadata, etc.)
    if (typeof message === 'object') {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    connectionStatus,
    connect,
    disconnect,
    sendMessage
  };
}
