import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import { useWebSocketBackendStore } from '../websocket/WebSocketBackend.store'
import type {
  AudioBackendStateInterface,
  AudioBackendStoreInterface
} from './models'

const initialState: AudioBackendStateInterface = {
  status: { running: false, message: '' },
  devices: null,
  selectedDeviceIndex: -1,
  channels: null,
  isLoading: false,
  error: null,
  platform: null
}

const writableStore = writable<AudioBackendStateInterface>(initialState)

export function useAudioBackendStore(): AudioBackendStoreInterface {
  const { getters: wsGetters } = useWebSocketBackendStore()

  const actions = {
    startBackend: async (audioOutputIndex = -1) => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/sc-backend/start', {
          audio_output_index: audioOutputIndex
        })
        writableStore.update(s => ({
          ...s,
          status: { running: result.running, message: result.message },
          isLoading: false
        }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    stopBackend: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/sc-backend/stop', {})
        writableStore.update(s => ({
          ...s,
          status: { running: result.running, message: result.message },
          isLoading: false
        }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    loadStatus: async () => {
      try {
        const result = await apiClient.get('/api/sc-backend/status')
        writableStore.update(s => ({ ...s, status: result }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    loadAudioDevices: async () => {
      try {
        const result = await apiClient.get('/api/sc-backend/audio-devices')
        if (result.success && result.devices) {
          // Transform devices from dict to array
          const devices = {
            output: Object.entries(result.devices.output || {}).map(([index, name]) => ({
              index: parseInt(index),
              name: name as string
            })),
            input: Object.entries(result.devices.input || {}).map(([index, name]) => ({
              index: parseInt(index),
              name: name as string
            }))
          }
          writableStore.update(s => ({ ...s, devices, platform: result.platform }))
        } else {
          writableStore.update(s => ({ ...s, platform: result.platform }))
        }

        // Load current setting
        const setting = await apiClient.get('/api/sc-backend/settings/audio-device')
        writableStore.update(s => ({ ...s, selectedDeviceIndex: setting.audio_output_index }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    setAudioDevice: async (index: number) => {
      try {
        await apiClient.post('/api/sc-backend/settings/audio-device', {
          audio_output_index: index
        })
        writableStore.update(s => ({ ...s, selectedDeviceIndex: index }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    launchIDE: async () => {
      try {
        const result = await apiClient.post('/api/sc-backend/launch-ide', {})
        if (!result.success) {
          writableStore.update(s => ({ ...s, error: result.message }))
        }
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    clearError: () => {
      writableStore.update(s => ({ ...s, error: null }))
    },

    loadChannels: async () => {
      try {
        const result = await apiClient.get('/api/sc-backend/settings/channels')
        writableStore.update(s => ({
          ...s,
          channels: {
            numOutputChannels: result.num_output_channels,
            numInputChannels: result.num_input_channels
          }
        }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message }))
      }
    },

    setChannels: async (numOutput: number, numInput: number) => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/sc-backend/settings/channels', {
          num_output_channels: numOutput,
          num_input_channels: numInput
        })
        writableStore.update(s => ({
          ...s,
          channels: {
            numOutputChannels: result.num_output_channels,
            numInputChannels: result.num_input_channels
          },
          isLoading: false
        }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    },

    reconfigureBackend: async () => {
      writableStore.update(s => ({ ...s, isLoading: true, error: null }))
      try {
        const result = await apiClient.post('/api/sc-backend/reconfigure', {})

        if (result.success) {
          await actions.loadStatus()
        } else {
          writableStore.update(s => ({ ...s, error: result.message }))
        }

        writableStore.update(s => ({ ...s, isLoading: false }))
      } catch (error: any) {
        writableStore.update(s => ({ ...s, error: error.message, isLoading: false }))
      }
    }
  }

  // Derived stores
  const status = derived(writableStore, $s => $s.status)
  const devices = derived(writableStore, $s => $s.devices)
  const selectedDeviceIndex = derived(writableStore, $s => $s.selectedDeviceIndex)
  const isLoading = derived(writableStore, $s => $s.isLoading)
  const error = derived(writableStore, $s => $s.error)
  const platform = derived(writableStore, $s => $s.platform)
  const showDeviceSelector = derived(platform, $p => $p !== 'linux')

  // Filter WebSocket console messages for SC-related logs
  const scLogs = derived(wsGetters.consoleMessages, $messages =>
    $messages.filter(m =>
      m.source === 'backend' ||
      m.source === 'sc_backend' ||
      m.message.toLowerCase().includes('supercollider') ||
      m.message.toLowerCase().includes('sclang')
    )
  )

  const channels = derived(writableStore, $s => $s.channels)

  const getters = {
    status,
    devices,
    selectedDeviceIndex,
    isLoading,
    error,
    platform,
    showDeviceSelector,
    scLogs,
    channels
  }

  return { actions, getters }
}
