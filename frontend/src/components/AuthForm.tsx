import { useState } from 'react'
import { AuthFormProps } from '../types'

const AuthForm: React.FC<AuthFormProps> = ({ onStartAuth }) => {
  const [username, setUsername] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onStartAuth(username.trim())
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="input-group">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your username"
          required
          autoFocus
        />
      </div>
      <button type="submit" disabled={!username.trim()}>
        Start Authentication
      </button>
    </form>
  )
}

export default AuthForm
