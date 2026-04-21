import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import FileUpload from './FileUpload'

global.fetch = vi.fn()

describe('FileUpload', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()

  beforeEach(() => {
    fetch.mockClear()
    mockOnSuccess.mockClear()
    mockOnError.mockClear()
    
    // Mock getUploadedFiles call on mount
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ files: [], count: 0 })
    })
  })

  it('renders upload zone with correct text', () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    expect(screen.getByText(/Drop file or click to upload/i)).toBeInTheDocument()
  })

  it('shows error for invalid file type', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    const file = new File(['content'], 'test.exe', { type: 'application/x-msdownload' })
    const input = document.querySelector('input[type="file"]')

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Only PDF and TXT files are supported')
    })
  })

  it('calls onUploadSuccess when upload succeeds', async () => {
    // Additional mock for the upload API call
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Upload successful', uploads_remaining: 4 })
    })

    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]')

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('Upload successful', 4)
    })
  })

  it('calls onUploadError when upload fails', async () => {
    // Additional mock for the upload API call
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'File too large' })
    })

    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]')

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('File too large')
    })
  })

  it('shows uploading state during upload', async () => {
    let resolveUpload
    const uploadPromise = new Promise(resolve => { resolveUpload = resolve })

    // Additional mock for the upload API call
    fetch.mockReturnValueOnce(uploadPromise.then(() => ({
      ok: true,
      json: async () => ({ message: 'Success', uploads_remaining: 4 })
    })))

    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const input = document.querySelector('input[type="file"]')

    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/Uploading.../i)).toBeInTheDocument()
    })

    resolveUpload()
  })
})
