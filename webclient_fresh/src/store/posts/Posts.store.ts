import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import { GET_POSTS } from '../../api-client/graphql/queries'
import type {
  PostsStateInterface,
  PostsStoreInterface,
  PostsStoreActionsInterface,
  PostsStoreGettersInterface
} from './models'
import type { PostInterface } from '../../models/posts/Post.interface'

const writablePostsStore = writable<PostsStateInterface>({
  loading: false,
  posts: [],
  selectedPost: null
})

export function usePostsStore(): PostsStoreInterface {
  const client = getContextClient()

  const actions: PostsStoreActionsInterface = {
    loadPosts: async () => {
      writablePostsStore.update((state) => ({
        ...state,
        loading: true,
        posts: []
      }))

      const result = await client.query(GET_POSTS, {})

      if (result.data?.posts) {
        writablePostsStore.update((state) => ({
          ...state,
          posts: result.data.posts,
          loading: false
        }))
      }
    },

    selectPost: (post: PostInterface | null) => {
      writablePostsStore.update((state) => ({
        ...state,
        selectedPost: post
      }))
    }
  }

  const loading = derived(writablePostsStore, ($state) => $state.loading)
  const posts = derived(writablePostsStore, ($state) => $state.posts)
  const selectedPost = derived(writablePostsStore, ($state) => $state.selectedPost)

  const getters: PostsStoreGettersInterface = {
    loading,
    posts,
    selectedPost
  }

  return {
    getters,
    actions
  }
}
