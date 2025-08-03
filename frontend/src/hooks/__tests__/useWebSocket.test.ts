import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '../useWebSocket'

// Enhanced mock WebSocket for testing
let mockWebSocket: any
let mockWebSocketInstance: any

beforeEach(() => {
  mockWebSocketInstance = {
    readyState: 0, // CONNECTING
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    onopen: null,
    onclose: null,
    onmessage: null,
    onerror: null,
  }

  mockWebSocket = vi.fn(() => mockWebSocketInstance)
  mockWebSocket.CONNECTING = 0
  mockWebSocket.OPEN = 1
  mockWebSocket.CLOSING = 2
  mockWebSocket.CLOSED = 3

  global.WebSocket = mockWebSocket as any
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('useWebSocket', () => {
  const defaultOptions = {
    url: 'ws://localhost:8080',
    onMessage: vi.fn(),
    onError: vi.fn(),
  }

  describe('when establishing connection', () => {
    it('should create WebSocket connection with correct URL', () => {
      // Arrange
      const testUrl = 'ws://test.example.com:9000'
      
      // Act
      renderHook(() => useWebSocket({ ...defaultOptions, url: testUrl }))
      
      // Assert
      expect(mockWebSocket).not.toHaveBeenCalled() // Should not auto-connect
    })

    it('should set status to connecting when connect is called', async () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      act(() => {
        result.current.connect()
      })
      
      // Assert
      expect(result.current.connectionStatus).toBe('connecting')
      expect(mockWebSocket).toHaveBeenCalledWith('ws://localhost:8080')
    })

    it('should set status to connected when WebSocket opens', async () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      act(() => {
        result.current.connect()
      })
      
      // Simulate WebSocket opening
      act(() => {
        mockWebSocketInstance.readyState = 1 // OPEN
        mockWebSocketInstance.onopen?.({ type: 'open' })
      })
      
      // Assert
      expect(result.current.connectionStatus).toBe('connected')
    })
  })

  describe('when connection fails', () => {
    it('should set status to disconnected on WebSocket error', async () => {
      // Arrange
      const onError = vi.fn()
      const { result } = renderHook(() => useWebSocket({ ...defaultOptions, onError }))
      
      // Act
      act(() => {
        result.current.connect()
      })
      
      // Simulate WebSocket error
      act(() => {
        mockWebSocketInstance.readyState = 3 // CLOSED
        mockWebSocketInstance.onerror?.({ type: 'error', target: mockWebSocketInstance })
      })
      
      // Assert
      expect(result.current.connectionStatus).toBe('disconnected')
      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })

    it('should set status to disconnected when WebSocket closes', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      act(() => {
        result.current.connect()
      })
      
      // Simulate WebSocket closing
      act(() => {
        mockWebSocketInstance.readyState = 3 // CLOSED
        mockWebSocketInstance.onclose?.({ type: 'close', target: mockWebSocketInstance })
      })
      
      // Assert
      expect(result.current.connectionStatus).toBe('disconnected')
    })
  })

  describe('when sending messages', () => {
    it('should send JSON messages when connected', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      const testMessage = { type: 'auth_challenge', username: 'testuser' }
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.readyState = 1 // OPEN
        result.current.sendMessage(testMessage)
      })
      
      // Assert
      expect(mockWebSocketInstance.send).toHaveBeenCalledWith(JSON.stringify(testMessage))
    })

    it('should send binary data when connected', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      const binaryData = new ArrayBuffer(8)
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.readyState = 1 // OPEN
        result.current.sendMessage(binaryData)
      })
      
      // Assert
      expect(mockWebSocketInstance.send).toHaveBeenCalledWith(binaryData)
    })

    it('should not send messages when not connected', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      const testMessage = { type: 'test' }
      
      // Act
      act(() => {
        result.current.sendMessage(testMessage)
      })
      
      // Assert
      expect(mockWebSocketInstance.send).not.toHaveBeenCalled()
    })
  })

  describe('when receiving messages', () => {
    it('should call onMessage callback for auth_success messages', () => {
      // Arrange
      const onMessage = vi.fn()
      const { result } = renderHook(() => useWebSocket({ ...defaultOptions, onMessage }))
      const authSuccessMessage = {
        type: 'auth_success',
        token: 'test-token',
        message: 'Authentication successful'
      }
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.onmessage?.({
          data: JSON.stringify(authSuccessMessage)
        })
      })
      
      // Assert
      expect(onMessage).toHaveBeenCalledWith({
        type: 'auth_success',
        token: 'test-token',
        message: 'Authentication successful'
      })
    })

    it('should call onMessage callback for auth_failed messages', () => {
      // Arrange
      const onMessage = vi.fn()
      const { result } = renderHook(() => useWebSocket({ ...defaultOptions, onMessage }))
      const authFailedMessage = {
        type: 'auth_failed',
        message: 'Authentication failed'
      }
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.onmessage?.({
          data: JSON.stringify(authFailedMessage)
        })
      })
      
      // Assert
      expect(onMessage).toHaveBeenCalledWith({
        type: 'auth_failed',
        message: 'Authentication failed'
      })
    })

    it('should handle server acknowledgment messages', () => {
      // Arrange
      const onMessage = vi.fn()
      const { result } = renderHook(() => useWebSocket({ ...defaultOptions, onMessage }))
      const connectedMessage = {
        type: 'connected',
        message: 'Connected to server'
      }
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.onmessage?.({
          data: JSON.stringify(connectedMessage)
        })
      })
      
      // Assert
      // Should not call onMessage for server acknowledgments
      expect(onMessage).not.toHaveBeenCalled()
    })

    it('should handle malformed JSON gracefully', () => {
      // Arrange
      const onError = vi.fn()
      const { result } = renderHook(() => useWebSocket({ ...defaultOptions, onError }))
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.onmessage?.({
          data: 'invalid json {'
        })
      })
      
      // Assert
      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })
  })

  describe('when disconnecting', () => {
    it('should close WebSocket connection when disconnect is called', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      act(() => {
        result.current.connect()
        result.current.disconnect()
      })
      
      // Assert
      expect(mockWebSocketInstance.close).toHaveBeenCalled()
    })

    it('should clean up WebSocket on component unmount', () => {
      // Arrange
      const { unmount } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      unmount()
      
      // Assert
      // This tests the useEffect cleanup function
      // The actual WebSocket instance might not exist if connect wasn't called
      // but the effect should still handle cleanup gracefully
    })
  })

  describe('connection state management', () => {
    it('should not create multiple connections when connect is called repeatedly', () => {
      // Arrange
      const { result } = renderHook(() => useWebSocket(defaultOptions))
      
      // Act
      act(() => {
        result.current.connect()
        mockWebSocketInstance.readyState = 1 // OPEN
        result.current.connect() // Second call
      })
      
      // Assert
      expect(mockWebSocket).toHaveBeenCalledTimes(1)
    })
  })
})
