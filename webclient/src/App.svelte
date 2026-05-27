<script lang="ts">
  import LayoutView from './views/Layout.view.svelte';
  import UserDirPickerModal from './components/shared/UserDirPickerModal.component.svelte';
  import InitModal from './components/shared/InitModal.component.svelte';
  import { onMount, onDestroy } from 'svelte';
  import { useAppStore } from './store/root/Root.store';
  import { useConsoleStore } from './store/console/Console.store';
  import { useInitializationStore } from './store/initialization/Initialization.store';
  import { loadFromBackend, startAutoSave } from './services/frontend-state.service';

  const appStore = useAppStore();
  const consoleStore = useConsoleStore();
  const initStore = useInitializationStore();

  const { getters: initGetters } = initStore;
  const { userDirConfigured, samplesInitialized, sccodeInitialized } = initGetters;

  let showUserDirPicker = $state(false);
  let showInitModal = $state(false);

  let websocketSyncUnsubscribe: (() => void) | undefined;
  let stopAutoSave: (() => void) | undefined;

  onMount(async () => {
    appStore.webSocketBackendStore.actions.connect();

    if (consoleStore.syncWithWebSocket) {
      websocketSyncUnsubscribe = consoleStore.syncWithWebSocket(appStore.webSocketBackendStore);
    }

    initStore.actions.subscribeToWebSocket(appStore.webSocketBackendStore);

    // Charger l'état frontend depuis le backend (override localStorage si présent)
    await loadFromBackend();
    stopAutoSave = startAutoSave();

    await initStore.actions.checkStatus();

    if (!$userDirConfigured) {
      showUserDirPicker = true;
    } else if (!$samplesInitialized || !$sccodeInitialized) {
      showInitModal = true;
    }
  });

  onDestroy(() => {
    if (websocketSyncUnsubscribe) {
      websocketSyncUnsubscribe();
    }
    if (stopAutoSave) {
      stopAutoSave();
    }
    appStore.webSocketBackendStore.actions.disconnect();
  });

  async function onUserDirConfigured() {
    showUserDirPicker = false;
    await initStore.actions.checkStatus();
    if (!$samplesInitialized || !$sccodeInitialized) {
      showInitModal = true;
    }
  }
</script>

<LayoutView />

<UserDirPickerModal
  isOpen={showUserDirPicker}
  onconfigured={onUserDirConfigured}
/>

<InitModal
  isOpen={showInitModal}
  onclose={() => { showInitModal = false; }}
/>
