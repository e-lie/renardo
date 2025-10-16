export interface LogEntryInterface {
  id: string
  timestamp: string
  level: string
  logger: string
  source: string
  message: string
  extra?: string | null
}
