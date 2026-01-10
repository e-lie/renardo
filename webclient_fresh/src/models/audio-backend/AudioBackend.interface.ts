export interface AudioDeviceInterface {
  index: number
  name: string
}

export interface AudioDevicesInterface {
  output: AudioDeviceInterface[]
  input: AudioDeviceInterface[]
}

export interface AudioBackendStatusInterface {
  running: boolean
  message: string
}

export interface ChannelsInterface {
  numOutputChannels: number
  numInputChannels: number
}

export interface ReconfigureResultInterface {
  success: boolean
  message: string
  regenerated: boolean
  restarted: boolean
}
