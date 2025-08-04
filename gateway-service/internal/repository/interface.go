package repository

import (
	"time"

	"gateway-service/internal/models"
)

// UserRepositoryInterface defines the interface for user repository operations
type UserRepositoryInterface interface {
	CreateUser(username, fullName, email string) (*models.User, error)
	GetUserByUsername(username string) (*models.User, error)
	GetUserProfile(username string) (*models.UserProfile, error)
	CreateFaceEntry(userID string, embedding []byte, quality string) (*models.FaceEntry, error)
	GetFaceEntriesByUserID(userID string) ([]models.FaceEntry, error)
	GetFaceEmbeddingsForUser(userID string) ([][]byte, error)
	CreateAuthSession(userID, token string, expiresAt time.Time) (*models.AuthSession, error)
	ValidateAuthSession(token string) (*models.AuthSession, error)
}
