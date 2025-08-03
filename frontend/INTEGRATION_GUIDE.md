# Facial Recognition Frontend Integration Guide

This document explains how the frontend works, what the mock server simulates, and how to integrate with a real backend.

## Table of Contents
1. [Frontend Overview](#frontend-overview)
2. [Mock Server Behavior](#mock-server-behavior)
3. [WebSocket API Specification](#websocket-api-specification)
4. [Backend Integration Requirements](#backend-integration-requirements)
5. [Authentication Flow](#authentication-flow)
6. [Data Models](#data-models)
7. [Testing & Development](#testing--development)

## Frontend Overview

The frontend is a React/TypeScript application that provides facial recognition authentication through WebSocket communication.

### Key Components:
- **AuthForm**: Username input and authentication initiation
- **VideoStream**: Camera access and video capture
- **UserDashboard**: Post-authentication user interface
- **ConnectionStatus**: WebSocket connection indicator

### Technology Stack:
- React 18 with TypeScript
- Vite for development and building
- WebSocket for real-time communication
- MediaDevices API for camera access

## Mock Server Behavior

The mock server (`mock-server.js`) simulates a real facial recognition backend:

### What it does:
1. **WebSocket Server**: Listens on `ws://localhost:8080`
2. **Connection Handling**: Accepts client connections and sends welcome message
3. **Authentication Simulation**: 
   - Receives auth challenges
   - Simulates processing time (2-4 seconds)
   - Returns success/failure with 80% success rate
4. **Token Generation**: Creates mock JWT-like tokens
5. **Message Logging**: Logs all received messages for debugging

### Mock Server Messages:

#### Incoming (from frontend):
```javascript
// Authentication request
{
  type: 'auth_challenge',
  username: 'john_doe',
  timestamp: 1672531200000
}

// Legacy support
{
  type: 'authenticate', 
  username: 'john_doe',
  timestamp: '2024-01-01T12:00:00Z'
}
```

#### Outgoing (to frontend):
```javascript
// Connection established
{
  type: 'connected',
  message: 'Connected to mock facial recognition server',
  timestamp: '2024-01-01T12:00:00.000Z'
}

// Authentication success
{
  type: 'auth_success',
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  username: 'john_doe',
  timestamp: '2024-01-01T12:00:00.000Z'
}

// Authentication failure
{
  type: 'auth_failed',
  message: 'Facial recognition failed. Please try again.',
  username: 'john_doe',
  timestamp: '2024-01-01T12:00:00.000Z'
}
```

## WebSocket API Specification

### Connection Endpoint
```
ws://localhost:8080
```

### Message Protocol
All messages are JSON formatted strings sent over WebSocket.

### Authentication Flow Messages

#### 1. Client → Server: Authentication Challenge
```typescript
interface AuthChallenge {
  type: 'auth_challenge'
  username: string
  timestamp: number
}
```

#### 2. Server → Client: Authentication Response

**Success:**
```typescript
interface AuthSuccess {
  type: 'auth_success'
  token: string        // JWT token for authenticated session
  username: string     // Confirmed username
  timestamp: string    // ISO 8601 timestamp
}
```

**Failure:**
```typescript
interface AuthFailure {
  type: 'auth_failed'
  message: string      // Error description
  username?: string    // Username that failed (optional)
  timestamp: string    // ISO 8601 timestamp
}
```

#### 3. Server → Client: Connection Acknowledgment
```typescript
interface Connected {
  type: 'connected'
  message: string      // Welcome/status message
  timestamp: string    // ISO 8601 timestamp
}
```

## Backend Integration Requirements

### 1. WebSocket Server Setup
Your Go backend should:
- Listen on a WebSocket endpoint (e.g., `ws://localhost:8080`)
- Handle connection upgrades from HTTP to WebSocket
- Maintain persistent connections for real-time communication

### 2. Authentication Processing
When receiving `auth_challenge`:
1. **Extract username** from the message
2. **Process facial recognition** (integrate with your ML service)
3. **Generate JWT token** if authentication succeeds
4. **Send appropriate response** (`auth_success` or `auth_failed`)

### 3. Required Backend Endpoints

#### WebSocket Handler (Go example structure):
```go
func handleWebSocket(w http.ResponseWriter, r *http.Request) {
    // Upgrade HTTP connection to WebSocket
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println("Upgrade failed:", err)
        return
    }
    defer conn.Close()

    // Send welcome message
    conn.WriteJSON(map[string]interface{}{
        "type": "connected",
        "message": "Connected to facial recognition server",
        "timestamp": time.Now().Format(time.RFC3339),
    })

    // Message handling loop
    for {
        var msg map[string]interface{}
        err := conn.ReadJSON(&msg)
        if err != nil {
            break
        }

        switch msg["type"] {
        case "auth_challenge":
            handleAuthChallenge(conn, msg)
        }
    }
}

func handleAuthChallenge(conn *websocket.Conn, msg map[string]interface{}) {
    username := msg["username"].(string)
    
    // TODO: Integrate with your facial recognition service
    success := authenticateUser(username)
    
    if success {
        token := generateJWT(username)
        conn.WriteJSON(map[string]interface{}{
            "type": "auth_success",
            "token": token,
            "username": username,
            "timestamp": time.Now().Format(time.RFC3339),
        })
    } else {
        conn.WriteJSON(map[string]interface{}{
            "type": "auth_failed",
            "message": "Facial recognition failed",
            "username": username,
            "timestamp": time.Now().Format(time.RFC3339),
        })
    }
}
```

### 4. Database Integration
The frontend expects user profile data. You'll need:

#### User Profile API:
```go
type UserProfile struct {
    Username    string      `json:"username"`
    FullName    string      `json:"fullName"`
    Email       string      `json:"email"`
    JoinDate    string      `json:"joinDate"`
    FaceEntries []FaceEntry `json:"faceEntries"`
}

type FaceEntry struct {
    ID        string `json:"id"`
    CreatedAt string `json:"createdAt"`
    Quality   string `json:"quality"`   // "high", "medium", "low"
    IsActive  bool   `json:"isActive"`
}
```

## Authentication Flow

### Complete Flow Diagram:
```
1. User enters username → Frontend
2. Frontend connects to WebSocket → Backend
3. Backend sends "connected" message → Frontend
4. Frontend sends "auth_challenge" → Backend
5. Backend processes facial recognition → ML Service
6. Backend generates JWT token (if success) → JWT Service
7. Backend sends "auth_success"/"auth_failed" → Frontend
8. Frontend shows dashboard/error → User
```

### Frontend State Management:
```typescript
type AuthStatus = 'idle' | 'authenticating' | 'authenticated' | 'failed'

interface AuthState {
  status: AuthStatus
  username: string
  isAuthenticated: boolean
  token: string | null
  error: string | null
}
```

## Data Models

### Frontend TypeScript Interfaces:

```typescript
// WebSocket message types
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected'

export interface WebSocketMessage {
  type: string
  [key: string]: any
}

// User profile (for dashboard)
export interface UserProfile {
  username: string
  fullName: string
  email: string
  joinDate: string
  faceEntries: FaceEntry[]
}

export interface FaceEntry {
  id: string
  createdAt: string
  quality: 'high' | 'medium' | 'low'
  isActive: boolean
}
```

## Testing & Development

### Running the Frontend:
```bash
cd frontend
npm install
npm run dev        # Development server
npm run dev:mock   # Development + mock server
```

### Mock Server Only:
```bash
cd frontend
node mock-server.js
```

### Testing Authentication:
1. Open `http://localhost:3002` (or appropriate port)
2. Enter any username
3. Click "Start Authentication"
4. Allow camera access
5. Wait for authentication result (80% success rate in mock)

### Environment Configuration:
Create `.env` file in frontend directory:
```env
VITE_WEBSOCKET_URL=ws://localhost:8080
VITE_API_BASE_URL=http://localhost:8080/api
```

### Frontend Configuration for Production:
Update WebSocket URL in `src/App.tsx`:
```typescript
const { connectionStatus, sendMessage, connect, disconnect } = useWebSocket({
  url: process.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080',
  // ... rest of config
})
```

## Security Considerations

### JWT Token Handling:
- Frontend stores token in memory (not localStorage for security)
- Token should include expiration time
- Implement token refresh mechanism if needed

### WebSocket Security:
- Use WSS (WebSocket Secure) in production
- Implement proper authentication before WebSocket upgrade
- Rate limiting for authentication attempts
- Input validation for all messages

### CORS Configuration:
Your Go backend should handle CORS for the frontend origin:
```go
func setupCORS(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "http://localhost:3002")
    w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
}
```

## Error Handling

### Frontend Error Types:
- WebSocket connection errors
- Camera access denied
- Authentication failures
- Network timeouts

### Backend Error Responses:
Always include descriptive error messages:
```json
{
  "type": "auth_failed",
  "message": "Face not recognized",
  "error_code": "FACE_NOT_FOUND",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Integration Checklist

- [ ] WebSocket server on port 8080
- [ ] Handle `auth_challenge` messages
- [ ] Respond with `auth_success`/`auth_failed`
- [ ] Generate valid JWT tokens
- [ ] Implement facial recognition processing
- [ ] Create user profile API endpoints
- [ ] Set up database for user data and face entries
- [ ] Configure CORS for frontend origin
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Test with frontend application

## Quick Start Integration

1. **Replace mock server** with your Go WebSocket server
2. **Update frontend WebSocket URL** if needed
3. **Implement authentication logic** in your backend
4. **Test authentication flow** end-to-end
5. **Add user profile API** for dashboard data
6. **Deploy and configure** production environment

---

*This frontend is designed to be backend-agnostic and can work with any WebSocket server that implements the specified message protocol.*
