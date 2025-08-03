import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import VideoStream from '../VideoStream'

// Create mocks at module level
const mockGetUserMedia = vi.fn()
const mockVideoTrack = {
  stop: vi.fn(),
  kind: 'video',
  enabled: true,
}

const mockStream = {
  getTracks: () => [mockVideoTrack],
}

// Mock navigator.mediaDevices at module level
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: mockGetUserMedia,
  },
  writable: true,
  configurable: true,
})

beforeEach(() => {
  // Reset mocks
  vi.clearAllMocks()
  mockGetUserMedia.mockResolvedValue(mockStream)

  // Mock video element properties
  Object.defineProperty(HTMLVideoElement.prototype, 'videoWidth', {
    value: 640,
    writable: true,
    configurable: true,
  })
  
  Object.defineProperty(HTMLVideoElement.prototype, 'videoHeight', {
    value: 480,
    writable: true,
    configurable: true,
  })

  Object.defineProperty(HTMLVideoElement.prototype, 'readyState', {
    value: 4, // HAVE_ENOUGH_DATA
    writable: true,
    configurable: true,
  })

  // Mock canvas context
  const mockContext = {
    drawImage: vi.fn(),
    fillRect: vi.fn(),
    clearRect: vi.fn(),
  }

  HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext) as any

  // Mock canvas toBlob
  HTMLCanvasElement.prototype.toBlob = vi.fn((callback: BlobCallback) => {
    const mockBlob = new Blob(['mock image data'], { type: 'image/jpeg' })
    callback(mockBlob)
  })
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('VideoStream', () => {
  const defaultProps = {
    onVideoData: vi.fn(),
    username: 'testuser',
    isActive: true,
  }

  describe('when component mounts', () => {
    it('should request camera access with correct constraints', async () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      await waitFor(() => {
        expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          },
          audio: false
        })
      })
    })

    it('should display camera starting message initially', () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      expect(screen.getByText(/starting camera/i)).toBeInTheDocument()
    })

    it('should display camera active status when stream starts', async () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/camera active/i)).toBeInTheDocument()
      })
    })
  })

  describe('when camera access fails', () => {
    it('should display error message when getUserMedia fails', async () => {
      // Arrange
      navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error('Camera access denied'))

      // Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/unable to access camera/i)).toBeInTheDocument()
        expect(screen.getByText(/check permissions/i)).toBeInTheDocument()
      })
    })

    it('should provide retry button when camera fails', async () => {
      // Arrange
      navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error('Access denied'))

      // Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
      })
    })
  })

  describe('video element properties', () => {
    it('should render video element with correct attributes', () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      const videoElement = document.querySelector('video')
      expect(videoElement).toBeInTheDocument()
      expect(videoElement).toHaveAttribute('autoPlay')
      expect(videoElement).toHaveAttribute('playsInline')
      expect(videoElement).toHaveAttribute('muted')
    })

    it('should render hidden canvas element', () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} />)

      // Assert
      const canvasElement = document.querySelector('canvas')
      expect(canvasElement).toBeInTheDocument()
      expect(canvasElement).toHaveStyle({ display: 'none' })
    })
  })

  describe('prop handling', () => {
    it('should handle missing username gracefully', async () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} username={undefined} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/camera active/i)).toBeInTheDocument()
      })
    })

    it('should handle isActive false without crashing', async () => {
      // Arrange & Act
      render(<VideoStream {...defaultProps} isActive={false} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/camera active/i)).toBeInTheDocument()
      })
    })
  })
})
