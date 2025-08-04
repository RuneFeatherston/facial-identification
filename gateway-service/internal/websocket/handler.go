package websocket

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"gateway-service/internal/auth"
	"gateway-service/internal/mlservice"
	"gateway-service/internal/repository"

	"github.com/gorilla/websocket"
)

// Upgrader configures the websocket upgrader
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// Allow all origins for now - implement proper checking in production
		return true
	},
}

// ConnectionState tracks the state of a WebSocket connection
type ConnectionState struct {
	Username            string
	PendingAuth         bool
	PendingRegistration bool
	StoredEmbeddings    [][]float64
	UserID              string
}

// Message types for WebSocket communication
type MessageType string

const (
	AuthChallenge      MessageType = "auth_challenge"
	VideoFrameMetadata MessageType = "video_frame_metadata"
	AuthSuccess        MessageType = "auth_success"
	AuthFailed         MessageType = "auth_failed"
	Connected          MessageType = "connected"
)

// WebSocket message structures matching the API specification
type WSMessage struct {
	Type      MessageType `json:"type"`
	Username  string      `json:"username,omitempty"`
	Token     string      `json:"token,omitempty"`
	Message   string      `json:"message,omitempty"`
	Timestamp string      `json:"timestamp"`
}

type AuthChallengeMessage struct {
	Type      MessageType `json:"type"`
	Username  string      `json:"username"`
	Timestamp int64       `json:"timestamp"`
}

type VideoFrameMetadataMessage struct {
	Type        MessageType `json:"type"`
	Username    string      `json:"username"`
	FrameNumber int         `json:"frameNumber"`
	Timestamp   int64       `json:"timestamp"`
	Width       int         `json:"width"`
	Height      int         `json:"height"`
	Format      string      `json:"format"`
	Size        int         `json:"size"`
}

// Handler manages WebSocket connections and authentication
type Handler struct {
	userRepo     repository.UserRepositoryInterface
	authSvc      *auth.Service
	mlClient     mlservice.Interface
	currentFrame map[string][]byte                    // Store current frame data by connection ID
	connections  map[*websocket.Conn]*ConnectionState // Track connection states
}

func NewHandler(userRepo repository.UserRepositoryInterface, authSvc *auth.Service, mlClient mlservice.Interface) *Handler {
	return &Handler{
		userRepo:     userRepo,
		authSvc:      authSvc,
		mlClient:     mlClient,
		currentFrame: make(map[string][]byte),
		connections:  make(map[*websocket.Conn]*ConnectionState),
	}
}

// HandleWebSocket handles WebSocket connections from the frontend
func (h *Handler) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	defer func() {
		// Clean up connection state
		delete(h.connections, conn)
		conn.Close()
	}()

	log.Printf("New WebSocket connection from %s", r.RemoteAddr)

	// Initialize connection state
	h.connections[conn] = &ConnectionState{}

	// Send welcome message
	welcome := WSMessage{
		Type:      Connected,
		Message:   "Connected to facial recognition server",
		Timestamp: time.Now().Format(time.RFC3339),
	}
	if err := conn.WriteJSON(welcome); err != nil {
		log.Printf("Failed to send welcome message: %v", err)
		return
	}

	// Message handling loop
	for {
		messageType, data, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket error: %v", err)
			}
			break
		}

		switch messageType {
		case websocket.TextMessage:
			h.handleTextMessage(conn, data)
		case websocket.BinaryMessage:
			h.handleBinaryMessage(conn, data)
		}
	}

	log.Printf("WebSocket connection closed for %s", r.RemoteAddr)
}

// handleTextMessage processes JSON text messages
func (h *Handler) handleTextMessage(conn *websocket.Conn, data []byte) {
	var message map[string]interface{}
	if err := json.Unmarshal(data, &message); err != nil {
		log.Printf("Failed to parse JSON message: %v", err)
		h.sendErrorMessage(conn, "Invalid JSON format")
		return
	}

	msgType, ok := message["type"].(string)
	if !ok {
		log.Printf("Message missing 'type' field")
		h.sendErrorMessage(conn, "Message missing 'type' field")
		return
	}

	switch MessageType(msgType) {
	case AuthChallenge:
		h.handleAuthChallenge(conn, message)
	case VideoFrameMetadata:
		h.handleVideoFrameMetadata(conn, message)
	case "authenticate": // Legacy support
		h.handleLegacyAuthenticate(conn, message)
	default:
		log.Printf("Unknown message type: %s", msgType)
		h.sendErrorMessage(conn, fmt.Sprintf("Unknown message type: %s", msgType))
	}
}

// handleBinaryMessage processes binary video frame data
func (h *Handler) handleBinaryMessage(conn *websocket.Conn, data []byte) {
	log.Printf("Received binary video frame: %d bytes", len(data))

	// Check connection state
	state, exists := h.connections[conn]
	if !exists {
		log.Printf("No connection state found for binary message")
		return
	}

	// If we're waiting for an authentication frame
	if state.PendingAuth && state.Username != "" {
		h.processAuthenticationFrame(conn, state, data)
		return
	}

	// Handle other binary message types (e.g., registration)
	log.Printf("Received binary frame but no pending operation")
}

// processAuthenticationFrame handles face authentication
func (h *Handler) processAuthenticationFrame(conn *websocket.Conn, state *ConnectionState, frameData []byte) {
	log.Printf("Processing authentication frame for user: %s", state.Username)

	go func() {
		// Extract face embedding from the frame using ML service
		response, err := h.mlClient.ExtractEmbedding(frameData)
		if err != nil {
			log.Printf("Failed to extract embedding: %v", err)
			h.sendAuthFailure(conn, state.Username, "Failed to process face image")
			state.PendingAuth = false
			return
		}

		if !response.Success {
			log.Printf("ML service failed to extract embedding: %s", response.Message)
			h.sendAuthFailure(conn, state.Username, "Face not detected or poor quality")
			state.PendingAuth = false
			return
		}

		// Compare extracted embedding with stored embeddings
		authResponse, err := h.mlClient.AuthenticateUser(response.Embedding, state.StoredEmbeddings)
		if err != nil {
			log.Printf("Authentication failed: %v", err)
			h.sendAuthFailure(conn, state.Username, "Authentication service error")
			state.PendingAuth = false
			return
		}

		if !authResponse.Success || !authResponse.IsAuthenticated {
			log.Printf("Authentication failed for user %s: confidence=%.2f", state.Username, authResponse.Confidence)
			h.sendAuthFailure(conn, state.Username, "Face authentication failed")
			state.PendingAuth = false
			return
		}

		// Authentication successful - generate JWT token
		token, err := h.authSvc.GenerateToken(state.UserID, state.Username)
		if err != nil {
			log.Printf("Failed to generate token: %v", err)
			h.sendAuthFailure(conn, state.Username, "Failed to generate authentication token")
			state.PendingAuth = false
			return
		}

		// Store auth session
		expiresAt := time.Now().Add(24 * time.Hour)
		_, err = h.userRepo.CreateAuthSession(state.UserID, token, expiresAt)
		if err != nil {
			log.Printf("Failed to create auth session: %v", err)
			// Continue anyway, token is still valid
		}

		// Send success response
		log.Printf("Authentication successful for user %s (confidence: %.2f)", state.Username, authResponse.Confidence)
		h.sendAuthSuccess(conn, state.Username, token)
		state.PendingAuth = false
	}()
}

// handleAuthChallenge processes authentication challenge messages
func (h *Handler) handleAuthChallenge(conn *websocket.Conn, message map[string]interface{}) {
	username, ok := message["username"].(string)
	if !ok {
		h.sendErrorMessage(conn, "Username is required")
		return
	}

	log.Printf("Processing auth challenge for username: %s", username)

	// Process authentication in background
	go func() {
		// Check if user exists
		user, err := h.userRepo.GetUserByUsername(username)
		if err != nil {
			log.Printf("User %s not found: %v", username, err)
			h.sendAuthFailure(conn, username, "User not found. Please register first.")
			return
		}

		// Get stored face embeddings for this user
		storedEmbeddings, err := h.userRepo.GetFaceEmbeddingsForUser(user.ID)
		if err != nil {
			log.Printf("Failed to get face embeddings for user %s: %v", username, err)
			h.sendAuthFailure(conn, username, "No face data found. Please register first.")
			return
		}

		if len(storedEmbeddings) == 0 {
			log.Printf("No face embeddings found for user %s", username)
			h.sendAuthFailure(conn, username, "No face data found. Please register first.")
			return
		}

		// Convert [][]byte to [][]float64 for ML service
		embeddings := make([][]float64, len(storedEmbeddings))
		for i, embeddingBytes := range storedEmbeddings {
			// Convert byte array back to float64 slice
			// This assumes the embeddings are stored as JSON-encoded float64 arrays
			var embedding []float64
			if err := json.Unmarshal(embeddingBytes, &embedding); err != nil {
				log.Printf("Failed to unmarshal embedding: %v", err)
				continue
			}
			embeddings[i] = embedding
		}

		// Set connection state to wait for authentication frame
		if state, exists := h.connections[conn]; exists {
			state.Username = username
			state.PendingAuth = true
			state.StoredEmbeddings = embeddings
			state.UserID = user.ID
		}

		// Request video frame for authentication
		response := WSMessage{
			Type:      VideoFrameMetadata,
			Username:  username,
			Message:   "Please look at the camera for authentication",
			Timestamp: time.Now().Format(time.RFC3339),
		}

		if err := conn.WriteJSON(response); err != nil {
			log.Printf("Failed to send frame request: %v", err)
			return
		}
	}()
}

// handleVideoFrameMetadata processes video frame metadata messages
func (h *Handler) handleVideoFrameMetadata(conn *websocket.Conn, message map[string]interface{}) {
	username, ok := message["username"].(string)
	if !ok {
		h.sendErrorMessage(conn, "Username is required in video frame metadata")
		return
	}

	frameNumber, ok := message["frameNumber"].(float64)
	if !ok {
		h.sendErrorMessage(conn, "Frame number is required in video frame metadata")
		return
	}

	width, ok := message["width"].(float64)
	if !ok {
		h.sendErrorMessage(conn, "Width is required in video frame metadata")
		return
	}

	height, ok := message["height"].(float64)
	if !ok {
		h.sendErrorMessage(conn, "Height is required in video frame metadata")
		return
	}

	size, ok := message["size"].(float64)
	if !ok {
		h.sendErrorMessage(conn, "Size is required in video frame metadata")
		return
	}

	format, ok := message["format"].(string)
	if !ok {
		format = "jpeg" // Default format
	}

	log.Printf("Video frame metadata - User: %s, Frame: %.0f, Size: %.0fx%.0f, Format: %s, Data size: %.0f bytes",
		username, frameNumber, width, height, format, size)

	// Store metadata for correlation with next binary frame
	// TODO: Store this metadata to correlate with incoming binary frame
}

// handleLegacyAuthenticate handles legacy authenticate messages for backward compatibility
func (h *Handler) handleLegacyAuthenticate(conn *websocket.Conn, message map[string]interface{}) {
	// Convert to auth_challenge format
	newMessage := map[string]interface{}{
		"type":      "auth_challenge",
		"username":  message["username"],
		"timestamp": time.Now().UnixMilli(),
	}
	h.handleAuthChallenge(conn, newMessage)
}

// sendAuthSuccess sends authentication success message
func (h *Handler) sendAuthSuccess(conn *websocket.Conn, username, token string) {
	response := WSMessage{
		Type:      AuthSuccess,
		Token:     token,
		Username:  username,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	if err := conn.WriteJSON(response); err != nil {
		log.Printf("Failed to send auth success: %v", err)
	} else {
		log.Printf("Authentication successful for user: %s", username)
	}
}

// sendAuthFailure sends authentication failure message
func (h *Handler) sendAuthFailure(conn *websocket.Conn, username, message string) {
	response := WSMessage{
		Type:      AuthFailed,
		Message:   message,
		Username:  username,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	if err := conn.WriteJSON(response); err != nil {
		log.Printf("Failed to send auth failure: %v", err)
	} else {
		log.Printf("Authentication failed for user: %s - %s", username, message)
	}
}

// sendErrorMessage sends a generic error message
func (h *Handler) sendErrorMessage(conn *websocket.Conn, message string) {
	response := WSMessage{
		Type:      AuthFailed,
		Message:   message,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	if err := conn.WriteJSON(response); err != nil {
		log.Printf("Failed to send error message: %v", err)
	}
}
