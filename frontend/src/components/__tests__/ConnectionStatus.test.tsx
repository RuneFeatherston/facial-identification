import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ConnectionStatus from '../ConnectionStatus'

describe('ConnectionStatus', () => {
  describe('when connection is established', () => {
    it('should display connected status text', () => {
      // Arrange
      const connectedStatus = 'connected'
      
      // Act
      render(<ConnectionStatus status={connectedStatus} />)
      
      // Assert
      expect(screen.getByText('Connected')).toBeInTheDocument()
    })
  })

  describe('when connection is in progress', () => {
    it('should display connecting status text', () => {
      // Arrange
      const connectingStatus = 'connecting'
      
      // Act
      render(<ConnectionStatus status={connectingStatus} />)
      
      // Assert
      expect(screen.getByText('Connecting...')).toBeInTheDocument()
    })
  })

  describe('when connection is lost', () => {
    it('should display disconnected status text', () => {
      // Arrange
      const disconnectedStatus = 'disconnected'
      
      // Act
      render(<ConnectionStatus status={disconnectedStatus} />)
      
      // Assert
      expect(screen.getByText('Disconnected')).toBeInTheDocument()
    })
  })

  describe('visual styling behavior', () => {
    it('should apply connected class when connected', () => {
      // Arrange
      const connectedStatus = 'connected'
      
      // Act
      render(<ConnectionStatus status={connectedStatus} />)
      
      // Assert
      const statusIndicator = document.querySelector('.status-indicator.connected')
      expect(statusIndicator).toBeInTheDocument()
    })

    it('should apply authenticating class when connecting', () => {
      // Arrange
      const connectingStatus = 'connecting'
      
      // Act
      render(<ConnectionStatus status={connectingStatus} />)
      
      // Assert
      const statusIndicator = document.querySelector('.status-indicator.authenticating')
      expect(statusIndicator).toBeInTheDocument()
    })

    it('should apply disconnected class when disconnected', () => {
      // Arrange
      const disconnectedStatus = 'disconnected'
      
      // Act
      render(<ConnectionStatus status={disconnectedStatus} />)
      
      // Assert
      const statusIndicator = document.querySelector('.status-indicator.disconnected')
      expect(statusIndicator).toBeInTheDocument()
    })
  })

  describe('edge cases', () => {
    it('should handle unknown status gracefully', () => {
      // Arrange
      const unknownStatus = 'invalid' as unknown as 'connected' | 'disconnected' | 'connecting'
      
      // Act
      render(<ConnectionStatus status={unknownStatus} />)
      
      // Assert
      expect(screen.getByText('Unknown')).toBeInTheDocument()
      const statusIndicator = document.querySelector('.status-indicator.disconnected')
      expect(statusIndicator).toBeInTheDocument()
    })
  })
})
