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
