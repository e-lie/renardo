<script lang="ts">
  import type { PostInterface } from '../models/posts/Post.interface'
  import PostsList from '../components/posts/PostsList.component.svelte'
  import { useAppStore, currentPage } from '../store'

  const { postsStore } = useAppStore()
  const { loading, posts } = postsStore.getters

  function onSelectPost(post: PostInterface) {
    postsStore.actions.selectPost(post)
    currentPage.set('post-detail')
  }

  $effect(() => {
    postsStore.actions.loadPosts()
  })
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-4xl font-bold text-center mb-8">Renardo Blog</h1>
  <PostsList loading={$loading} posts={$posts} onselect={onSelectPost} />
</div>
