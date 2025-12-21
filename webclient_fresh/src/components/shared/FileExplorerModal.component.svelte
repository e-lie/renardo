<script lang="ts">
  import type { DirectoryEntry } from '../../models/file-explorer'

  let {
    isOpen = false,
    mode = 'select-folder',
    initialPath = null,
    onclose,
    onselect
  }: {
    isOpen?: boolean
    mode?: 'select-folder' | 'save-file'
    initialPath?: string | null
    onclose: () => void
    onselect: (path: string) => void
  } = $props()

  let currentPath = $state<string>('/')
  let entries = $state<DirectoryEntry[]>([])
  let selectedPath = $state<string | null>(null)
  let fileName = $state<string>('')
  let loading = $state<boolean>(false)
  let error = $state<string | null>(null)

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

  // Initialize with initial path, project folder, or home directory
  $effect(() => {
    if (isOpen) {
      async function initializeDirectory() {
        // Use initialPath if provided
        if (initialPath) {
          loadDirectory(initialPath)
          return
        }

        // Otherwise use home directory
        try {
          const response = await fetch('http://localhost:8000/api/file-explorer/home')
          if (response.ok) {
            const data = await response.json()
            loadDirectory(data.path)
          } else {
            loadDirectory('/')
          }
        } catch (e) {
          loadDirectory('/')
        }
      }
      initializeDirectory()
    }
  })

  function handleEntryClick(entry: DirectoryEntry) {
    if (entry.is_directory) {
      selectedPath = entry.path
      loadDirectory(entry.path)
    } else {
      selectedPath = entry.path
      fileName = entry.name
    }
  }

  async function handleGoUp() {
    try {
      const response = await fetch(`http://localhost:8000/api/file-explorer/parent?path=${encodeURIComponent(currentPath)}`)
      if (response.ok) {
        const data = await response.json()
        loadDirectory(data.path)
      }
    } catch (e) {
      // Fallback to manual parent calculation
      const parts = currentPath.split('/').filter(p => p)
      if (parts.length > 0) {
        parts.pop()
        const parent = '/' + parts.join('/')
        loadDirectory(parent || '/')
      }
    }
  }

  function handleSelect() {
    if (mode === 'select-folder' && selectedPath) {
      onselect(selectedPath)
    } else if (mode === 'save-file' && fileName) {
      const fullPath = currentPath + '/' + fileName
      onselect(fullPath)
    }
  }

  function handleCancel() {
    selectedPath = null
    fileName = ''
    onclose()
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
    <div class="bg-surface-50 dark:bg-surface-900 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-surface-300 dark:border-surface-700">
        <h2 class="text-xl font-bold text-surface-900 dark:text-surface-50">
          {mode === 'select-folder' ? 'Select Folder' : 'Save File'}
        </h2>
        <button class="btn btn-sm variant-ghost" onclick={handleCancel}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Path breadcrumb -->
      <div class="px-4 py-2 bg-surface-100 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
        <div class="flex items-center gap-2">
          <button class="btn btn-sm variant-ghost" onclick={handleGoUp} disabled={currentPath === '/'}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
          </button>
          <span class="text-sm text-surface-700 dark:text-surface-300 font-mono">{currentPath}</span>
        </div>
      </div>

      <!-- File list -->
      <div class="flex-1 overflow-y-auto p-4">
        {#if loading}
          <div class="flex items-center justify-center h-full">
            <p class="text-surface-500">Loading...</p>
          </div>
        {:else if error}
          <div class="flex items-center justify-center h-full">
            <p class="text-error-500">{error}</p>
          </div>
        {:else if entries.length === 0}
          <div class="flex items-center justify-center h-full">
            <p class="text-surface-500">Empty directory</p>
          </div>
        {:else}
          <div class="space-y-1">
            {#each entries as entry}
              <button
                class="w-full text-left px-3 py-2 rounded-lg transition-colors {selectedPath === entry.path ? 'bg-primary-500/20 border-primary-500' : 'hover:bg-surface-200 dark:hover:bg-surface-800'}"
                onclick={() => handleEntryClick(entry)}
              >
                <div class="flex items-center gap-2">
                  {#if entry.is_directory}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 text-warning-500">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                    </svg>
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 text-surface-500">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                  {/if}
                  <span class="text-surface-900 dark:text-surface-50">{entry.name}</span>
                </div>
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <!-- File name input (for save mode) -->
      {#if mode === 'save-file'}
        <div class="px-4 py-3 border-t border-surface-300 dark:border-surface-700">
          <label class="block">
            <span class="text-sm text-surface-700 dark:text-surface-300">File name:</span>
            <input
              type="text"
              class="input mt-1"
              bind:value={fileName}
              placeholder="Enter file name..."
            />
          </label>
        </div>
      {/if}

      <!-- Footer -->
      <div class="flex items-center justify-end gap-2 p-4 border-t border-surface-300 dark:border-surface-700">
        <button class="btn variant-ghost" onclick={handleCancel}>
          Cancel
        </button>
        <button
          class="btn variant-filled-primary"
          onclick={handleSelect}
          disabled={mode === 'select-folder' ? !selectedPath : !fileName}
        >
          {mode === 'select-folder' ? 'Select' : 'Save'}
        </button>
      </div>
    </div>
  </div>
{/if}
