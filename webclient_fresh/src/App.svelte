<script lang="ts">
  import { setContextClient, createClient, fetchExchange } from '@urql/svelte';
  import { currentPage } from './store/root/Root.store';
  import Navbar from './components/shared/Navbar.component.svelte';
  import PostsView from './views/Posts.view.svelte';
  import AuthorsView from './views/Authors.view.svelte';
  import PostDetailView from './views/PostDetail.view.svelte';
  import LogsView from './views/Logs.view.svelte';
  import EditorView from './views/Editor.view.svelte';

  const client = createClient({
    url: 'http://localhost:8000/graphql',
    exchanges: [fetchExchange],
  });

  setContextClient(client);
</script>

<div class="min-h-screen bg-base-100">
  <Navbar />

  {#if $currentPage === 'editor'}
    <EditorView />
  {:else if $currentPage === 'posts'}
    <PostsView />
  {:else if $currentPage === 'authors'}
    <AuthorsView />
  {:else if $currentPage === 'post-detail'}
    <PostDetailView />
  {:else if $currentPage === 'logs'}
    <LogsView />
  {:else}
    <div class="text-center py-8">
      <h1 class="text-2xl font-bold mb-4">Page not found</h1>
      <button class="btn btn-primary" onclick={() => currentPage.set('posts')}>
        Go to Posts
      </button>
    </div>
  {/if}
</div>
