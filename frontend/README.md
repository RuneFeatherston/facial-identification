# Facial Recognition Frontend

A React/TypeScript frontend application for facial recognition authentication using WebSockets.

## Features

- **Live Camera Feed**: Captures real-time video from user's camera
- **WebSocket Communication**: Streams video data to backend for authentication
- **Clean UI**: Modern, responsive interface for authentication flow
- **Username + Video Authentication**: Combines username input with facial recognition
- **Real-time Status**: Shows connection status and authentication progress
- **Token Validation**: Receives and displays authentication tokens from backend

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **WebSocket** for real-time communication
- **Canvas API** for video frame capture
- **Media API** for camera access

## Getting Started

### Prerequisites

- Node.js 16+ 
- A webcam
- Backend WebSocket server running on `ws://localhost:8080/ws`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

This will start the development server on `http://localhost:3000`.

### Build

```bash
npm run build
```

## Architecture

### Components

- **App.tsx**: Main application component managing authentication state
- **AuthForm.tsx**: Username input form
- **VideoStream.tsx**: Camera feed capture and streaming
- **ConnectionStatus.tsx**: WebSocket connection status indicator

### Hooks

- **useWebSocket.ts**: WebSocket connection management with auto-reconnection

### Types

- **types.ts**: TypeScript interfaces for type safety

## WebSocket Protocol

The frontend communicates with the backend using the following message format:

### Outgoing Messages

1. **Authentication Challenge**:
```json
{
  "type": "auth_challenge",
  "username": "user123",
  "timestamp": 1234567890
}
```

2. **Video Data**: Binary blob data (JPEG frames)

### Incoming Messages

1. **Authentication Success**:
```json
{
  "type": "auth_success",
  "token": "jwt_token_here"
}
```

2. **Authentication Failed**:
```json
{
  "type": "auth_failed",
  "message": "Authentication failed reason"
}
```

## Configuration

### WebSocket URL

The WebSocket URL can be configured in `src/App.tsx`:

```typescript
const { connectionStatus, sendMessage, connect, disconnect } = useWebSocket({
  url: 'ws://localhost:8080/ws', // Change this to your backend URL
  // ...
})
```

### Video Settings

Video capture settings can be modified in `src/components/VideoStream.tsx`:

```typescript
const stream = await navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 640 },
    height: { ideal: 480 },
    facingMode: 'user'
  },
  audio: false
})
```

## Backend Integration

This frontend is designed to work with a Go backend that:

1. Accepts WebSocket connections at `/ws`
2. Receives username + video stream data
3. Performs facial recognition authentication
4. Returns validation tokens

The backend should handle:
- WebSocket upgrade
- Binary video frame processing
- Facial recognition algorithms
- JWT token generation
- User database lookup

## Browser Compatibility

- Chrome 88+
- Firefox 84+
- Safari 14+
- Edge 88+

Requires support for:
- WebSocket API
- Media Devices API
- Canvas API
- ES2020 features

## Security Considerations

- Camera permission required
- HTTPS recommended for production
- WebSocket connections should use WSS in production
- Implement proper CORS policies
- Validate all incoming data on backend
- Implement rate limiting for authentication attempts

## Development Notes

- Video frames are captured at 10 FPS (100ms intervals)
- JPEG compression at 70% quality for optimal balance
- Auto-reconnection on WebSocket disconnection
- Responsive design for various screen sizes
- Error handling for camera access issues
