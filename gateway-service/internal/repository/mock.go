package repository

import (
	"fmt"
	"time"

	"gateway-service/internal/models"
)

// MockUserRepository implements UserRepositoryInterface for testing
type MockUserRepository struct {
	users        map[string]*models.User
	faceEntries  map[string][]models.FaceEntry
	authSessions map[string]*models.AuthSession
}

// Ensure MockUserRepository implements the interface
var _ UserRepositoryInterface = (*MockUserRepository)(nil)

// NewMockUserRepository creates a new mock repository with test data
func NewMockUserRepository() *MockUserRepository {
	mock := &MockUserRepository{
		users:        make(map[string]*models.User),
		faceEntries:  make(map[string][]models.FaceEntry),
		authSessions: make(map[string]*models.AuthSession),
	}

	// Pre-populate with test data
	testUser := &models.User{
		ID:        "test-user-id-123",
		Username:  "testuser",
		FullName:  "Test User",
		Email:     "test@example.com",
		JoinDate:  time.Now().AddDate(0, -1, 0), // 1 month ago
		CreatedAt: time.Now().AddDate(0, -1, 0),
		UpdatedAt: time.Now(),
	}
	mock.users["testuser"] = testUser

	// Add test face entries
	mock.faceEntries[testUser.ID] = []models.FaceEntry{
		{
			ID:        "face-entry-1",
			UserID:    testUser.ID,
			Embedding: []byte("mock-embedding-data-1"),
			Quality:   "high",
			IsActive:  true,
			CreatedAt: time.Now().AddDate(0, 0, -7), // 1 week ago
			UpdatedAt: time.Now().AddDate(0, 0, -7),
		},
		{
			ID:        "face-entry-2",
			UserID:    testUser.ID,
			Embedding: []byte("mock-embedding-data-2"),
			Quality:   "medium",
			IsActive:  true,
			CreatedAt: time.Now().AddDate(0, 0, -3), // 3 days ago
			UpdatedAt: time.Now().AddDate(0, 0, -3),
		},
	}

	return mock
}

func (m *MockUserRepository) CreateUser(username, fullName, email string) (*models.User, error) {
	if _, exists := m.users[username]; exists {
		return nil, fmt.Errorf("user already exists: %s", username)
	}

	user := &models.User{
		ID:        fmt.Sprintf("mock-user-id-%s", username),
		Username:  username,
		FullName:  fullName,
		Email:     email,
		JoinDate:  time.Now(),
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	m.users[username] = user
	return user, nil
}

func (m *MockUserRepository) GetUserByUsername(username string) (*models.User, error) {
	if user, exists := m.users[username]; exists {
		return user, nil
	}
	return nil, fmt.Errorf("user not found: %s", username)
}

func (m *MockUserRepository) GetUserProfile(username string) (*models.UserProfile, error) {
	user, err := m.GetUserByUsername(username)
	if err != nil {
		return nil, err
	}

	faceEntries := m.faceEntries[user.ID]
	if faceEntries == nil {
		faceEntries = []models.FaceEntry{}
	}

	return &models.UserProfile{
		User:        *user,
		FaceEntries: faceEntries,
	}, nil
}

func (m *MockUserRepository) CreateFaceEntry(userID string, embedding []byte, quality string) (*models.FaceEntry, error) {
	entry := &models.FaceEntry{
		ID:        fmt.Sprintf("mock-face-entry-%d", time.Now().UnixNano()),
		UserID:    userID,
		Embedding: embedding,
		Quality:   quality,
		IsActive:  true,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if m.faceEntries[userID] == nil {
		m.faceEntries[userID] = []models.FaceEntry{}
	}
	m.faceEntries[userID] = append(m.faceEntries[userID], *entry)

	return entry, nil
}

func (m *MockUserRepository) GetFaceEntriesByUserID(userID string) ([]models.FaceEntry, error) {
	entries := m.faceEntries[userID]
	if entries == nil {
		return []models.FaceEntry{}, nil
	}
	return entries, nil
}

func (m *MockUserRepository) GetFaceEmbeddingsForUser(userID string) ([][]byte, error) {
	entries := m.faceEntries[userID]
	var embeddings [][]byte
	for _, entry := range entries {
		if entry.IsActive {
			embeddings = append(embeddings, entry.Embedding)
		}
	}
	return embeddings, nil
}

func (m *MockUserRepository) CreateAuthSession(userID, token string, expiresAt time.Time) (*models.AuthSession, error) {
	session := &models.AuthSession{
		ID:        fmt.Sprintf("mock-session-%d", time.Now().UnixNano()),
		UserID:    userID,
		Token:     token,
		ExpiresAt: expiresAt,
		CreatedAt: time.Now(),
		IsActive:  true,
	}
	m.authSessions[token] = session
	return session, nil
}

func (m *MockUserRepository) ValidateAuthSession(token string) (*models.AuthSession, error) {
	if session, exists := m.authSessions[token]; exists {
		if session.IsActive && session.ExpiresAt.After(time.Now()) {
			return session, nil
		}
	}
	return nil, fmt.Errorf("invalid or expired token")
}
