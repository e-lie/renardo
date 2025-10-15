<script lang="ts">
  import { queryStore, getContextClient } from '@urql/svelte'
  import { GET_AUTHORS } from '../queries'
  import AuthorCard from './AuthorCard.svelte'
  import type { Author } from '../types'

  const client = getContextClient()
  const authors = queryStore({
    client,
    query: GET_AUTHORS,
  })
</script>

<div class="space-y-6">
  {#if $authors.fetching}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if $authors.error}
    <div class="alert alert-error">
      <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Error: {$authors.error.message}</span>
    </div>
  {:else if $authors.data?.authors}
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each $authors.data.authors as author (author.id)}
        <AuthorCard {author} />
      {/each}
    </div>
  {:else}
    <div class="text-center py-8">
      <p class="text-base-content/60">No authors found</p>
    </div>
  {/if}
</div>