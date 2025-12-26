<script lang="ts">
  import { useProjectStore } from '../../../store/project'
  import { useI18nStore } from '../../../store/i18n/I18n.store'
  import type { DirectoryEntry } from '../../../models/file-explorer'

  let {
    componentId,
    title = 'Project Explorer',
  }: {
    componentId: string
    title?: string
  } = $props()

  const { getters: projectGetters } = useProjectStore()
  const { currentProject } = projectGetters

  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  let currentPath = $state<string>('')
  let entries = $state<DirectoryEntry[]>([])
  let loading = $state<boolean>(false)
  let error = $state<string | null>(null)
  let pathHistory = $state<string[]>([])

  // Load directory entries
  async function loadDirectory(path: string) {
    loading = true
    error = null
    try {
      const response = await fetch(`http://localhost:8000/api/file-explorer/list?path=${encodeURIComponent(path)}`)
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to load directory')
      }
      entries = await response.json()
      currentPath = path
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load directory'
    } finally {
      loading = false
    }
  }

  // Watch for project changes
  $effect(() => {
    if ($currentProject?.root_path) {
      loadDirectory($currentProject.root_path)
      pathHistory = [$currentProject.root_path]
    } else {
      currentPath = ''
      entries = []
      pathHistory = []
    }
  })

  function handleEntryClick(entry: DirectoryEntry) {
    if (entry.is_directory) {
      pathHistory = [...pathHistory, entry.path]
      loadDirectory(entry.path)
    } else {
      // TODO: Open file in editor
      console.log('Open file:', entry.path)
    }
  }

  async function handleGoUp() {
    if (pathHistory.length > 1) {
      pathHistory = pathHistory.slice(0, -1)
      const parentPath = pathHistory[pathHistory.length - 1]
      loadDirectory(parentPath)
    }
  }
</script>

<div class="h-full flex flex-col">
  <!-- Header -->
  <div class="p-4 border-b border-surface-300 dark:border-surface-700">
    <h2 class="text-lg font-bold text-surface-900 dark:text-surface-50">{title}</h2>
  </div>

  {#if !$currentProject}
    <div class="flex-1 flex items-center justify-center p-4">
      <p class="text-surface-500 text-center">{$translate('selectCodeFolder')}</p>
    </div>
  {:else}
    <!-- Path breadcrumb -->
    <div class="px-4 py-2 bg-surface-100 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
      <div class="flex items-center gap-2">
        <button
          class="btn btn-sm variant-ghost"
          onclick={handleGoUp}
          disabled={pathHistory.length <= 1}
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </button>
        <span class="text-xs text-surface-700 dark:text-surface-300 font-mono truncate">{currentPath}</span>
      </div>
    </div>

    <!-- File list -->
    <div class="flex-1 overflow-y-auto p-2">
      {#if loading}
        <div class="flex items-center justify-center h-full">
          <p class="text-surface-500">{$translate('loading')}</p>
        </div>
      {:else if error}
        <div class="flex items-center justify-center h-full">
          <p class="text-error-500">{error}</p>
        </div>
      {:else if entries.length === 0}
        <div class="flex items-center justify-center h-full">
          <p class="text-surface-500">{$translate('emptyDirectory')}</p>
        </div>
      {:else}
        <div class="space-y-1">
          {#each entries as entry}
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
