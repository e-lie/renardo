export type ConsoleMessageLevel = 'info' | 'command' | 'error' | 'success' | 'warn'

export interface ConsoleMessageInterface {
  message: string
  level: ConsoleMessageLevel
  timestamp?: string
}
