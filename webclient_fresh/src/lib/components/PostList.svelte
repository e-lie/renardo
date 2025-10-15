<script lang="ts">
  import { queryStore, getContextClient } from '@urql/svelte'
  import { GET_POSTS } from '../queries'
  import PostCard from './PostCard.svelte'
  import type { Post } from '../types'

  const client = getContextClient()
  const posts = queryStore({
    client,
    query: GET_POSTS,
  })
</script>

<div class="space-y-6">
  {#if $posts.fetching}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if $posts.error}
    <div class="alert alert-error">
      <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Error: {$posts.error.message}</span>
    </div>
  {:else if $posts.data?.posts}
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each $posts.data.posts as post (post.id)}
        <PostCard {post} />
      {/each}
    </div>
  {:else}
    <div class="text-center py-8">
      <p class="text-base-content/60">No posts found</p>
    </div>
  {/if}
</div>