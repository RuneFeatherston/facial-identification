import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import AuthForm from '../AuthForm'

describe('AuthForm', () => {
  describe('when user submits valid username', () => {
    it('should call onStartAuth with trimmed username', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const validUsername = 'john.doe'
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const usernameInput = screen.getByLabelText(/username/i)
      const submitButton = screen.getByRole('button', { name: /start authentication/i })
      
      await user.type(usernameInput, validUsername)
      await user.click(submitButton)
      
      // Assert
      expect(mockOnStartAuth).toHaveBeenCalledOnce()
      expect(mockOnStartAuth).toHaveBeenCalledWith(validUsername)
    })

    it('should trim whitespace from username before submitting', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const usernameWithWhitespace = '  john.doe  '
      const expectedTrimmedUsername = 'john.doe'
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const usernameInput = screen.getByLabelText(/username/i)
      await user.type(usernameInput, usernameWithWhitespace)
      await user.click(screen.getByRole('button', { name: /start authentication/i }))
      
      // Assert
      expect(mockOnStartAuth).toHaveBeenCalledWith(expectedTrimmedUsername)
    })
  })

  describe('when user submits empty username', () => {
    it('should not call onStartAuth with empty string', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const submitButton = screen.getByRole('button', { name: /start authentication/i })
      await user.click(submitButton)
      
      // Assert
      expect(mockOnStartAuth).not.toHaveBeenCalled()
    })

    it('should not call onStartAuth with only whitespace', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const whitespaceOnlyUsername = '   '
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const usernameInput = screen.getByLabelText(/username/i)
      await user.type(usernameInput, whitespaceOnlyUsername)
      await user.click(screen.getByRole('button', { name: /start authentication/i }))
      
      // Assert
      expect(mockOnStartAuth).not.toHaveBeenCalled()
    })
  })

  describe('form interaction behavior', () => {
    it('should disable submit button when username is empty', () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      
      // Act
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Assert
      const submitButton = screen.getByRole('button', { name: /start authentication/i })
      expect(submitButton).toBeDisabled()
    })

    it('should enable submit button when username has content', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const usernameInput = screen.getByLabelText(/username/i)
      await user.type(usernameInput, 'john')
      
      // Assert
      const submitButton = screen.getByRole('button', { name: /start authentication/i })
      expect(submitButton).toBeEnabled()
    })

    it('should focus username input on mount', () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      
      // Act
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Assert
      const usernameInput = screen.getByLabelText(/username/i)
      expect(usernameInput).toHaveFocus()
    })
  })

  describe('keyboard navigation', () => {
    it('should submit form when Enter key is pressed', async () => {
      // Arrange
      const mockOnStartAuth = vi.fn()
      const validUsername = 'alice.smith'
      const user = userEvent.setup()
      
      render(<AuthForm onStartAuth={mockOnStartAuth} />)
      
      // Act
      const usernameInput = screen.getByLabelText(/username/i)
      await user.type(usernameInput, validUsername)
      await user.keyboard('{Enter}')
      
      // Assert
      expect(mockOnStartAuth).toHaveBeenCalledWith(validUsername)
    })
  })
})
