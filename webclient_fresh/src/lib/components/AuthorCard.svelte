<script lang="ts">
  import type { Author } from '../types'

  export let author: Author
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">
      <div class="avatar placeholder">
        <div class="bg-neutral text-neutral-content rounded-full w-12">
          <span class="text-xl">{author.name.charAt(0)}</span>
        </div>
      </div>
      {author.name}
    </h2>
    <p class="text-base-content/70">{author.email}</p>

    {#if author.posts && author.posts.length > 0}
      <div class="mt-4">
        <h3 class="font-semibold mb-2">Recent Posts ({author.posts.length})</h3>
        <div class="space-y-2">
          {#each author.posts.slice(0, 3) as post}
            <div class="text-sm">
              <div class="font-medium">{post.title}</div>
              <div class="text-base-content/60 text-xs">
                {new Date(post.createdAt).toLocaleDateString()}
              </div>
            </div>
          {/each}
          {#if author.posts.length > 3}
            <div class="text-xs text-base-content/60">
              +{author.posts.length - 3} more posts
            </div>
          {/if}
        </div>
      </div>
    {:else}
      <div class="text-sm text-base-content/60 mt-4">
        No posts yet
      </div>
    {/if}

    <div class="card-actions justify-end mt-4">
      <div class="btn btn-primary btn-sm">View Profile</div>
    </div>
  </div>
</div>