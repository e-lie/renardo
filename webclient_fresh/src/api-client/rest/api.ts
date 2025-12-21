const API_URL = 'http://localhost:8000'

export interface ExecuteCodeResponse {
  success: boolean
  message: string
  output?: string | null
}

export async function executeCode(code: string): Promise<ExecuteCodeResponse> {
  const response = await fetch(`${API_URL}/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code }),
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

class ApiClient {
  async get(url: string): Promise<any> {
    const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // Handle plain text responses
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('text/plain')) {
      return { data: await response.text() }
    }

    return await response.json()
  }

  async post(url: string, data: any): Promise<any> {
    const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`
    
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  }
}

export const apiClient = new ApiClient()
