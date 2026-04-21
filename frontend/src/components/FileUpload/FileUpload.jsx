import { useState, useRef } from 'react'
import apiService from '../../services/api'
import './FileUpload.css'

function FileUpload({ onUploadSuccess, onUploadError }) {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

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
      onUploadSuccess(result.message || 'File uploaded successfully')
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

  return (
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
          <p>Uploading...</p>
        </div>
      ) : (
        <div className="upload-content">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p>Drop a file or click to upload</p>
          <small>PDF or TXT files only</small>
        </div>
      )}
    </div>
  )
}

export default FileUpload
