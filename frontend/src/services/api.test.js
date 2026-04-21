import { describe, it, expect, vi, beforeEach } from 'vitest'
import apiService from '../services/api'

global.fetch = vi.fn()

describe('ApiService', () => {
  beforeEach(() => {
    fetch.mockClear()
  })

  describe('query', () => {
    it('sends query request with correct payload', async () => {
      const mockResponse = {
        answer: 'Test answer',
        sources: []
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await apiService.query('test question', 'session-123')

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/query'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: 'test question',
            session_id: 'session-123'
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Query failed' })
      })

      await expect(
        apiService.query('test', 'session-123')
      ).rejects.toThrow('Query failed')
    })
  })

  describe('uploadFile', () => {
    it('uploads file with FormData', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      const mockResponse = { message: 'Upload successful' }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await apiService.uploadFile(mockFile)

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/upload'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('throws error on upload failure', async () => {
      const mockFile = new File(['content'], 'test.pdf')
      
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'File too large' })
      })

      await expect(
        apiService.uploadFile(mockFile)
      ).rejects.toThrow('File too large')
    })
  })
})
