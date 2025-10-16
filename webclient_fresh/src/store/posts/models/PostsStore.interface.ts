import type { Readable } from 'svelte/store'
import type { PostInterface } from '../../../models/posts/Post.interface'

export interface PostsStoreActionsInterface {
  loadPosts: () => Promise<void>
  selectPost: (post: PostInterface | null) => void
}

export interface PostsStoreGettersInterface {
  loading: Readable<boolean>
  posts: Readable<PostInterface[]>
  selectedPost: Readable<PostInterface | null>
}

export interface PostsStoreInterface {
  getters: PostsStoreGettersInterface
  actions: PostsStoreActionsInterface
}
