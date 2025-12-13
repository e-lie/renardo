<script lang="ts">
  import { setContextClient, createClient, fetchExchange } from '@urql/svelte';
  import { currentPage } from './store/root/Root.store';
  import Navbar from './components/shared/Navbar.component.svelte';
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
  {:else}
    <div class="text-center py-8">
      <h1 class="text-2xl font-bold mb-4">Page not found</h1>
      <button class="btn btn-primary" onclick={() => currentPage.set('editor')}>
        Go to Editor
      </button>
    </div>
  {/if}
</div>
