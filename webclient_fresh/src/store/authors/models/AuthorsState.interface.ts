import type { AuthorInterface } from '../../../models/authors/Author.interface'

export interface AuthorsStateInterface {
  loading: boolean
  authors: AuthorInterface[]
}
