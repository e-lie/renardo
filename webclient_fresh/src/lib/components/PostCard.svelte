<script lang="ts">
  import { currentPage, selectedPost } from '../stores'
  import type { Post } from '../types'

  export let post: Post

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  function readMore() {
    selectedPost.set(post)
    currentPage.set('post-detail')
  }
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">{post.title}</h2>
    <p class="text-base-content/70 line-clamp-3">{post.content}</p>
    <div class="card-actions justify-between items-center mt-4">
      <div class="text-sm text-base-content/60">
        <div class="font-medium">{post.author.name}</div>
        <div>{formatDate(post.createdAt)}</div>
      </div>
      <button class="btn btn-primary btn-sm" on:click={readMore}>Read More</button>
    </div>
  </div>
</div>

<style>
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>