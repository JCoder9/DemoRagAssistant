import { useState, useRef, useEffect } from 'react'
import apiService from '../../services/api'
import FileUpload from '../FileUpload'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const [notification, setNotification] = useState(null)
  const [uploadsRemaining, setUploadsRemaining] = useState(null)
  const [isFirstRequest, setIsFirstRequest] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type })
    const timeout = type === 'error' ? 15000 : 4000
    setTimeout(() => setNotification(null), timeout)
  }

  const handleUploadSuccess = (message, uploadsLeft) => {
    showNotification(message, 'success')
    if (uploadsLeft !== undefined) {
      setUploadsRemaining(uploadsLeft)
    }
  }

  const handleUploadError = (message) => {
    showNotification(message, 'error')
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    const question = input
    setInput('')
    setLoading(true)

    // Show cold start warning on first request
    if (isFirstRequest) {
      showNotification('First request may take 30-60 seconds as the free-tier server wakes up...', 'info')
      setIsFirstRequest(false)
    }

    try {
      const data = await apiService.query(question, sessionId)
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: error.message,
      }
      setMessages(prev => [...prev, errorMessage])
      
      // Show helpful message for timeout errors
      if (error.message.includes('timeout') || error.message.includes('failed to fetch')) {
        showNotification('Free-tier server is waking up. Please try again in a few seconds.', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Demo RAG Assistant</h1>
        <p>Ask questions about your documents (PDF & TXT files)</p>
      </div>

      {notification && (
        <div className={`notification ${notification.type}`}>
          <span>{notification.message}</span>
          <button 
            className="notification-close" 
            onClick={() => setNotification(null)}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      )}

      <div className="upload-section">
        <FileUpload 
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
        {uploadsRemaining !== null && (
          <div className="usage-indicator">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <span>{uploadsRemaining} upload{uploadsRemaining !== 1 ? 's' : ''} remaining this session</span>
          </div>
        )}
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>Start a conversation</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <details>
                    <summary>{msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}</summary>
                    {msg.sources.map((source, i) => (
                      <div key={i} className="source-item">
                        <small>{source.text.substring(0, 100)}...</small>
                      </div>
                    ))}
                  </details>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={sendMessage}>
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
          />
          <div className="usage-indicator-inline">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <span>10/hr • 30/day limits</span>
          </div>
        </div>
        <button type="submit" disabled={loading || !input.trim()}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  )
}

export default ChatInterface
