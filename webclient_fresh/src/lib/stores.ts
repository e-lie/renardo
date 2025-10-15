import { writable } from 'svelte/store'

// Simple router store
export const currentPage = writable('posts')
export const selectedPost = writable(null)
export const currentSession = writable('renardo-session')