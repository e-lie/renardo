export interface AbletonStatusInterface {
  status: 'stopped' | 'running' | 'error'
  message: string
}

export interface AbletonStateInterface {
  status: AbletonStatusInterface
  startupEnabled: boolean
  isLoading: boolean
  error: string | null
}
