<script lang="ts">
  import { setContextClient, createClient, fetchExchange } from '@urql/svelte';
  import EditorView from './views/Editor.view.svelte';

  const client = createClient({
    url: 'http://localhost:8000/graphql',
    exchanges: [fetchExchange],
  });

  setContextClient(client);
</script>

<div class="h-screen overflow-hidden bg-base-100">
  <EditorView />
</div>
