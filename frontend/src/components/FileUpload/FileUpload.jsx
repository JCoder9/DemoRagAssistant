import { useState, useRef, useEffect } from 'react'
import apiService from '../../services/api'
import './FileUpload.css'

function FileUpload({ onUploadSuccess, onUploadError }) {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [removing, setRemoving] = useState(null)
  const fileInputRef = useRef(null)

  // Fetch uploaded files on component mount
  useEffect(() => {
    const fetchUploadedFiles = async () => {
      try {
        const result = await apiService.getUploadedFiles()
        if (result.files && result.files.length > 0) {
          const files = result.files.map(filename => ({
            name: filename,
            type: filename.endsWith('.pdf') ? 'application/pdf' : 'text/plain',
            uploadedAt: null
          }))
          setUploadedFiles(files)
        }
      } catch (error) {
        console.error('Failed to fetch uploaded files:', error)
      }
    }
    
    fetchUploadedFiles()
  }, [])

  const handleFile = async (file) => {
    if (!file) return

    const allowedTypes = ['application/pdf', 'text/plain']
    if (!allowedTypes.includes(file.type)) {
      onUploadError('Only PDF and TXT files are supported')
      return
    }

    setUploading(true)
    try {
      const result = await apiService.uploadFile(file)
      setUploadedFiles(prev => [...prev, { name: file.name, type: file.type, uploadedAt: new Date() }])
      onUploadSuccess(result.message || 'File uploaded successfully', result.uploads_remaining)
    } catch (error) {
      onUploadError(error.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleFileInput = (e) => {
    const file = e.target.files?.[0]
    handleFile(file)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = async (filename, index) => {
    setRemoving(filename)
    try {
      await apiService.deleteDocument(filename)
      setUploadedFiles(prev => prev.filter((_, i) => i !== index))
      onUploadSuccess(`Removed ${filename}`)
    } catch (error) {
      onUploadError(error.message)
    } finally {
      setRemoving(null)
    }
  }

  return (
    <div className="file-upload-container">
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt"
        onChange={handleFileInput}
        disabled={uploading}
        style={{ display: 'none' }}
      />
      
        {uploading ? (
          <div className="upload-content">
            <div className="spinner"></div>
            <span>Uploading...</span>
          </div>
        ) : (
          <div className="upload-content">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <span>Drop file or click to upload</span>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          {uploadedFiles.map((file, index) => (
            <div key={index} className="uploaded-file-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <span className="file-name">{file.name}</span>
              <button
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  handleRemove(file.name, index)
                }}
                disabled={removing === file.name}
                aria-label={`Remove ${file.name}`}
              >
                {removing === file.name ? '...' : '×'}
              </button>
            </div>
          ))}
        </div>
      )}
      
    </div>
  )
}

export default FileUpload
