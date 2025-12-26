import type { ConsoleMessageInterface } from '../../../models/console'

export interface ConsoleStateInterface {
  messages: ConsoleMessageInterface[]
  isMinimized: boolean
}
