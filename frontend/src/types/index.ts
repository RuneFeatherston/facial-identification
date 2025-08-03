export interface AuthMessage {
  type: 'authenticate';
  username: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'connected' | 'auth_success' | 'auth_failure' | 'video_frame';
  message?: string;
  token?: string;
  user?: string;
  data?: string;
  timestamp: string;
}

export interface AuthResult {
  success: boolean;
  token?: string;
  message?: string;
  user?: string;
}
