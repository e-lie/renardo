import type { PostInterface } from '../../../models/posts/Post.interface'

export interface PostsStateInterface {
  loading: boolean
  posts: PostInterface[]
  selectedPost: PostInterface | null
}
