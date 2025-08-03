import { ConnectionStatusProps } from '../types'

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status }) => {
  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'connecting':
        return 'Connecting...'
      case 'disconnected':
        return 'Disconnected'
      default:
        return 'Unknown'
    }
  }

  const getStatusClass = () => {
    switch (status) {
      case 'connected':
        return 'connected'
      case 'connecting':
        return 'authenticating'
      case 'disconnected':
        return 'disconnected'
      default:
        return 'disconnected'
    }
  }

  return (
    <div style={{ marginBottom: '1rem', textAlign: 'left' }}>
      <span className={`status-indicator ${getStatusClass()}`}></span>
      <span>{getStatusText()}</span>
    </div>
  )
}

export default ConnectionStatus
