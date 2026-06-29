import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import type { AbletonStateInterface, AbletonStoreInterface } from './models'

const initialState: AbletonStateInterface = {
  status: { status: 'stopped', message: '' },
  startupEnabled: false,
  isLoading: false,
  error: null,
}

const writableStore = writable<AbletonStateInterface>(initialState)

export function useAbletonStore(): AbletonStoreInterface {
  const actions = {
    loadStatus: async () => {
      try {
        const result = await apiClient.get('/api/ableton/status')
        writableStore.update(s => ({ ...s, status: { status: result.status, message: result.message } }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message }))
      }
    },

    start: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/ableton/start', {})
        writableStore.update(s => ({
          ...s,
          status: { status: result.status, message: result.message },
          isLoading: false,
        }))
        if (!result.success) writableStore.update(s => ({ ...s, error: result.message }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message, isLoading: false }))
      }
    },

    stop: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/ableton/stop', {})
        writableStore.update(s => ({
          ...s,
          status: { status: result.status, message: result.message },
          isLoading: false,
        }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message, isLoading: false }))
      }
    },

    restart: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/ableton/restart', {})
        writableStore.update(s => ({
          ...s,
          status: { status: result.status, message: result.message },
          isLoading: false,
        }))
        if (!result.success) writableStore.update(s => ({ ...s, error: result.message }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message, isLoading: false }))
      }
    },

    loadStartupEnabled: async () => {
      try {
        const result = await apiClient.get('/api/ableton/settings/startup-enabled')
        writableStore.update(s => ({ ...s, startupEnabled: result.enabled }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message }))
      }
    },

    setStartupEnabled: async (enabled: boolean) => {
      try {
        await apiClient.post('/api/ableton/settings/startup-enabled', { enabled })
        writableStore.update(s => ({ ...s, startupEnabled: enabled }))
      } catch (err: any) {
        writableStore.update(s => ({ ...s, error: err.message }))
      }
    },

    clearError: () => writableStore.update(s => ({ ...s, error: null })),
  }

  const status = derived(writableStore, $s => $s.status)
  const startupEnabled = derived(writableStore, $s => $s.startupEnabled)
  const isLoading = derived(writableStore, $s => $s.isLoading)
  const error = derived(writableStore, $s => $s.error)

  return { actions, getters: { status, startupEnabled, isLoading, error } }
}
