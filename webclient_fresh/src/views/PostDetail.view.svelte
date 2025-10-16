<script lang="ts">
  import { ElButton, ElCard } from '../components/primitives'
  import { useAppStore, currentPage } from '../store'

  const { postsStore } = useAppStore()
  const { selectedPost } = postsStore.getters

  function goBack() {
    postsStore.actions.selectPost(null)
    currentPage.set('posts')
  }
</script>

<div class="container mx-auto px-4 py-8">
  {#if $selectedPost}
    <ElButton variant="ghost" onclick={goBack} addCss="mb-4">
      ← Back to Posts
    </ElButton>

    <ElCard>
      <div class="card-body">
        <h1 class="card-title text-3xl">{$selectedPost.title}</h1>
        <p class="text-sm text-base-content/60">
          By {$selectedPost.author.name} ({$selectedPost.author.email}) •
          {new Date($selectedPost.createdAt).toLocaleDateString()}
        </p>
        <div class="divider"></div>
        <p class="whitespace-pre-wrap">{$selectedPost.content}</p>
      </div>
    </ElCard>
  {:else}
    <p>No post selected</p>
  {/if}
</div>
