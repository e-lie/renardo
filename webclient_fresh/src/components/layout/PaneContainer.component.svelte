<script lang="ts">
  import type { PanePosition } from '../../models/layout'
  import TabbedPane from './children/TabbedPane.component.svelte'
  import CodeEditor from '../editor/CodeEditor.component.svelte'
  import TopMenu from './children/TopMenu.component.svelte'
  import { useEditorStore } from '../../store/editor'

  let {
    position,
    width,
    height,
    minWidth,
    minHeight
  }: {
    position: PanePosition
    width?: number
    height?: number
    minWidth?: number
    minHeight?: number
  } = $props()

  const { getters, actions } = useEditorStore()
  const { activeBuffer, tabs } = getters

  // Initialize with at least one tab for center position
  $effect(() => {
    if (position === 'center' && $tabs.length === 0) {
      const bufferId = actions.createBuffer({
        name: 'Untitled',
        content: '',
        language: 'python',
      })
      actions.createTab(bufferId)
    }
  })

  const style = $derived.by(() => {
    let s = ''
    if (width) s += `width: ${width}px; `
    if (height) s += `height: ${height}px; `
    if (minWidth) s += `min-width: ${minWidth}px; `
    if (minHeight) s += `min-height: ${minHeight}px; `
    return s
  })

  const bgColor = $derived.by(() => {
    const colors = {
      'top-menu': 'bg-surface-200 dark:bg-surface-800',
      'left-top': 'bg-primary-500/10 dark:bg-primary-500/20',
      'left-middle': 'bg-primary-500/20 dark:bg-primary-500/30',
      'left-bottom': 'bg-secondary-500/10 dark:bg-secondary-500/20',
      'right-top': 'bg-tertiary-500/10 dark:bg-tertiary-500/20',
      'right-middle': 'bg-tertiary-500/20 dark:bg-tertiary-500/30',
      'right-bottom': 'bg-success-500/10 dark:bg-success-500/20',
      'bottom-left': 'bg-warning-500/10 dark:bg-warning-500/20',
      'bottom-right': 'bg-error-500/10 dark:bg-error-500/20',
      'center': 'bg-surface-100 dark:bg-surface-900'
    }
    return colors[position] || 'bg-surface-100 dark:bg-surface-900'
  })

  const cssClass = $derived(
    `h-full ${bgColor} border border-surface-300 dark:border-surface-700 overflow-hidden`
  )

  function handleChange(content: string) {
    if ($activeBuffer) {
      actions.updateBufferContent($activeBuffer.id, content)
    }
  }

  function handleExecute(code: string) {
    actions.executeCode(code)
  }

  function handleCreateTab() {
    const newBufferId = actions.createBuffer({
      name: 'Untitled',
      content: '',
      language: 'python',
    })
    const newTabId = actions.createTab(newBufferId)
    actions.switchToTab(newTabId)
  }

  function handleSwitchTab(tabId: string) {
    actions.switchToTab(tabId)
  }

  function handleCloseTab(tabId: string) {
    actions.closeTab(tabId)
  }
</script>

<div class={cssClass} {style}>
  {#if position === 'center'}
    <div class="h-full flex flex-col">
      {#if $tabs.length > 1}
        <!-- Tab bar -->
        <div class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
          {#each $tabs as tab}
            <div class="flex items-center group">
              <button
                class="px-3 py-2 text-sm transition-colors {tab.isActive ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500' : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
                onclick={() => handleSwitchTab(tab.id)}
              >
                <span class="text-surface-900 dark:text-surface-50">{tab.title}</span>
              </button>
              {#if !tab.isPinned}
                <button
                  class="px-1 opacity-0 group-hover:opacity-100 transition-opacity text-surface-500 hover:text-surface-900 dark:hover:text-surface-50"
                  onclick={() => handleCloseTab(tab.id)}
                  title="Close tab"
                >
                  ×
                </button>
              {/if}
            </div>
          {/each}
        </div>
      {/if}

      <!-- Editor content -->
      <div class="flex-1 overflow-hidden">
        <CodeEditor buffer={$activeBuffer} onchange={handleChange} onexecute={handleExecute} oncreatetab={handleCreateTab} />
      </div>
    </div>
  {:else if position === 'top-menu'}
    <TopMenu />
  {:else}
    <TabbedPane {position} />
  {/if}
</div>
