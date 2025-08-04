package mlservice

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"
)

// Client handles communication with the ML service
type Client struct {
	baseURL    string
	httpClient *http.Client
}

// ExtractEmbeddingResponse represents the response from embedding extraction
type ExtractEmbeddingResponse struct {
	Success   bool      `json:"success"`
	Embedding []float64 `json:"embedding,omitempty"`
	Quality   string    `json:"quality"`
	Message   string    `json:"message"`
}

// AuthenticateRequest represents an authentication request to ML service
type AuthenticateRequest struct {
	TestEmbedding    []float64   `json:"test_embedding"`
	StoredEmbeddings [][]float64 `json:"stored_embeddings"`
}

// AuthenticateResponse represents an authentication response from ML service
type AuthenticateResponse struct {
	Success         bool    `json:"success"`
	IsAuthenticated bool    `json:"is_authenticated"`
	Confidence      float64 `json:"confidence"`
	BestMatchIndex  *int    `json:"best_match_index,omitempty"`
	Message         string  `json:"message"`
}

// NewClient creates a new ML service client
func NewClient(baseURL string) *Client {
	return &Client{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// ExtractEmbedding extracts face embedding from image data
func (c *Client) ExtractEmbedding(imageData []byte) (*ExtractEmbeddingResponse, error) {
	// Create multipart form data for file upload
	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)

	// Create form file field
	part, err := writer.CreateFormFile("file", "image.jpg")
	if err != nil {
		return nil, fmt.Errorf("failed to create form file: %w", err)
	}

	// Write image data
	if _, err := part.Write(imageData); err != nil {
		return nil, fmt.Errorf("failed to write image data: %w", err)
	}

	// Close the writer
	if err := writer.Close(); err != nil {
		return nil, fmt.Errorf("failed to close multipart writer: %w", err)
	}

	// Send request
	resp, err := c.httpClient.Post(
		c.baseURL+"/extract-embedding",
		writer.FormDataContentType(),
		&buf,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to ML service: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	var response ExtractEmbeddingResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &response, nil
}

// AuthenticateUser compares a test embedding against stored embeddings
func (c *Client) AuthenticateUser(testEmbedding []float64, storedEmbeddings [][]float64) (*AuthenticateResponse, error) {
	req := AuthenticateRequest{
		TestEmbedding:    testEmbedding,
		StoredEmbeddings: storedEmbeddings,
	}

	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := c.httpClient.Post(
		c.baseURL+"/authenticate",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to ML service: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	var response AuthenticateResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &response, nil
}

// Health checks if the ML service is available
func (c *Client) Health() error {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return fmt.Errorf("failed to connect to ML service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("ML service health check failed with status: %d", resp.StatusCode)
	}

	return nil
}
