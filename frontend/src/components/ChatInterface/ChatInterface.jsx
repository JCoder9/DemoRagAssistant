import { useState } from 'react'
import apiService from '../../services/api'
import FileUpload from '../FileUpload'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const [notification, setNotification] = useState(null)

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const handleUploadSuccess = (message) => {
    showNotification(message, 'success')
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
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Demo RAG Assistant</h1>
        <p>Ask questions about your documents</p>
      </div>

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}

      <div className="upload-section">
        <FileUpload 
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
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
      </div>

      <form className="input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
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
