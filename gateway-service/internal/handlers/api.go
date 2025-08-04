package handlers

import (
	"encoding/json"
	"net/http"

	"gateway-service/internal/repository"
)

// APIHandlers provides HTTP API endpoints
type APIHandlers struct {
	userRepo repository.UserRepositoryInterface
}

// NewAPIHandlers creates a new API handlers instance
func NewAPIHandlers(userRepo repository.UserRepositoryInterface) *APIHandlers {
	return &APIHandlers{
		userRepo: userRepo,
	}
}

// HealthHandler handles health check requests
func (h *APIHandlers) HealthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	response := map[string]interface{}{
		"status":  "healthy",
		"service": "gateway-service",
	}
	json.NewEncoder(w).Encode(response)
}

// GetUserProfileHandler retrieves user profile with face entries
func (h *APIHandlers) GetUserProfileHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	username := r.URL.Query().Get("username")
	if username == "" {
		http.Error(w, `{"error":"Username parameter is required"}`, http.StatusBadRequest)
		return
	}

	profile, err := h.userRepo.GetUserProfile(username)
	if err != nil {
		http.Error(w, `{"error":"User not found"}`, http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(profile)
}

// CORS middleware
func (h *APIHandlers) CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*") // Allow all origins for testing
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}
