<script lang="ts">
  import { onMount } from 'svelte';
  import { useAppStore } from '../../../store/root';
  import { useI18nStore } from '../../../store/i18n/I18n.store';
  import { dispatchLoadFile } from '../../../events/editorEvents';
  import type { DirectoryEntry } from '../../../models/file-explorer';
  import FileExplorerModal from '../../shared/FileExplorerModal.component.svelte';

  let {
    componentId,
    title = 'User Directory',
  }: {
    componentId: string;
    title?: string;
  } = $props();

  const { userDirectoryStore } = useAppStore();
  const { loading, userDirectoryPath, currentPath, entries, error } = userDirectoryStore.getters;
  const { loadUserDirectory, listUserDirectory, setUserDirectory, navigateToEntry } = userDirectoryStore.actions;

  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;

  let showFileExplorer = $state(false);
  let pathHistory = $state<string[]>([]);

  onMount(async () => {
    await loadUserDirectory();
  });

  // Update path history when current path changes
  $effect(() => {
    const path = $currentPath;
    if (path && !pathHistory.includes(path)) {
      pathHistory = [...pathHistory, path];
    }
  });

  function handleDirectorySelect(path: string) {
    setUserDirectory(path);
    showFileExplorer = false;
  }

  async function handleEntryClick(entry: DirectoryEntry) {
    if (entry.is_directory) {
      const userDir = $userDirectoryPath;
      const relativePath = userDir ? entry.path.replace(userDir, '').replace(/^\//, '') : entry.path;
      await listUserDirectory(relativePath);
    } else {
      // Load file in editor
      await loadFileInEditor(entry.path, entry.name);
    }
  }

  async function loadFileInEditor(filePath: string, fileName: string) {
    try {
      const response = await fetch(`http://localhost:8000/api/file-explorer/read?path=${encodeURIComponent(filePath)}`);

      if (response.ok) {
        const data = await response.json();
        const content = data.content || '';

        const tabTitle = fileName.replace(/\.[^/.]+$/, '');
        dispatchLoadFile(content, tabTitle, filePath);
      } else {
        const errorData = await response.json();
        console.error('Failed to load file:', errorData.detail);
      }
    } catch (e) {
      console.error('Failed to load file:', e);
    }
  }

  async function handleGoUp() {
    const userDir = $userDirectoryPath;
    const current = $currentPath;

    if (userDir && current && current !== userDir) {
      // Navigate to parent directory
      const currentRelative = current.replace(userDir, '').replace(/^\//, '');
      const parts = currentRelative.split('/').filter(Boolean);

      if (parts.length > 0) {
        parts.pop();
        const newRelative = parts.join('/');
        await listUserDirectory(newRelative || '');
      }
    }
  }

  function canGoUp(): boolean {
    const userDir = $userDirectoryPath;
    const current = $currentPath;
    return !!(userDir && current && current !== userDir);
  }
</script>

<div class="h-full flex flex-col">
  <!-- Header -->
  <div class="p-4 border-b border-surface-300 dark:border-surface-700 flex items-center justify-between">
    <button
      class="btn btn-sm variant-ghost"
      onclick={() => showFileExplorer = true}
      title="Change User Directory"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
      </svg>
      {#if $userDirectoryPath}
        <span class="text-xs">{$userDirectoryPath.split('/').pop()}</span>
      {:else}
        <span class="text-xs">Select User Directory</span>
      {/if}
    </button>
  </div>

  {#if !$userDirectoryPath}
    <div class="flex-1 flex items-center justify-center p-4">
      <p class="text-surface-500 text-center">{$translate('loading')}</p>
    </div>
  {:else}
    <!-- Path breadcrumb -->
    <div class="px-4 py-2 bg-surface-100 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
      <div class="flex items-center gap-2">
        <button
          class="btn btn-sm variant-ghost"
          onclick={handleGoUp}
          disabled={!canGoUp()}
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </button>
        <span class="text-xs text-surface-700 dark:text-surface-300 font-mono truncate">{$currentPath || $userDirectoryPath}</span>
      </div>
    </div>

    <!-- File list -->
    <div class="flex-1 overflow-y-auto p-2">
      {#if $loading}
        <div class="flex items-center justify-center h-full">
          <p class="text-surface-500">{$translate('loading')}</p>
        </div>
      {:else if $error}
        <div class="flex items-center justify-center h-full">
          <p class="text-error-500">{$error}</p>
        </div>
      {:else if $entries.length === 0}
        <div class="flex items-center justify-center h-full">
          <p class="text-surface-500">{$translate('emptyDirectory')}</p>
        </div>
      {:else}
        <div class="space-y-1">
          {#each $entries as entry}
            <button
              class="w-full text-left px-2 py-1.5 rounded-lg transition-colors hover:bg-surface-200 dark:hover:bg-surface-800"
              onclick={() => handleEntryClick(entry)}
            >
              <div class="flex items-center gap-2">
                {#if entry.is_directory}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 text-warning-500 flex-shrink-0">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                  </svg>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 text-surface-500 flex-shrink-0">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                {/if}
                <span class="text-sm text-surface-900 dark:text-surface-50 truncate">{entry.name}</span>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<FileExplorerModal
  isOpen={showFileExplorer}
  mode="select-folder"
  initialPath={$userDirectoryPath || null}
  onclose={() => showFileExplorer = false}
  onselect={handleDirectorySelect}
/>
