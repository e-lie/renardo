<script lang="ts">
  import type { AuthorInterface } from '../../models/authors/Author.interface'
  import AuthorCard from './children/AuthorCard.component.svelte'

  let {
    loading = false,
    authors = []
  }: {
    loading?: boolean
    authors?: AuthorInterface[]
  } = $props()
</script>

<div class="space-y-6">
  {#if loading}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if authors.length === 0}
    <div class="text-center py-8">
      <p class="text-base-content/60">No authors found</p>
    </div>
  {:else}
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each authors as author (author.id)}
        <AuthorCard
          testid={`author-card-${author.id}`}
          {author}
        />
      {/each}
    </div>
  {/if}
</div>
