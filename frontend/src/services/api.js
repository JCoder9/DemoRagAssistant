import config from '../config'

class ApiService {
  async query(question, sessionId) {
    const response = await fetch(`${config.apiUrl}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${config.apiUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload failed')
    }

    return response.json()
  }
}

export default new ApiService()
