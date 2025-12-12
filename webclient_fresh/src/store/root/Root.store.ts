import { writable } from 'svelte/store'
import type { RootStoreInterface } from './models'
import { usePostsStore } from '../posts'
import { useAuthorsStore } from '../authors'

// Router store for navigation
export const currentPage = writable<'posts' | 'authors' | 'post-detail' | 'logs'>('posts')

// Hook that returns our root store instance
export function useAppStore(): RootStoreInterface {
  return {
    postsStore: usePostsStore(),
    authorsStore: useAuthorsStore()
  }
}
