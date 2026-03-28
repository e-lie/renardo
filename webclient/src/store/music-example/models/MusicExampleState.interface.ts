import type { MusicExampleFileInterface } from '@/models/music-example'

export interface MusicExampleStateInterface {
  loading: boolean
  musicExampleFiles: MusicExampleFileInterface[]
  error: string | null
}
