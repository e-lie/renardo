export interface MusicExampleFileInterface {
  name: string
  path: string
  url: string
}

export interface MusicExampleResponseInterface {
  success: boolean
  files: MusicExampleFileInterface[]
}
