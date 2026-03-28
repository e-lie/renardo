import type { Readable } from 'svelte/store'
import type { MusicExampleFileInterface } from '@/models/music-example'

export interface MusicExampleStoreActionsInterface {
  loadMusicExampleFiles: () => Promise<void>
  selectMusicExampleFile: (file: MusicExampleFileInterface, editorStore: any) => Promise<void>
  setError: (error: string | null) => void
}

export interface MusicExampleStoreGettersInterface {
  loading: Readable<boolean>
  musicExampleFiles: Readable<MusicExampleFileInterface[]>
  error: Readable<string | null>
}

export interface MusicExampleStoreInterface {
  actions: MusicExampleStoreActionsInterface
  getters: MusicExampleStoreGettersInterface
}
