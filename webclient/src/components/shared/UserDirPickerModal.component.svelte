<script lang="ts">
  import { useI18nStore } from '../../store/i18n/I18n.store'
  import { apiClient } from '../../api-client/rest/api'

  let {
    isOpen = false,
    onclose,
    onconfigured
  }: {
    isOpen?: boolean
    onclose?: () => void
    onconfigured?: () => void
  } = $props()

  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  interface DirEntry {
    name: string
    path: string
    is_directory: boolean
    has_children: boolean
  }

  let currentPath = $state('')
  let entries = $state<DirEntry[]>([])
  let selectedPath = $state('')
  let loading = $state(false)
  let saving = $state(false)
  let error = $state<string | null>(null)

  $effect(() => {
    if (isOpen && !currentPath) {
      initBrowser()
    }
  })

  async function initBrowser() {
    loading = true
    error = null
    try {
      const homeResp = await apiClient.get('/api/file-explorer/home')
      currentPath = homeResp.path
      selectedPath = homeResp.path
      await loadEntries(homeResp.path)
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load directory'
    } finally {
      loading = false
    }
  }

  async function loadEntries(path: string) {
    loading = true
    error = null
    try {
      const resp = await apiClient.get(`/api/file-explorer/list?path=${encodeURIComponent(path)}`)
      entries = (resp as DirEntry[]).filter((e: DirEntry) => e.is_directory)
      currentPath = path
      selectedPath = path
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to list directory'
    } finally {
      loading = false
    }
  }

  async function navigateUp() {
    try {
      const resp = await apiClient.get(`/api/file-explorer/parent?path=${encodeURIComponent(currentPath)}`)
      await loadEntries(resp.path)
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to navigate'
    }
  }

  async function navigateInto(entry: DirEntry) {
    await loadEntries(entry.path)
  }

  async function handleConfirm() {
    saving = true
    error = null
    try {
      await apiClient.post('/api/user-directory/set', { path: selectedPath })
      onconfigured?.()
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to set directory'
    } finally {
      saving = false
    }
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onclose?.()
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card bg-surface-100 dark:bg-surface-800 w-full max-w-2xl p-6 space-y-4">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">{$translate('initUserDirTitle')}</h2>
        {#if onclose}
          <button
            class="btn variant-ghost w-8 h-8 p-0 rounded-full"
            onclick={() => onclose?.()}
            aria-label="Close"
          >
            ✕
          </button>
        {/if}
      </div>

      <p class="opacity-70 text-sm">{$translate('initUserDirDescription')}</p>

      <!-- Current path breadcrumb -->
      <div class="flex items-center gap-2 text-sm font-mono bg-surface-200 dark:bg-surface-900 rounded px-3 py-2 truncate">
        <button
          class="btn btn-sm variant-ghost p-1"
          onclick={navigateUp}
          disabled={loading}
          aria-label="Go up"
        >
          ↑
        </button>
        <span class="truncate opacity-70">{currentPath}</span>
      </div>

      <!-- Error -->
      {#if error}
        <div class="alert variant-filled-error text-sm">{error}</div>
      {/if}

      <!-- Directory listing -->
      <div class="bg-surface-200 dark:bg-surface-900 rounded-lg h-64 overflow-y-auto">
        {#if loading}
          <div class="flex items-center justify-center h-full opacity-50">
            <span class="animate-spin mr-2">⏳</span>
            {$translate('loading')}
          </div>
        {:else if entries.length === 0}
          <div class="flex items-center justify-center h-full opacity-50 italic text-sm">
            {$translate('emptyDirectory')}
          </div>
        {:else}
          <ul class="divide-y divide-surface-300 dark:divide-surface-700">
            {#each entries as entry}
              <li>
                <button
                  class="w-full text-left px-4 py-2 hover:bg-surface-300 dark:hover:bg-surface-700 flex items-center gap-2 text-sm"
                  onclick={() => navigateInto(entry)}
                >
                  <span>📁</span>
                  <span class="truncate">{entry.name}</span>
                  {#if entry.has_children}
                    <span class="ml-auto opacity-40 text-xs">▶</span>
                  {/if}
                </button>
              </li>
            {/each}
          </ul>
        {/if}
      </div>

      <!-- Selected path display -->
      <div class="text-sm space-y-1">
        <span class="opacity-60">{$translate('initUserDirCurrentSelection')}</span>
        <div class="font-mono text-xs bg-surface-200 dark:bg-surface-900 rounded px-3 py-2 truncate">
          {selectedPath || '—'}
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-2">
        {#if onclose}
          <button
            class="btn variant-ghost"
            onclick={() => onclose?.()}
            disabled={saving}
          >
            {$translate('cancel')}
          </button>
        {/if}
        <button
          class="btn variant-filled-primary"
          onclick={handleConfirm}
          disabled={!selectedPath || saving || loading}
        >
          {#if saving}
            <span class="animate-spin mr-1">⏳</span>
          {/if}
          {$translate('initUserDirSelectButton')}
        </button>
      </div>
    </div>
  </div>
{/if}
