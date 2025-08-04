package mlservice

import (
	"fmt"
)

// MockClient implements Interface for testing
type MockClient struct {
	shouldFail bool
	responses  map[string]*ExtractEmbeddingResponse
}

// NewMockClient creates a new mock ML service client
func NewMockClient() *MockClient {
	return &MockClient{
		shouldFail: false,
		responses:  make(map[string]*ExtractEmbeddingResponse),
	}
}

// SetShouldFail configures the mock to simulate failures
func (m *MockClient) SetShouldFail(fail bool) {
	m.shouldFail = fail
}

// SetResponse configures a specific response for a test key
func (m *MockClient) SetResponse(key string, response *ExtractEmbeddingResponse) {
	m.responses[key] = response
}

// ExtractEmbedding simulates ML service face embedding extraction
func (m *MockClient) ExtractEmbedding(imageData []byte) (*ExtractEmbeddingResponse, error) {
	if m.shouldFail {
		return nil, fmt.Errorf("mock ML service failure")
	}

	// Check if we have a pre-configured response
	if response, exists := m.responses["default"]; exists {
		return response, nil
	}

	// Default successful response
	return &ExtractEmbeddingResponse{
		Success:   true,
		Embedding: []float64{0.1, 0.2, 0.3, 0.4, 0.5}, // Mock embedding
		Quality:   "high",
		Message:   "Mock embedding extracted successfully",
	}, nil
}

// AuthenticateUser simulates ML service authentication
func (m *MockClient) AuthenticateUser(testEmbedding []float64, storedEmbeddings [][]float64) (*AuthenticateResponse, error) {
	if m.shouldFail {
		return nil, fmt.Errorf("mock ML service failure")
	}

	// Simulate authentication logic
	// For testing, we'll say authentication succeeds if we have stored embeddings
	success := len(storedEmbeddings) > 0
	confidence := 0.0
	if success {
		confidence = 0.88 // Mock confidence score
	}

	return &AuthenticateResponse{
		Success:         success,
		IsAuthenticated: success,
		Confidence:      confidence,
		Message:         "Mock authentication completed",
	}, nil
}

// Health simulates ML service health check
func (m *MockClient) Health() error {
	if m.shouldFail {
		return fmt.Errorf("mock ML service is unhealthy")
	}
	return nil
}
