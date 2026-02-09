/**
 * Collaborative Editing Service
 * Handles collaborative code editing sessions and WebSocket communication
 */

import api from './api';

export interface CollaborativeSession {
  id: string;
  owner_id: string;
  course_id?: string;
  title: string;
  description?: string;
  language: string;
  code_content: string;
  is_public: boolean;
  max_participants?: number;
  current_participants: number;
  expires_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateSession {
  course_id?: string;
  title: string;
  description?: string;
  language: string;
  code_content?: string;
  is_public?: boolean;
  max_participants?: number;
}

export interface UpdateSession {
  title?: string;
  description?: string;
  language?: string;
  code_content?: string;
  is_public?: boolean;
  max_participants?: number;
}

export interface Participant {
  id: string;
  session_id: string;
  user_id: string;
  cursor_position?: { line: number; column: number };
  is_active: boolean;
  joined_at: string;
  last_active_at?: string;
}

export interface CodeUpdate {
  type: 'code_update' | 'cursor_move' | 'user_joined' | 'user_left';
  user_id?: string;
  session_id?: string;
  content?: string;
  cursor_position?: { line: number; column: number };
  timestamp?: string;
}

/**
 * Create a new collaborative session
 */
export async function createCollaborativeSession(
  data: CreateSession
): Promise<CollaborativeSession> {
  const response = await api.post('/collaborative', data);
  return response.data;
}

/**
 * Get list of collaborative sessions
 */
export async function getCollaborativeSessions(params?: {
  course_id?: string;
  my_sessions?: boolean;
  skip?: number;
  limit?: number;
}): Promise<{
  sessions: CollaborativeSession[];
  total: number;
  skip: number;
  limit: number;
}> {
  const response = await api.get('/collaborative', { params });
  return response.data;
}

/**
 * Get details of a specific session
 */
export async function getCollaborativeSession(sessionId: string): Promise<CollaborativeSession> {
  const response = await api.get(`/collaborative/${sessionId}`);
  return response.data;
}

/**
 * Update a collaborative session
 */
export async function updateCollaborativeSession(
  sessionId: string,
  data: UpdateSession
): Promise<CollaborativeSession> {
  const response = await api.put(`/collaborative/${sessionId}`, data);
  return response.data;
}

/**
 * Delete a collaborative session
 */
export async function deleteCollaborativeSession(sessionId: string): Promise<void> {
  await api.delete(`/collaborative/${sessionId}`);
}

/**
 * Get participants of a session
 */
export async function getSessionParticipants(sessionId: string): Promise<Participant[]> {
  const response = await api.get(`/collaborative/${sessionId}/participants`);
  return response.data;
}

/**
 * Collaborative WebSocket Manager
 */
export class CollaborativeWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private token: string;
  private onCodeUpdate?: (update: CodeUpdate) => void;
  private onConnectionChange?: (connected: boolean) => void;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(
    sessionId: string,
    token: string,
    callbacks: {
      onCodeUpdate?: (update: CodeUpdate) => void;
      onConnectionChange?: (connected: boolean) => void;
    }
  ) {
    this.sessionId = sessionId;
    this.token = token;
    this.onCodeUpdate = callbacks.onCodeUpdate;
    this.onConnectionChange = callbacks.onConnectionChange;
  }

  /**
   * Connect to WebSocket
   */
  connect(): void {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/api/v1/collaborative/ws/${this.sessionId}?token=${this.token}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Collaborative WebSocket connected');
      this.reconnectAttempts = 0;
      this.onConnectionChange?.(true);
    };

    this.ws.onmessage = (event) => {
      try {
        const data: CodeUpdate = JSON.parse(event.data);
        this.onCodeUpdate?.(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('Collaborative WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Collaborative WebSocket disconnected');
      this.onConnectionChange?.(false);
      this.attemptReconnect();
    };
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  /**
   * Send code update
   */
  sendCodeUpdate(content: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'code_update',
          content,
          timestamp: new Date().toISOString(),
        })
      );
    }
  }

  /**
   * Send cursor position update
   */
  sendCursorUpdate(line: number, column: number): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'cursor_move',
          cursor_position: { line, column },
          timestamp: new Date().toISOString(),
        })
      );
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

/**
 * Get language display name
 */
export function getLanguageDisplayName(lang: string): string {
  const languages: Record<string, string> = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    java: 'Java',
    cpp: 'C++',
    csharp: 'C#',
    go: 'Go',
    rust: 'Rust',
    php: 'PHP',
    ruby: 'Ruby',
    html: 'HTML',
    css: 'CSS',
    sql: 'SQL',
    markdown: 'Markdown',
    json: 'JSON',
    yaml: 'YAML',
  };
  return languages[lang] || lang.toUpperCase();
}

/**
 * Get Monaco editor language ID
 */
export function getMonacoLanguage(lang: string): string {
  const mapping: Record<string, string> = {
    cpp: 'cpp',
    csharp: 'csharp',
    javascript: 'javascript',
    typescript: 'typescript',
    python: 'python',
    java: 'java',
    go: 'go',
    rust: 'rust',
    php: 'php',
    ruby: 'ruby',
    html: 'html',
    css: 'css',
    sql: 'sql',
    markdown: 'markdown',
    json: 'json',
    yaml: 'yaml',
  };
  return mapping[lang] || 'plaintext';
}

/**
 * Generate default code template
 */
export function getDefaultCodeTemplate(language: string): string {
  const templates: Record<string, string> = {
    javascript: '// JavaScript collaborative session\nconsole.log("Hello, World!");\n',
    typescript: '// TypeScript collaborative session\nconst greeting: string = "Hello, World!";\nconsole.log(greeting);\n',
    python: '# Python collaborative session\nprint("Hello, World!")\n',
    java: '// Java collaborative session\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
    cpp: '// C++ collaborative session\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}\n',
    go: '// Go collaborative session\npackage main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}\n',
    html: '<!-- HTML collaborative session -->\n<!DOCTYPE html>\n<html>\n<head>\n    <title>Collaborative Session</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>\n',
    css: '/* CSS collaborative session */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}\n',
  };
  return templates[language] || '// Start coding...\n';
}
