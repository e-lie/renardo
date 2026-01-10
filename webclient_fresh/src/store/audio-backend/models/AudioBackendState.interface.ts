import type { AudioDevicesInterface, AudioBackendStatusInterface } from '../../../models/audio-backend'

export interface AudioBackendStateInterface {
  status: AudioBackendStatusInterface
  devices: AudioDevicesInterface | null
  selectedDeviceIndex: number
  isLoading: boolean
  error: string | null
  platform: string | null
}
