import { useState, useEffect } from 'react'
import VideoStream from './components/VideoStream'
import AuthForm from './components/AuthForm'
import ConnectionStatus from './components/ConnectionStatus'
import UserDashboard from './components/UserDashboard'
import { useWebSocket } from './hooks/useWebSocket'
import { AuthState } from './types'

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    status: 'idle',
    username: '',
    isAuthenticated: false,
    token: null,
    error: null
  })
  const [authChallengeSent, setAuthChallengeSent] = useState(false)

  const {
    connectionStatus,
    sendMessage,
    connect,
    disconnect
  } = useWebSocket({
    url: 'ws://localhost:8080', // Mock server endpoint
    onMessage: (data) => {
      // Handle authentication response from backend
      if (data.type === 'auth_success') {
        setAuthState(prev => ({
          ...prev,
          status: 'authenticated',
          isAuthenticated: true,
          token: data.token,
          error: null
        }))
      } else if (data.type === 'auth_failed') {
        setAuthState(prev => ({
          ...prev,
          status: 'failed',
          isAuthenticated: false,
          token: null,
          error: data.message || 'Authentication failed'
        }))
      }
    },
    onError: (error) => {
      setAuthState(prev => ({
        ...prev,
        status: 'failed',
        error: error.message
      }))
    }
  })

  const handleStartAuth = (username: string) => {
    if (!username.trim()) {
      setAuthState(prev => ({
        ...prev,
        error: 'Username is required'
      }))
      return
    }

    setAuthState({
      status: 'authenticating',
      username: username.trim(),
      isAuthenticated: false,
      token: null,
      error: null
    })
    setAuthChallengeSent(false)

    // Connect to WebSocket if not already connected
    if (connectionStatus === 'disconnected') {
      connect()
    }
  }

  const handleVideoData = (frameData: ArrayBuffer, metadata: any) => {
    if (authState.status === 'authenticating' && connectionStatus === 'connected') {
      // Send frame metadata first (JSON)
      sendMessage({
        type: 'video_frame_metadata',
        username: metadata.username,
        frameNumber: metadata.frameNumber,
        timestamp: metadata.timestamp,
        width: metadata.width,
        height: metadata.height,
        format: metadata.format,
        size: frameData.byteLength
      })
      
      // Then send the binary frame data
      sendMessage(frameData)
    }
  }

  const handleReset = () => {
    setAuthState({
      status: 'idle',
      username: '',
      isAuthenticated: false,
      token: null,
      error: null
    })
    setAuthChallengeSent(false)
    disconnect()
  }

  const handleLogout = () => {
    setAuthState({
      status: 'idle',
      username: '',
      isAuthenticated: false,
      token: null,
      error: null
    })
    setAuthChallengeSent(false)
    disconnect()
  }

  const handleRescanFace = () => {
    // Keep the same user but restart the authentication process
    setAuthState(prev => ({
      ...prev,
      status: 'authenticating',
      isAuthenticated: false,
      token: null,
      error: null
    }))
    setAuthChallengeSent(false)
    
    // Connect to WebSocket if not already connected
    if (connectionStatus === 'disconnected') {
      connect()
    }
  }

  useEffect(() => {
    // Auto-connect on component mount
    connect()

    return () => {
      disconnect()
    }
  }, [])

  // Send auth challenge when connected and in authenticating state
  useEffect(() => {
    if (connectionStatus === 'connected' && 
        authState.status === 'authenticating' && 
        !authChallengeSent &&
        authState.username) {
      sendMessage({
        type: 'auth_challenge',
        username: authState.username,
        timestamp: Date.now()
      })
      setAuthChallengeSent(true)
      console.log('Auth challenge sent for user:', authState.username)
    }
  }, [connectionStatus, authState.status, authState.username, authChallengeSent, sendMessage])

  return (
    <div className="container">
      {/* Show dashboard when authenticated */}
      {authState.status === 'authenticated' && authState.token && authState.username ? (
        <UserDashboard 
          username={authState.username}
          token={authState.token}
          onLogout={handleLogout}
          onRescanFace={handleRescanFace}
        />
      ) : (
        <>
          <h1>Facial Recognition Authentication</h1>
          
          <div className="auth-form">
            <ConnectionStatus status={connectionStatus} />
            
            {authState.status === 'idle' && (
              <AuthForm onStartAuth={handleStartAuth} />
            )}

            {authState.status === 'authenticating' && (
              <div>
                <h3>Authenticating as {authState.username}...</h3>
                <VideoStream 
                  onVideoData={handleVideoData} 
                  username={authState.username}
                  isActive={true}
                />
                <button onClick={handleReset}>Cancel</button>
              </div>
            )}

            {authState.status === 'failed' && authState.error && (
              <div className="error-message">
                <h3>❌ Authentication Failed</h3>
                <p>{authState.error}</p>
                <button onClick={handleReset}>Try Again</button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default App
