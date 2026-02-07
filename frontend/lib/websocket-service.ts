/**
 * WebSocket service for real-time chat functionality
 */

type MessageHandler = (data: any) => void;

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private roomId: string | null = null;
  private token: string | null = null;
  private isConnecting = false;

  /**
   * Connect to a chat room WebSocket
   */
  connect(roomId: string, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN && this.roomId === roomId) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      // Disconnect from previous room if any
      if (this.ws) {
        this.disconnect();
      }

      this.roomId = roomId;
      this.token = token;
      this.isConnecting = true;

      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/api/v1/chat/ws/${roomId}?token=${token}`;

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log(`✅ Connected to chat room ${roomId}`);
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = () => {
          console.log(`❌ Disconnected from chat room ${roomId}`);
          this.isConnecting = false;
          this.attemptReconnect();
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from current WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.roomId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    if (!this.roomId || !this.token) {
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.roomId && this.token) {
        this.connect(this.roomId, this.token).catch(console.error);
      }
    }, delay);
  }

  /**
   * Send a message through WebSocket
   */
  send(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return;
    }

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Send a chat message
   */
  sendMessage(content: string, metadata?: any): void {
    this.send({
      type: 'message',
      content,
      metadata: metadata || {},
    });
  }

  /**
   * Send typing indicator
   */
  sendTyping(isTyping: boolean): void {
    this.send({
      type: 'typing',
      is_typing: isTyping,
    });
  }

  /**
   * Mark messages as read
   */
  markAsRead(): void {
    this.send({
      type: 'read',
    });
  }

  /**
   * Register a handler for a specific message type
   */
  on(messageType: string, handler: MessageHandler): void {
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, new Set());
    }
    this.handlers.get(messageType)!.add(handler);
  }

  /**
   * Unregister a handler
   */
  off(messageType: string, handler: MessageHandler): void {
    const handlers = this.handlers.get(messageType);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.handlers.delete(messageType);
      }
    }
  }

  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(data: any): void {
    const handlers = this.handlers.get(data.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in message handler for type ${data.type}:`, error);
        }
      });
    }

    // Also call wildcard handlers
    const wildcardHandlers = this.handlers.get('*');
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in wildcard handler:', error);
        }
      });
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection state
   */
  getState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

// Export singleton instance
export const wsService = new WebSocketService();
export default wsService;
