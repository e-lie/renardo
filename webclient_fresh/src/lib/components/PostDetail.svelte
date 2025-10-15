<script lang="ts">
  import { currentPage, selectedPost } from '../stores'
  import type { Post } from '../types'

  export let post: Post

  function goBack() {
    currentPage.set('posts')
    selectedPost.set(null)
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
</script>

<div class="max-w-4xl mx-auto">
  <!-- Back button -->
  <div class="mb-6">
    <button class="btn btn-ghost btn-sm" on:click={goBack}>
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Back to Posts
    </button>
  </div>

  <!-- Post content -->
  <article class="bg-base-100 shadow-xl rounded-lg overflow-hidden">
    <!-- Header -->
    <div class="bg-primary text-primary-content p-6">
      <h1 class="text-3xl font-bold mb-4">{post.title}</h1>

      <div class="flex items-center space-x-4">
        <div class="avatar placeholder">
          <div class="bg-base-100 text-base-content rounded-full w-12">
            <span class="text-lg font-semibold">{post.author.name.charAt(0)}</span>
          </div>
        </div>

        <div>
          <div class="font-semibold">{post.author.name}</div>
          <div class="text-primary-content/80 text-sm">{post.author.email}</div>
          <div class="text-primary-content/70 text-sm">{formatDate(post.createdAt)}</div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <div class="prose max-w-none">
        {#each post.content.split('\n') as paragraph}
          {#if paragraph.trim()}
            <p class="mb-4 leading-relaxed text-base-content">{paragraph}</p>
          {/if}
        {/each}
      </div>
    </div>

    <!-- Footer -->
    <div class="bg-base-200 p-6">
      <div class="flex justify-between items-center">
        <div class="text-sm text-base-content/60">
          Published on {formatDate(post.createdAt)}
        </div>

        <div class="flex space-x-2">
          <button class="btn btn-outline btn-sm">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Like
          </button>

          <button class="btn btn-outline btn-sm">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
            Share
          </button>
        </div>
      </div>
    </div>
  </article>
</div>