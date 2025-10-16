import type { Readable } from 'svelte/store'
import type { AuthorInterface } from '../../../models/authors/Author.interface'

export interface AuthorsStoreActionsInterface {
  loadAuthors: () => Promise<void>
}

export interface AuthorsStoreGettersInterface {
  loading: Readable<boolean>
  authors: Readable<AuthorInterface[]>
}

export interface AuthorsStoreInterface {
  getters: AuthorsStoreGettersInterface
  actions: AuthorsStoreActionsInterface
}
