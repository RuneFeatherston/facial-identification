package mlservice

// Interface defines the contract for ML service operations
type Interface interface {
	ExtractEmbedding(imageData []byte) (*ExtractEmbeddingResponse, error)
	AuthenticateUser(testEmbedding []float64, storedEmbeddings [][]float64) (*AuthenticateResponse, error)
	Health() error
}

// Ensure Client implements the interface
var _ Interface = (*Client)(nil)
