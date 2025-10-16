<script lang="ts">
  import type { PostInterface } from '../../models/posts/Post.interface'
  import PostCard from './children/PostCard.component.svelte'

  let {
    loading = false,
    posts = [],
    onselect
  }: {
    loading?: boolean
    posts?: PostInterface[]
    onselect?: (post: PostInterface) => void
  } = $props()
</script>

<div class="space-y-6">
  {#if loading}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if posts.length === 0}
    <div class="text-center py-8">
      <p class="text-base-content/60">No posts found</p>
    </div>
  {:else}
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each posts as post (post.id)}
        <PostCard
          testid={`post-card-${post.id}`}
          {post}
          {onselect}
        />
      {/each}
    </div>
  {/if}
</div>
