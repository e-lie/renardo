import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import { GET_HISTORICAL_LOGS, SUBSCRIBE_TO_LOGS } from '../../api-client/graphql/queries'
import type { LogEntryInterface } from '../../models/logs'
import type {
  LogsStateInterface,
  LogsStoreInterface,
  LogsStoreActionsInterface,
  LogsStoreGettersInterface
} from './models'

// Private writable store
const writableLogsStore = writable<LogsStateInterface>({
  loading: false,
  logs: [],
  filterLevel: null
})

// Subscription cleanup function
let unsubscribe: (() => void) | null = null

// Public hook
export function useLogsStore(): LogsStoreInterface {
  const client = getContextClient()

  // Actions: modify state
  const actions: LogsStoreActionsInterface = {
    loadLogs: async (limit = 1000) => {
      writableLogsStore.update(state => ({ ...state, loading: true }))

      try {
        const result = await client.query(GET_HISTORICAL_LOGS, { limit })

        if (result.data?.historicalLogs) {
          writableLogsStore.update(state => ({
            ...state,
            logs: result.data.historicalLogs,
            loading: false
          }))
        } else {
          writableLogsStore.update(state => ({ ...state, loading: false }))
        }
      } catch (error) {
        console.error('Error loading logs:', error)
        writableLogsStore.update(state => ({ ...state, loading: false }))
      }
    },

    setFilterLevel: (level: string | null) => {
      writableLogsStore.update(state => ({ ...state, filterLevel: level }))
    },

    subscribeToLogs: () => {
      // Clean up any existing subscription
      if (unsubscribe) {
        unsubscribe()
      }

      let filterLevel: string | null = null
      const unsubscribeFilter = derived(writableLogsStore, $state => $state.filterLevel).subscribe(
        level => (filterLevel = level)
      )

      const subscription = client
        .subscription(SUBSCRIBE_TO_LOGS, { filterLevel })
        .subscribe(result => {
          if (result.data?.logs) {
            const newLog: LogEntryInterface = result.data.logs
            writableLogsStore.update(state => ({
              ...state,
              logs: [newLog, ...state.logs] // Add new log at the beginning
            }))
          }
        })

      unsubscribe = () => {
        unsubscribeFilter()
        subscription.unsubscribe()
      }
    },

    unsubscribeFromLogs: () => {
      if (unsubscribe) {
        unsubscribe()
        unsubscribe = null
      }
    }
  }

  // Getters: read-only derived stores
  const loading = derived(writableLogsStore, $state => $state.loading)
  const logs = derived(writableLogsStore, $state => $state.logs)
  const filterLevel = derived(writableLogsStore, $state => $state.filterLevel)

  // Filtered logs based on selected level
  const filteredLogs = derived(writableLogsStore, $state => {
    if (!$state.filterLevel) {
      return $state.logs
    }
    return $state.logs.filter(log => log.level === $state.filterLevel)
  })

  const getters: LogsStoreGettersInterface = {
    loading,
    logs,
    filterLevel,
    filteredLogs
  }

  return { actions, getters }
}
