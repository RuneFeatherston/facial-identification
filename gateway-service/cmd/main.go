package main

import (
	"log"
	"net/http"
	"os"

	"gateway-service/internal/auth"
	"gateway-service/internal/database"
	"gateway-service/internal/handlers"
	"gateway-service/internal/mlservice"
	"gateway-service/internal/repository"
	"gateway-service/internal/websocket"
)

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func main() {
	// Check if we're in test mode (skip database for testing)
	testMode := getEnv("TEST_MODE", "") == "true"

	// Database configuration from environment
	dbConfig := database.Config{
		Host:     getEnv("DB_HOST", "localhost"),
		Port:     5432, // Fixed port, no need for env parsing complexity
		User:     getEnv("DB_USER", "postgres"),
		Password: getEnv("DB_PASSWORD", "postgres"),
		DBName:   getEnv("DB_NAME", "facial_recognition"),
		SSLMode:  getEnv("DB_SSLMODE", "disable"),
	}

	var userRepo repository.UserRepositoryInterface

	if testMode {
		log.Println("Running in TEST MODE - using mock repository")
		userRepo = repository.NewMockUserRepository()
	} else {
		// Initialize database
		db, err := database.NewConnection(dbConfig)
		if err != nil {
			log.Fatalf("Failed to connect to database: %v", err)
		}
		defer db.Close()

		// Create tables
		if err := db.CreateTables(); err != nil {
			log.Fatalf("Failed to create tables: %v", err)
		}

		userRepo = repository.NewUserRepository(db)
	}
	authService := auth.NewService(getEnv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production"))
	mlClient := mlservice.NewClient(getEnv("ML_SERVICE_URL", "http://localhost:8081"))

	// Initialize handlers
	apiHandlers := handlers.NewAPIHandlers(userRepo)
	wsHandler := websocket.NewHandler(userRepo, authService, mlClient)

	// Setup routes with CORS middleware
	mux := http.NewServeMux()

	// API routes
	mux.HandleFunc("/health", apiHandlers.HealthHandler)
	mux.HandleFunc("/api/user/profile", apiHandlers.GetUserProfileHandler)

	// WebSocket route
	mux.HandleFunc("/ws", wsHandler.HandleWebSocket)

	// Apply CORS middleware
	handler := apiHandlers.CORSMiddleware(mux)

	// Start server
	port := getEnv("SERVER_PORT", "8080")
	host := getEnv("SERVER_HOST", "0.0.0.0")
	serverAddr := host + ":" + port

	log.Printf("Gateway service starting on %s", serverAddr)
	log.Printf("WebSocket endpoint: ws://%s/ws", serverAddr)
	log.Printf("Health endpoint: http://%s/health", serverAddr)
	log.Printf("User profile API: http://%s/api/user/profile", serverAddr)

	log.Fatal(http.ListenAndServe(serverAddr, handler))
}
