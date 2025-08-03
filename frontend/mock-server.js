import { WebSocketServer } from 'ws';

const PORT = 8080;
const wss = new WebSocketServer({ port: PORT });

console.log(`Mock WebSocket server running on ws://localhost:${PORT}`);

wss.on('connection', function connection(ws) {
  console.log('Client connected');

  ws.on('message', function incoming(data) {
    try {
      // Handle both JSON and binary data
      if (data instanceof Buffer) {
        // Check if it's JSON or binary
        try {
          const message = JSON.parse(data.toString());
          console.log('Received JSON message:', message.type);
          handleJSONMessage(ws, message);
        } catch (e) {
          // It's binary video frame data
          console.log(`📹 Received binary video frame: ${data.length} bytes`);
          // In a real implementation, you would process this binary data
          // For now, just acknowledge receipt
        }
      } else {
        // ArrayBuffer or other binary data
        console.log(`📹 Received binary video frame: ${data.byteLength || data.length} bytes`);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  });

  function handleJSONMessage(ws, message) {
    // Handle different message types
    switch (message.type) {
      case 'auth_challenge':
        // Simulate authentication process
        console.log(`🔍 Processing authentication for user: ${message.username}`);
        setTimeout(() => {
          // Simulate random success/failure for testing
          const isSuccess = Math.random() > 0.2; // 80% success rate
          
          if (isSuccess) {
            // Generate a mock JWT-like token
            const token = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${Buffer.from(JSON.stringify({
              username: message.username,
              exp: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
              iat: Date.now()
            })).toString('base64')}.mock_signature_${Date.now()}`;

            ws.send(JSON.stringify({
              type: 'auth_success',
              token: token,
              username: message.username,
              timestamp: new Date().toISOString()
            }));
            console.log(`✅ Authentication successful for user: ${message.username}`);
          } else {
            ws.send(JSON.stringify({
              type: 'auth_failed',
              message: 'Facial recognition failed. Please try again.',
              username: message.username,
              timestamp: new Date().toISOString()
            }));
            console.log(`❌ Authentication failed for user: ${message.username}`);
          }
        }, 2000 + Math.random() * 2000); // Random delay 2-4 seconds
        break;

      case 'video_frame_metadata':
        // Handle video frame metadata
        console.log(`📹 Frame #${message.frameNumber} metadata: ${message.width}x${message.height}, ${message.size} bytes`);
        break;

      case 'authenticate':
        // Legacy support for 'authenticate' message type
        setTimeout(() => {
          const isSuccess = Math.random() > 0.3;
          if (isSuccess) {
            ws.send(JSON.stringify({
              type: 'auth_success',
              token: `mock_token_${Date.now()}`,
              username: message.username,
              timestamp: new Date().toISOString()
            }));
            console.log(`✅ Authentication successful for user: ${message.username}`);
          } else {
            ws.send(JSON.stringify({
              type: 'auth_failed',
              message: 'Face not recognized',
              timestamp: new Date().toISOString()
            }));
            console.log(`❌ Authentication failed for user: ${message.username}`);
          }
        }, 2000 + Math.random() * 3000);
        break;

      case 'video_frame':
        // Just acknowledge receipt of video frames (legacy)
        console.log(`📹 Received video frame metadata`);
        break;

      case 'disconnect':
        console.log('Client requesting disconnect');
        ws.close();
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }

  ws.on('close', function close() {
    console.log('Client disconnected');
  });

  ws.on('error', function error(err) {
    console.error('WebSocket error:', err);
  });

  // Send a welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to mock facial recognition server',
    timestamp: new Date().toISOString()
  }));
});

wss.on('error', function error(err) {
  console.error('Server error:', err);
});

process.on('SIGINT', function() {
  console.log('\nShutting down mock server...');
  wss.close(() => {
    process.exit(0);
  });
});
