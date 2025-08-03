import { useRef, useEffect, useState, useCallback } from 'react'
import { VideoFrameMetadata } from '../types'

interface VideoStreamProps {
  onVideoData: (frameData: ArrayBuffer, metadata: VideoFrameMetadata) => void
  username?: string
  isActive?: boolean
}

const VideoStream: React.FC<VideoStreamProps> = ({ onVideoData, username = '', isActive = true }) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const frameCountRef = useRef<number>(0)
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const captureFrame = useCallback(() => {
    const video = videoRef.current
    const canvas = canvasRef.current

    if (video && canvas && video.readyState === video.HAVE_ENOUGH_DATA && isActive) {
      const context = canvas.getContext('2d')
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)

        // Convert canvas to blob, then to ArrayBuffer with metadata
        canvas.toBlob((blob) => {
          if (blob) {
            blob.arrayBuffer().then(buffer => {
              const metadata: VideoFrameMetadata = {
                username: username,
                frameNumber: frameCountRef.current++,
                timestamp: Date.now(),
                width: canvas.width,
                height: canvas.height,
                format: 'jpeg'
              }
              
              onVideoData(buffer, metadata)
            })
          }
        }, 'image/jpeg', 0.8) // JPEG with 80% quality for good balance
      }
    }
  }, [isActive, username, onVideoData])

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setIsStreaming(true)
        setError(null)

        // Start capturing frames every 500ms (2 FPS) to avoid overwhelming the connection
        if (isActive) {
          intervalRef.current = setInterval(captureFrame, 500)
        }
      }
    } catch (err) {
      console.error('Error accessing camera:', err)
      setError('Unable to access camera. Please check permissions.')
    }
  }, [isActive, captureFrame])

  const stopCamera = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null
    }

    setIsStreaming(false)
  }

  useEffect(() => {
    startCamera()

    return () => {
      stopCamera()
    }
  }, [startCamera])

  useEffect(() => {
    // Start/stop frame capture based on isActive
    if (isActive && isStreaming && !intervalRef.current) {
      intervalRef.current = setInterval(captureFrame, 500)
    } else if (!isActive && intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [isActive, isStreaming, captureFrame])

  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <button onClick={startCamera}>Retry</button>
      </div>
    )
  }

  return (
    <div className="video-container">
      <video
        ref={videoRef}
        className="video-stream"
        autoPlay
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        style={{ display: 'none' }}
      />
      <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>
        {isStreaming ? (
          <span>📹 Camera active - Streaming frames {isActive ? `(Frame #${frameCountRef.current})` : '(Paused)'}</span>
        ) : (
          <span>📷 Starting camera...</span>
        )}
      </div>
    </div>
  )
}

export default VideoStream
