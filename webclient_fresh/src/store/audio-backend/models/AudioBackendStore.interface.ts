import type { Readable } from 'svelte/store'
import type { AudioBackendStateInterface } from './AudioBackendState.interface'
import type { AudioDevicesInterface, AudioBackendStatusInterface } from '../../../models/audio-backend'
import type { ConsoleMessageInterface } from '../../../models/websocket'

export interface AudioBackendStoreActionsInterface {
  startBackend: (audioOutputIndex?: number) => Promise<void>
  stopBackend: () => Promise<void>
  loadStatus: () => Promise<void>
  loadAudioDevices: () => Promise<void>
  setAudioDevice: (index: number) => Promise<void>
  launchIDE: () => Promise<void>
  clearError: () => void
}

export interface AudioBackendStoreGettersInterface {
  status: Readable<AudioBackendStatusInterface>
  devices: Readable<AudioDevicesInterface | null>
  selectedDeviceIndex: Readable<number>
  isLoading: Readable<boolean>
  error: Readable<string | null>
  platform: Readable<string | null>
  showDeviceSelector: Readable<boolean>
  scLogs: Readable<ConsoleMessageInterface[]>
}

export interface AudioBackendStoreInterface {
  actions: AudioBackendStoreActionsInterface
  getters: AudioBackendStoreGettersInterface
}
