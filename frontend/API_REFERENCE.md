# API Reference - Facial Recognition Frontend

## WebSocket Messages

### Client → Server Messages

#### Authentication Challenge
```json
{
  "type": "auth_challenge",
  "username": "john_doe",
  "timestamp": 1672531200000
}
```

**Fields:**
- `type`: Always "auth_challenge"
- `username`: User identifier for authentication
- `timestamp`: Unix timestamp when challenge was sent

#### Video Frame Metadata
```json
{
  "type": "video_frame_metadata",
  "username": "john_doe",
  "frameNumber": 42,
  "timestamp": 1672531200000,
  "width": 640,
  "height": 480,
  "format": "jpeg",
  "size": 15248
}
```

**Fields:**
- `type`: Always "video_frame_metadata"
- `username`: User identifier
- `frameNumber`: Sequential frame counter
- `timestamp`: Unix timestamp when frame was captured
- `width`: Frame width in pixels
- `height`: Frame height in pixels
- `format`: Image format ("jpeg")
- `size`: Binary data size in bytes

#### Video Frame Data (Binary)
- **Type**: Binary ArrayBuffer
- **Format**: JPEG image data
- **Frequency**: ~2 frames per second
- **Quality**: 80% JPEG compression
- **Size**: Typically 10-30KB per frame

**Note**: Video frame metadata (JSON) is sent immediately before each binary frame.

### Server → Client Messages

#### Connection Established
```json
{
  "type": "connected",
  "message": "Connected to facial recognition server",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Authentication Success
```json
{
  "type": "auth_success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImpvaG5fZG9lIiwiZXhwIjoxNjcyNjE3NjAwLCJpYXQiOjE2NzI1MzEyMDB9.signature",
  "username": "john_doe",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Fields:**
- `type`: Always "auth_success"
- `token`: JWT token for authenticated session
- `username`: Confirmed username
- `timestamp`: ISO 8601 timestamp

#### Authentication Failure
```json
{
  "type": "auth_failed",
  "message": "Facial recognition failed. Please try again.",
  "username": "john_doe",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Fields:**
- `type`: Always "auth_failed"
- `message`: Human-readable error description
- `username`: Username that failed authentication (optional)
- `timestamp`: ISO 8601 timestamp

## Frontend Configuration

### Environment Variables
```env
VITE_WEBSOCKET_URL=ws://localhost:8080
VITE_API_BASE_URL=http://localhost:8080/api
```

### Mock Server vs Production
The frontend automatically connects to the WebSocket URL specified in the code. Update `src/App.tsx`:

```typescript
// Development (mock server)
url: 'ws://localhost:8080'

// Production
url: process.env.VITE_WEBSOCKET_URL || 'wss://your-domain.com/ws'
```

## User Dashboard Data

The dashboard component expects user profile data with this structure:

```typescript
interface UserProfile {
  username: string      // "john_doe"
  fullName: string      // "John Doe"
  email: string         // "john@company.com"
  joinDate: string      // "2024-01-15"
  faceEntries: FaceEntry[]
}

interface FaceEntry {
  id: string           // "face_001"
  createdAt: string    // "2024-01-15T10:30:00Z"
  quality: 'high' | 'medium' | 'low'
  isActive: boolean    // true
}
```

## Backend Implementation Example (Go)

### Basic WebSocket Handler
```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "time"
    
    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true // Configure properly for production
    },
}

type AuthChallenge struct {
    Type      string `json:"type"`
    Username  string `json:"username"`
    Timestamp int64  `json:"timestamp"`
}

type VideoFrameMetadata struct {
    Type        string `json:"type"`
    Username    string `json:"username"`
    FrameNumber int    `json:"frameNumber"`
    Timestamp   int64  `json:"timestamp"`
    Width       int    `json:"width"`
    Height      int    `json:"height"`
    Format      string `json:"format"`
    Size        int    `json:"size"`
}

type AuthResponse struct {
    Type      string `json:"type"`
    Token     string `json:"token,omitempty"`
    Username  string `json:"username,omitempty"`
    Message   string `json:"message,omitempty"`
    Timestamp string `json:"timestamp"`
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println("Upgrade failed:", err)
        return
    }
    defer conn.Close()

    // Send welcome message
    welcome := AuthResponse{
        Type:      "connected",
        Message:   "Connected to facial recognition server",
        Timestamp: time.Now().Format(time.RFC3339),
    }
    conn.WriteJSON(welcome)

    // Message loop
    for {
        messageType, data, err := conn.ReadMessage()
        if err != nil {
            log.Println("Read error:", err)
            break
        }

        switch messageType {
        case websocket.TextMessage:
            // Handle JSON messages
            var message map[string]interface{}
            if err := json.Unmarshal(data, &message); err != nil {
                log.Println("JSON parse error:", err)
                continue
            }

            switch message["type"] {
            case "auth_challenge":
                handleAuthChallenge(conn, message)
            case "video_frame_metadata":
                handleVideoMetadata(conn, message)
            }

        case websocket.BinaryMessage:
            // Handle binary video frame data
            log.Printf("Received binary frame: %d bytes", len(data))
            processVideoFrame(data)
        }
    }
}

func handleAuthChallenge(conn *websocket.Conn, msg map[string]interface{}) {
    username := msg["username"].(string)
    
    // TODO: Integrate with your facial recognition service
    success := authenticateUser(username)
    
    if success {
        token := generateJWT(username)
        conn.WriteJSON(AuthResponse{
            Type:      "auth_success",
            Token:     token,
            Username:  username,
            Timestamp: time.Now().Format(time.RFC3339),
        })
    } else {
        conn.WriteJSON(AuthResponse{
            Type:      "auth_failed",
            Message:   "Facial recognition failed",
            Username:  username,
            Timestamp: time.Now().Format(time.RFC3339),
        })
    }
}

func handleVideoMetadata(conn *websocket.Conn, msg map[string]interface{}) {
    frameNum := int(msg["frameNumber"].(float64))
    width := int(msg["width"].(float64))
    height := int(msg["height"].(float64))
    size := int(msg["size"].(float64))
    
    log.Printf("Frame #%d metadata: %dx%d, %d bytes", frameNum, width, height, size)
    // Store metadata for correlation with next binary message
}

func processVideoFrame(frameData []byte) {
    // TODO: Process JPEG frame data for facial recognition
    // This is where you'd integrate with your ML/CV service
    log.Printf("Processing video frame: %d bytes", len(frameData))
}

func authenticateUser(username string) bool {
    // TODO: Implement your facial recognition logic
    return true // Placeholder
}

func generateJWT(username string) string {
    // TODO: Implement JWT generation
    return "mock_token_" + username // Placeholder
}

func main() {
    http.HandleFunc("/ws", handleWebSocket)
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## Testing Commands

### Start Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Start Mock Server
```bash
cd frontend
node mock-server.js
```

### Test Authentication Flow
1. Navigate to frontend URL (usually http://localhost:3002)
2. Enter username: "test"
3. Click "Start Authentication"
4. Allow camera access
5. Wait for result (mock server has 80% success rate)

### Check WebSocket Connection
Use browser developer tools:
1. Open Network tab
2. Filter by "WS" (WebSocket)
3. Start authentication
4. View WebSocket messages in real-time

## Deployment Notes

### Frontend Build
```bash
npm run build
# Outputs to dist/ directory
```

### Backend Requirements
- WebSocket support
- CORS configuration
- JWT token generation
- Facial recognition service integration
- User database with profile and face entry storage

### Security Checklist
- [ ] Use WSS in production
- [ ] Implement proper CORS
- [ ] Validate all input messages
- [ ] Rate limit authentication attempts
- [ ] Secure JWT signing
- [ ] Handle camera permissions properly
