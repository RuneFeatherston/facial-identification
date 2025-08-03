export interface AuthState {
  status: 'idle' | 'authenticating' | 'authenticated' | 'failed'
  username: string
  isAuthenticated: boolean
  token: string | null
  error: string | null
}

export interface VideoFrameMetadata {
  username: string
  frameNumber: number
  timestamp: number
  width: number
  height: number
  format: string
}

export interface WebSocketMessage {
  type: string
  [key: string]: unknown
}

export interface AuthResponse {
  type: 'auth_success' | 'auth_failed'
  token?: string
  message?: string
}

export interface AuthChallenge {
  type: 'auth_challenge'
  username: string
  timestamp: number
}

export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected'

export interface VideoStreamProps {
  onVideoData: (videoData: Blob) => void
}

export interface AuthFormProps {
  onStartAuth: (username: string) => void
}

export interface ConnectionStatusProps {
  status: ConnectionStatus
}
