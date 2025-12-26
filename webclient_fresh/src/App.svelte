<script lang="ts">
  import LayoutView from './views/Layout.view.svelte';
  import { onMount, onDestroy } from 'svelte';
  import { useAppStore } from './store/root/Root.store';
  import { useConsoleStore } from './store/console/Console.store';

  // Initialize stores
  const appStore = useAppStore();
  const consoleStore = useConsoleStore();

  let websocketSyncUnsubscribe: (() => void) | undefined;

  onMount(() => {
    // Connect WebSocket
    appStore.webSocketBackendStore.actions.connect();
    
    // Sync console with WebSocket messages
    if (consoleStore.syncWithWebSocket) {
      websocketSyncUnsubscribe = consoleStore.syncWithWebSocket(appStore.webSocketBackendStore);
    }
  });

  onDestroy(() => {
    // Cleanup WebSocket sync
    if (websocketSyncUnsubscribe) {
      websocketSyncUnsubscribe();
    }
    
    // Disconnect WebSocket
    appStore.webSocketBackendStore.actions.disconnect();
  });
</script>

<LayoutView />
