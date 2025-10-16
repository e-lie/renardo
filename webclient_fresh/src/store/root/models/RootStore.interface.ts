import type { PostsStoreInterface } from '../../posts'
import type { AuthorsStoreInterface } from '../../authors'

export interface RootStoreInterface {
  postsStore: PostsStoreInterface
  authorsStore: AuthorsStoreInterface
}
