export interface InitLogEntry {
  id: string
  level: string
  message: string
}

export interface InitializationStateInterface {
  loading: boolean
  userDirConfigured: boolean
  userDir: string | null
  samplesInitialized: boolean
  sccodeInitialized: boolean
  downloading: boolean
  downloadComplete: boolean
  downloadError: string | null
  initLogs: InitLogEntry[]
}
