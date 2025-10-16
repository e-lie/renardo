import type { LogEntryInterface } from '../../../models/logs'

export interface LogsStateInterface {
  loading: boolean
  logs: LogEntryInterface[]
  filterLevel: string | null
}
