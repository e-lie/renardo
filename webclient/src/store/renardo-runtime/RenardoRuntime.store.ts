import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import { useWebSocketBackendStore } from '../websocket/WebSocketBackend.store'
import type {
  RenardoRuntimeStateInterface,
  RenardoRuntimeStoreInterface
} from './models'

const initialState: RenardoRuntimeStateInterface = {
  status: { running: false, status: 'stopped', pid: null },
  isLoading: false,
  error: null
}

const writableStore = writable<RenardoRuntimeStateInterface>(initialState)

function applyResult(result: any) {
  writableStore.update(s => ({
    ...s,
    status: {
      running: result.running,
      status: result.status,
      pid: result.pid ?? null
    },
    isLoading: false
  }))
}

export function useRenardoRuntimeStore(): RenardoRuntimeStoreInterface {
  const { getters: wsGetters } = useWebSocketBackendStore()

  const actions = {
    loadStatus: async () => {
      try {
        const result = await apiClient.get('/api/runtime/status')
        writableStore.update(s => ({
          ...s,
          status: { running: result.running, status: result.status, pid: result.pid ?? null }
        }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    startRuntime: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/runtime/start', {})
        applyResult(result)
        if (!result.success) {
          writableStore.update(s => ({ ...s, error: result.message }))
        }
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    stopRuntime: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/runtime/stop', {})
        applyResult(result)
        if (!result.success) {
          writableStore.update(s => ({ ...s, error: result.message }))
        }
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    restartRuntime: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/runtime/restart', {})
        applyResult(result)
        if (!result.success) {
          writableStore.update(s => ({ ...s, error: result.message }))
        }
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    clearError: () => {
      writableStore.update(s => ({ ...s, error: null }))
    }
  }

  const status = derived(writableStore, $s => $s.status)
  const isLoading = derived(writableStore, $s => $s.isLoading)
  const error = derived(writableStore, $s => $s.error)

  const runtimeLogs = derived(wsGetters.consoleMessages, $messages =>
    $messages.filter(m => m.source === 'runtime')
  )

  return { actions, getters: { status, isLoading, error, runtimeLogs } }
}
