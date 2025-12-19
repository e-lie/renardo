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
