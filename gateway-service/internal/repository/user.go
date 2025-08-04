package repository

import (
	"database/sql"
	"fmt"
	"time"

	"gateway-service/internal/database"
	"gateway-service/internal/models"
)

type UserRepository struct {
	db *database.DB
}

func NewUserRepository(db *database.DB) *UserRepository {
	return &UserRepository{db: db}
}

// CreateUser creates a new user in the database
func (r *UserRepository) CreateUser(username, fullName, email string) (*models.User, error) {
	query := `
		INSERT INTO users (username, full_name, email)
		VALUES ($1, $2, $3)
		RETURNING id, username, full_name, email, join_date, created_at, updated_at`

	var user models.User
	err := r.db.QueryRow(query, username, fullName, email).Scan(
		&user.ID, &user.Username, &user.FullName, &user.Email,
		&user.JoinDate, &user.CreatedAt, &user.UpdatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	return &user, nil
}

// GetUserByUsername retrieves a user by username
func (r *UserRepository) GetUserByUsername(username string) (*models.User, error) {
	query := `
		SELECT id, username, full_name, email, join_date, created_at, updated_at
		FROM users WHERE username = $1`

	var user models.User
	err := r.db.QueryRow(query, username).Scan(
		&user.ID, &user.Username, &user.FullName, &user.Email,
		&user.JoinDate, &user.CreatedAt, &user.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found: %s", username)
		}
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	return &user, nil
}

// GetUserProfile retrieves a complete user profile with face entries
func (r *UserRepository) GetUserProfile(username string) (*models.UserProfile, error) {
	user, err := r.GetUserByUsername(username)
	if err != nil {
		return nil, err
	}

	faceEntries, err := r.GetFaceEntriesByUserID(user.ID)
	if err != nil {
		return nil, err
	}

	return &models.UserProfile{
		User:        *user,
		FaceEntries: faceEntries,
	}, nil
}

// CreateFaceEntry creates a new face entry for a user with embedding data
func (r *UserRepository) CreateFaceEntry(userID string, embedding []byte, quality string) (*models.FaceEntry, error) {
	query := `
		INSERT INTO face_entries (user_id, embedding, quality)
		VALUES ($1, $2, $3)
		RETURNING id, user_id, quality, is_active, created_at, updated_at`

	var entry models.FaceEntry
	err := r.db.QueryRow(query, userID, embedding, quality).Scan(
		&entry.ID, &entry.UserID, &entry.Quality, &entry.IsActive,
		&entry.CreatedAt, &entry.UpdatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("failed to create face entry: %w", err)
	}

	entry.Embedding = embedding
	return &entry, nil
}

// GetFaceEntriesByUserID retrieves all face entries for a user
func (r *UserRepository) GetFaceEntriesByUserID(userID string) ([]models.FaceEntry, error) {
	query := `
		SELECT id, user_id, embedding, quality, is_active, created_at, updated_at
		FROM face_entries WHERE user_id = $1 ORDER BY created_at DESC`

	rows, err := r.db.Query(query, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get face entries: %w", err)
	}
	defer rows.Close()

	var entries []models.FaceEntry
	for rows.Next() {
		var entry models.FaceEntry
		err := rows.Scan(
			&entry.ID, &entry.UserID, &entry.Embedding, &entry.Quality, &entry.IsActive,
			&entry.CreatedAt, &entry.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan face entry: %w", err)
		}
		entries = append(entries, entry)
	}

	return entries, nil
}

// GetFaceEmbeddingsForUser retrieves all active face embeddings for authentication
func (r *UserRepository) GetFaceEmbeddingsForUser(userID string) ([][]byte, error) {
	query := `
		SELECT embedding FROM face_entries 
		WHERE user_id = $1 AND is_active = true 
		ORDER BY created_at DESC`

	rows, err := r.db.Query(query, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get face embeddings: %w", err)
	}
	defer rows.Close()

	var embeddings [][]byte
	for rows.Next() {
		var embedding []byte
		err := rows.Scan(&embedding)
		if err != nil {
			return nil, fmt.Errorf("failed to scan embedding: %w", err)
		}
		embeddings = append(embeddings, embedding)
	}

	return embeddings, nil
}

// CreateAuthSession creates a new authentication session
func (r *UserRepository) CreateAuthSession(userID, token string, expiresAt time.Time) (*models.AuthSession, error) {
	query := `
		INSERT INTO auth_sessions (user_id, token, expires_at)
		VALUES ($1, $2, $3)
		RETURNING id, user_id, token, expires_at, created_at, is_active`

	var session models.AuthSession
	err := r.db.QueryRow(query, userID, token, expiresAt).Scan(
		&session.ID, &session.UserID, &session.Token, &session.ExpiresAt,
		&session.CreatedAt, &session.IsActive,
	)

	if err != nil {
		return nil, fmt.Errorf("failed to create auth session: %w", err)
	}

	return &session, nil
}

// ValidateAuthSession validates an authentication token
func (r *UserRepository) ValidateAuthSession(token string) (*models.AuthSession, error) {
	query := `
		SELECT id, user_id, token, expires_at, created_at, is_active
		FROM auth_sessions 
		WHERE token = $1 AND is_active = true AND expires_at > NOW()`

	var session models.AuthSession
	err := r.db.QueryRow(query, token).Scan(
		&session.ID, &session.UserID, &session.Token, &session.ExpiresAt,
		&session.CreatedAt, &session.IsActive,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("invalid or expired token")
		}
		return nil, fmt.Errorf("failed to validate session: %w", err)
	}

	return &session, nil
}
