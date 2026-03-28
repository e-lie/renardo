import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import type {
  InitializationStateInterface,
  InitializationStoreInterface,
  InitializationStoreActionsInterface,
  InitializationStoreGettersInterface,
  InitLogEntry
} from './models'

const initialState: InitializationStateInterface = {
  loading: false,
  userDirConfigured: true,
  userDir: null,
  samplesInitialized: true,
  sccodeInitialized: true,
  downloading: false,
  downloadComplete: false,
  downloadError: null,
  initLogs: []
}

const writableInitStore = writable<InitializationStateInterface>(initialState)

export function useInitializationStore(): InitializationStoreInterface {
  let wsUnsubscribe: (() => void) | undefined

  const actions: InitializationStoreActionsInterface = {
    checkStatus: async () => {
      writableInitStore.update(s => ({ ...s, loading: true }))
      try {
        const response = await apiClient.get('/api/init/status')
        writableInitStore.update(s => ({
          ...s,
          loading: false,
          userDirConfigured: response.user_dir_configured,
          userDir: response.user_dir,
          samplesInitialized: response.samples_initialized,
          sccodeInitialized: response.sccode_initialized
        }))
      } catch (error) {
        writableInitStore.update(s => ({ ...s, loading: false }))
      }
    },

    downloadMissing: async (downloadSamples: boolean, downloadSccode: boolean) => {
      writableInitStore.update(s => ({
        ...s,
        downloading: true,
        downloadComplete: false,
        downloadError: null,
        initLogs: []
      }))
      try {
        await apiClient.post('/api/init/download-missing', {
          download_samples: downloadSamples,
          download_sccode: downloadSccode
        })
      } catch (error) {
        writableInitStore.update(s => ({
          ...s,
          downloading: false,
          downloadError: error instanceof Error ? error.message : 'Download request failed'
        }))
      }
    },

    clearLogs: () => {
      writableInitStore.update(s => ({ ...s, initLogs: [] }))
    },

    subscribeToWebSocket: (wsStore: any) => {
      if (wsUnsubscribe) wsUnsubscribe()
      wsUnsubscribe = wsStore.getters.consoleMessages.subscribe((messages: any[]) => {
        const initMessages = messages.filter((m: any) => m.source === 'init')
        if (initMessages.length === 0) return

        writableInitStore.update(s => {
          const existingIds = new Set(s.initLogs.map((l: InitLogEntry) => l.id))
          const newLogs = [...s.initLogs]
          let downloading = s.downloading
          let downloadComplete = s.downloadComplete
          let downloadError = s.downloadError

          for (const msg of initMessages) {
            if (existingIds.has(msg.id)) continue
            newLogs.push({ id: msg.id, level: msg.level, message: msg.message })

            if (msg.metadata?.event === 'init_complete') {
              downloading = false
              downloadComplete = true
            } else if (msg.metadata?.event === 'init_error') {
              downloading = false
              downloadError = msg.message
            }
          }

          return { ...s, initLogs: newLogs, downloading, downloadComplete, downloadError }
        })
      })
    }
  }

  const loading = derived(writableInitStore, $s => $s.loading)
  const userDirConfigured = derived(writableInitStore, $s => $s.userDirConfigured)
  const userDir = derived(writableInitStore, $s => $s.userDir)
  const samplesInitialized = derived(writableInitStore, $s => $s.samplesInitialized)
  const sccodeInitialized = derived(writableInitStore, $s => $s.sccodeInitialized)
  const downloading = derived(writableInitStore, $s => $s.downloading)
  const downloadComplete = derived(writableInitStore, $s => $s.downloadComplete)
  const downloadError = derived(writableInitStore, $s => $s.downloadError)
  const initLogs = derived(writableInitStore, $s => $s.initLogs)
  const hasAllResources = derived(writableInitStore, $s => $s.samplesInitialized && $s.sccodeInitialized)

  const getters: InitializationStoreGettersInterface = {
    loading,
    userDirConfigured,
    userDir,
    samplesInitialized,
    sccodeInitialized,
    downloading,
    downloadComplete,
    downloadError,
    initLogs,
    hasAllResources
  }

  return { actions, getters }
}
