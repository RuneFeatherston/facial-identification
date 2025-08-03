import { useState } from 'react'

interface FaceEntry {
  id: string
  createdAt: string
  quality: 'high' | 'medium' | 'low'
  isActive: boolean
}

interface UserProfile {
  username: string
  fullName: string
  email: string
  joinDate: string
  faceEntries: FaceEntry[]
}

interface UserDashboardProps {
  username: string
  token: string
  onLogout: () => void
  onRescanFace: () => void
}

export default function UserDashboard({ username, token, onLogout, onRescanFace }: UserDashboardProps) {
  // Mock user data - in real app this would come from API using the token
  const [userProfile] = useState<UserProfile>({
    username: username,
    fullName: getFullNameForUser(username), // Mock function
    email: `${username}@company.com`,
    joinDate: '2024-01-15',
    faceEntries: [
      {
        id: 'face_001',
        createdAt: '2024-01-15T10:30:00Z',
        quality: 'high',
        isActive: true
      },
      {
        id: 'face_002', 
        createdAt: '2024-02-10T14:20:00Z',
        quality: 'medium',
        isActive: true
      }
    ]
  })

  const [showToken, setShowToken] = useState(false)

  const handleDeleteFaceEntry = (faceId: string) => {
    if (confirm('Are you sure you want to delete this face entry? This action cannot be undone.')) {
      // In real app, this would call an API to delete the face entry
      console.log(`Deleting face entry: ${faceId}`)
      // Update local state or refetch data
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'high': return '#10b981' // green
      case 'medium': return '#f59e0b' // yellow
      case 'low': return '#ef4444' // red
      default: return '#6b7280' // gray
    }
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h2>Welcome back, {userProfile.fullName}!</h2>
          <p className="subtitle">@{userProfile.username}</p>
        </div>
        <button onClick={onLogout} className="logout-btn">
          Logout
        </button>
      </div>

      {/* User Info Card */}
      <div className="card">
        <h3>Profile Information</h3>
        <div className="profile-info">
          <div className="info-item">
            <label>Full Name:</label>
            <span>{userProfile.fullName}</span>
          </div>
          <div className="info-item">
            <label>Username:</label>
            <span>{userProfile.username}</span>
          </div>
          <div className="info-item">
            <label>Email:</label>
            <span>{userProfile.email}</span>
          </div>
          <div className="info-item">
            <label>Member Since:</label>
            <span>{formatDate(userProfile.joinDate)}</span>
          </div>
        </div>
      </div>

      {/* Authentication Token */}
      <div className="card">
        <h3>Authentication Token</h3>
        <div className="token-section">
          <button 
            onClick={() => setShowToken(!showToken)}
            className="toggle-token-btn"
          >
            {showToken ? 'Hide Token' : 'Show Token'}
          </button>
          {showToken && (
            <div className="token-display">
              <code>{token}</code>
              <button 
                onClick={() => navigator.clipboard.writeText(token)}
                className="copy-btn"
              >
                Copy
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Face Management */}
      <div className="card">
        <div className="card-header">
          <h3>Face Recognition Entries</h3>
          <button onClick={onRescanFace} className="rescan-btn">
            + Add New Face Scan
          </button>
        </div>
        
        <div className="face-entries">
          {userProfile.faceEntries.map((entry) => (
            <div key={entry.id} className="face-entry">
              <div className="face-entry-info">
                <div className="face-entry-id">ID: {entry.id}</div>
                <div className="face-entry-date">
                  Added: {formatDate(entry.createdAt)}
                </div>
                <div className="face-entry-quality">
                  <span 
                    className="quality-badge"
                    style={{ backgroundColor: getQualityColor(entry.quality) }}
                  >
                    {entry.quality.toUpperCase()} QUALITY
                  </span>
                  <span className={`status ${entry.isActive ? 'active' : 'inactive'}`}>
                    {entry.isActive ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </div>
              </div>
              <div className="face-entry-actions">
                <button 
                  onClick={() => handleDeleteFaceEntry(entry.id)}
                  className="delete-btn"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {userProfile.faceEntries.length === 0 && (
          <div className="no-entries">
            <p>No face entries found. Add your first face scan to get started.</p>
            <button onClick={onRescanFace} className="rescan-btn primary">
              Add Face Scan
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// Mock function to get full name - in real app this would come from database
function getFullNameForUser(username: string): string {
  const mockNames: Record<string, string> = {
    'rr': 'Robert Rodriguez',
    'runef': 'Rune Frandsen',
    'admin': 'Administrator',
    'john': 'John Doe',
    'jane': 'Jane Smith',
    'test': 'Test User'
  }
  
  return mockNames[username] || `${username.charAt(0).toUpperCase()}${username.slice(1)} User`
}
