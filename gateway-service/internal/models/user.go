package models

import (
	"time"
)

// User represents a user in the system
type User struct {
	ID        string    `json:"id" db:"id"`
	Username  string    `json:"username" db:"username"`
	FullName  string    `json:"fullName" db:"full_name"`
	Email     string    `json:"email" db:"email"`
	JoinDate  time.Time `json:"joinDate" db:"join_date"`
	CreatedAt time.Time `json:"createdAt" db:"created_at"`
	UpdatedAt time.Time `json:"updatedAt" db:"updated_at"`
}

// FaceEntry represents a stored face embedding for a user
type FaceEntry struct {
	ID        string    `json:"id" db:"id"`
	UserID    string    `json:"userId" db:"user_id"`
	Embedding []byte    `json:"-" db:"embedding"`     // Binary face embedding data (not exposed in JSON)
	Quality   string    `json:"quality" db:"quality"` // "high", "medium", "low"
	IsActive  bool      `json:"isActive" db:"is_active"`
	CreatedAt time.Time `json:"createdAt" db:"created_at"`
	UpdatedAt time.Time `json:"updatedAt" db:"updated_at"`
}

// AuthSession represents an active authentication session
type AuthSession struct {
	ID        string    `json:"id" db:"id"`
	UserID    string    `json:"userId" db:"user_id"`
	Token     string    `json:"token" db:"token"`
	ExpiresAt time.Time `json:"expiresAt" db:"expires_at"`
	CreatedAt time.Time `json:"createdAt" db:"created_at"`
	IsActive  bool      `json:"isActive" db:"is_active"`
}

// UserProfile represents the complete user profile with face entries
type UserProfile struct {
	User        User        `json:"user"`
	FaceEntries []FaceEntry `json:"faceEntries"`
}
