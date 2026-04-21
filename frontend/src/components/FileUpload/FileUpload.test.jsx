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
  })

  it('renders upload zone with correct text', () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    )

    expect(screen.getByText(/Drop a file or click to upload/i)).toBeInTheDocument()
    expect(screen.getByText(/PDF or TXT files only/i)).toBeInTheDocument()
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
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Upload successful' })
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
      expect(mockOnSuccess).toHaveBeenCalledWith('Upload successful')
    })
  })

  it('calls onUploadError when upload fails', async () => {
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

    fetch.mockReturnValueOnce(uploadPromise.then(() => ({
      ok: true,
      json: async () => ({ message: 'Success' })
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
