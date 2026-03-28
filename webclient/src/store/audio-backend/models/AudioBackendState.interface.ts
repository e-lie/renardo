import type { AudioDevicesInterface, AudioBackendStatusInterface, ChannelsInterface } from '../../../models/audio-backend'

export interface AudioBackendStateInterface {
  status: AudioBackendStatusInterface
  devices: AudioDevicesInterface | null
  selectedDeviceIndex: number
  channels: ChannelsInterface | null
  isLoading: boolean
  error: string | null
  platform: string | null
}
