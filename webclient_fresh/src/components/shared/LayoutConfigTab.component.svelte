<script lang="ts">
  import { useLayoutStore } from '../../store/layout'
  import type { PanePosition } from '../../models/layout'

  const { getters, actions } = useLayoutStore()
  const { paneSetVisibility, paneVisibility, paneTabConfigs } = getters

  function getPaneColor(position: string): string {
    if (position === 'top-menu') {
      return 'bg-surface-200 dark:bg-surface-800'
    }
    return 'bg-surface-100 dark:bg-surface-900'
  }

  function addTabToPane(position: string, componentType: 'TextArea' | 'CodeEditor' | 'ConsoleOutput' | 'TutorialTab') {
    const titles = {
      'TextArea': 'Text Area',
      'CodeEditor': 'Code Editor',
      'ConsoleOutput': 'ฅ^•ﻌ•^ฅ >> output',
      'TutorialTab': 'Tutorials'
    }
    actions.addTab(position, {
      title: titles[componentType],
      componentType,
      componentId: `${componentType.toLowerCase()}-${position}-${Date.now()}`,
      closable: true,
      active: false
    })
  }

  function removeTabFromPane(position: string, tabId: string) {
    actions.removeTab(position, tabId)
  }

  function moveTabUp(position: string, tabId: string) {
    actions.moveTab(position, tabId, 'up')
  }

  function moveTabDown(position: string, tabId: string) {
    actions.moveTab(position, tabId, 'down')
  }

  let openMenuPosition = $state<string | null>(null)

  function toggleMenu(position: string) {
    openMenuPosition = openMenuPosition === position ? null : position
  }
</script>

<div class="space-y-4">
  <h3 class="h3">Layout Configuration</h3>

  <!-- Pane Set Toggles -->
  <div class="space-y-2">
    <h4 class="h4 text-sm">Pane Sets</h4>
    <div class="flex gap-2">
      <button
        class="btn btn-sm {$paneSetVisibility.left ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('left')}
      >
        Left Panes
      </button>
      <button
        class="btn btn-sm {$paneSetVisibility.right ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('right')}
      >
        Right Panes
      </button>
      <button
        class="btn btn-sm {$paneSetVisibility.bottom ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('bottom')}
      >
        Bottom Panes
      </button>
    </div>
  </div>

  <!-- Visual Layout Grid -->
  <div class="flex flex-col gap-2 p-4 bg-surface-200 dark:bg-surface-800 rounded-lg h-[400px]">
    <!-- Top Row - Top Menu -->
    <div class="flex h-[15%]">
      <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('top-menu')}">
        <div class="flex flex-col items-center gap-1">
          <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Top Menu</span>
          <input
            type="checkbox"
            class="checkbox checkbox-sm"
            checked={$paneVisibility.get('top-menu')}
            onchange={() => actions.togglePaneVisibility('top-menu')}
          />
        </div>
      </div>
    </div>

    <!-- Middle Row -->
    <div class="flex flex-1 gap-2">
      <!-- Left Column -->
      <div class="flex flex-col gap-2 w-[25%]">
        <!-- Left Top -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('left-top')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Left Top</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('left-top')}
              onchange={() => actions.togglePaneVisibility('left-top')}
            />
          </div>
        </div>
        <!-- Left Middle -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('left-middle')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Left Mid</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('left-middle')}
              onchange={() => actions.togglePaneVisibility('left-middle')}
            />
          </div>
        </div>
        <!-- Left Bottom -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('left-bottom')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Left Bot</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('left-bottom')}
              onchange={() => actions.togglePaneVisibility('left-bottom')}
            />
          </div>
        </div>
      </div>

      <!-- Center -->
      <div class="flex-1 flex items-center justify-center border-2 border-primary-500 rounded-lg bg-surface-100 dark:bg-surface-900">
        <span class="text-sm font-bold text-surface-900 dark:text-surface-50">Code Editor</span>
      </div>

      <!-- Right Column -->
      <div class="flex flex-col gap-2 w-[25%]">
        <!-- Right Top -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('right-top')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Right Top</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('right-top')}
              onchange={() => actions.togglePaneVisibility('right-top')}
            />
          </div>
        </div>
        <!-- Right Middle -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('right-middle')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Right Mid</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('right-middle')}
              onchange={() => actions.togglePaneVisibility('right-middle')}
            />
          </div>
        </div>
        <!-- Right Bottom -->
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('right-bottom')}">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Right Bot</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get('right-bottom')}
              onchange={() => actions.togglePaneVisibility('right-bottom')}
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="flex h-[25%] gap-2">
      <!-- Bottom Left -->
      <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('bottom-left')}">
        <div class="flex flex-col items-center gap-1">
          <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Bottom Left</span>
          <input
            type="checkbox"
            class="checkbox checkbox-sm"
            checked={$paneVisibility.get('bottom-left')}
            onchange={() => actions.togglePaneVisibility('bottom-left')}
          />
        </div>
      </div>
      <!-- Bottom Right -->
      <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor('bottom-right')}">
        <div class="flex flex-col items-center gap-1">
          <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">Bottom Right</span>
          <input
            type="checkbox"
            class="checkbox checkbox-sm"
            checked={$paneVisibility.get('bottom-right')}
            onchange={() => actions.togglePaneVisibility('bottom-right')}
          />
        </div>
      </div>
    </div>
  </div>

  <!-- Tab Management Section -->
  <div class="divider">Pane Tab Management</div>
  <div class="alert alert-info mb-4">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>
    <span class="text-sm">Each pane can contain multiple components in tabs. Add ColorPicker or TextArea components to any pane.</span>
  </div>

  <!-- Tab management grid -->
  <div class="flex flex-col gap-2 p-4 bg-surface-100 dark:bg-surface-900 rounded-lg" style="min-height: 400px;">

    <!-- Middle Row -->
    <div class="flex flex-1 gap-2">
      <!-- Left Column -->
      <div class="flex flex-col gap-2 w-[25%]">
        {#each ['left-top', 'left-middle', 'left-bottom'] as position}
          <div class="flex-1 flex flex-col border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor(position)} p-2 min-h-0">
            {#if $paneVisibility.get(position)}
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{position.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                <span class="badge badge-xs badge-primary">{$paneTabConfigs.get(position)?.length || 0}</span>
              </div>
              <div class="flex-1 overflow-y-auto min-h-0 space-y-1">
                {#each ($paneTabConfigs.get(position) || []) as tab, index}
                  <div class="flex items-center gap-1 p-1 text-xs rounded {tab.active ? 'bg-primary-500/20' : 'bg-surface-200 dark:bg-surface-800'}">
                    <div class="flex flex-col">
                      <button
                        class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                        onclick={() => moveTabUp(position, tab.id)}
                        disabled={index === 0}
                      >▲</button>
                      <button
                        class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                        onclick={() => moveTabDown(position, tab.id)}
                        disabled={index === ($paneTabConfigs.get(position)?.length || 0) - 1}
                      >▼</button>
                    </div>
                    <span>{tab.componentType === 'TextArea' ? '📝' : tab.componentType === 'ConsoleOutput' ? 'ฅ^•ﻌ•^ฅ' : tab.componentType === 'TutorialTab' ? '📚' : '💻'}</span>
                    <span class="flex-1 truncate text-surface-900 dark:text-surface-50">{tab.title}</span>
                    {#if tab.closable}
                      <button class="text-error-500 hover:bg-error-500/20 rounded px-1" onclick={() => removeTabFromPane(position, tab.id)}>×</button>
                    {/if}
                  </div>
                {/each}
              </div>
              <div class="relative mt-1">
                <button class="btn btn-xs variant-ghost w-full" onclick={() => toggleMenu(position)}>+ Add Component</button>
                {#if openMenuPosition === position}
                  <div class="absolute bottom-full left-0 mb-1 w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 rounded-lg shadow-lg z-10">
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-t-lg" onclick={() => { addTabToPane(position, 'TextArea'); openMenuPosition = null }}>
                      📝 Text Area
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700" onclick={() => { addTabToPane(position, 'CodeEditor'); openMenuPosition = null }}>
                      💻 Code Editor
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700" onclick={() => { addTabToPane(position, 'ConsoleOutput'); openMenuPosition = null }}>
                      ฅ^•ﻌ•^ฅ Console Output
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-b-lg" onclick={() => { addTabToPane(position, 'TutorialTab'); openMenuPosition = null }}>
                      📚 Tutorials
                    </button>
                  </div>
                {/if}
              </div>
            {:else}
              <div class="flex-1 flex items-center justify-center opacity-50">
                <span class="text-xs text-surface-600 dark:text-surface-400">Hidden</span>
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Center -->
      <div class="flex-1 flex items-center justify-center border-2 border-primary-500 rounded-lg bg-surface-100 dark:bg-surface-900">
        <div class="text-center">
          <span class="text-2xl mb-2">📝</span>
          <div class="text-sm font-bold text-surface-900 dark:text-surface-50">Code Editor</div>
          <div class="badge badge-xs badge-primary mt-1">Always Visible</div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="flex flex-col gap-2 w-[25%]">
        {#each ['right-top', 'right-middle', 'right-bottom'] as position}
          <div class="flex-1 flex flex-col border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor(position)} p-2 min-h-0">
            {#if $paneVisibility.get(position)}
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{position.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                <span class="badge badge-xs badge-primary">{$paneTabConfigs.get(position)?.length || 0}</span>
              </div>
              <div class="flex-1 overflow-y-auto min-h-0 space-y-1">
                {#each ($paneTabConfigs.get(position) || []) as tab, index}
                  <div class="flex items-center gap-1 p-1 text-xs rounded {tab.active ? 'bg-primary-500/20' : 'bg-surface-200 dark:bg-surface-800'}">
                    <div class="flex flex-col">
                      <button
                        class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                        onclick={() => moveTabUp(position, tab.id)}
                        disabled={index === 0}
                      >▲</button>
                      <button
                        class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                        onclick={() => moveTabDown(position, tab.id)}
                        disabled={index === ($paneTabConfigs.get(position)?.length || 0) - 1}
                      >▼</button>
                    </div>
                    <span>{tab.componentType === 'TextArea' ? '📝' : tab.componentType === 'ConsoleOutput' ? 'ฅ^•ﻌ•^ฅ' : tab.componentType === 'TutorialTab' ? '📚' : '💻'}</span>
                    <span class="flex-1 truncate text-surface-900 dark:text-surface-50">{tab.title}</span>
                    {#if tab.closable}
                      <button class="text-error-500 hover:bg-error-500/20 rounded px-1" onclick={() => removeTabFromPane(position, tab.id)}>×</button>
                    {/if}
                  </div>
                {/each}
              </div>
              <div class="relative mt-1">
                <button class="btn btn-xs variant-ghost w-full" onclick={() => toggleMenu(position)}>+ Add Component</button>
                {#if openMenuPosition === position}
                  <div class="absolute bottom-full left-0 mb-1 w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 rounded-lg shadow-lg z-10">
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-t-lg" onclick={() => { addTabToPane(position, 'TextArea'); openMenuPosition = null }}>
                      📝 Text Area
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700" onclick={() => { addTabToPane(position, 'CodeEditor'); openMenuPosition = null }}>
                      💻 Code Editor
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700" onclick={() => { addTabToPane(position, 'ConsoleOutput'); openMenuPosition = null }}>
                      ฅ^•ﻌ•^ฅ Console Output
                    </button>
                    <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-b-lg" onclick={() => { addTabToPane(position, 'TutorialTab'); openMenuPosition = null }}>
                      📚 Tutorials
                    </button>
                  </div>
                {/if}
              </div>
            {:else}
              <div class="flex-1 flex items-center justify-center opacity-50">
                <span class="text-xs text-surface-600 dark:text-surface-400">Hidden</span>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="flex gap-2" style="height: 150px;">
      {#each ['bottom-left', 'bottom-right'] as position}
        <div class="flex-1 flex flex-col border-2 border-surface-300 dark:border-surface-700 rounded-lg {getPaneColor(position)} p-2">
          {#if $paneVisibility.get(position)}
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{position.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
              <span class="badge badge-xs badge-primary">{$paneTabConfigs.get(position)?.length || 0}</span>
            </div>
            <div class="flex-1 overflow-y-auto space-y-1">
              {#each ($paneTabConfigs.get(position) || []) as tab, index}
                <div class="flex items-center gap-1 p-1 text-xs rounded {tab.active ? 'bg-primary-500/20' : 'bg-surface-200 dark:bg-surface-800'}">
                  <div class="flex flex-col">
                    <button
                      class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                      onclick={() => moveTabUp(position, tab.id)}
                      disabled={index === 0}
                    >▲</button>
                    <button
                      class="text-surface-600 dark:text-surface-400 hover:text-primary-500 disabled:opacity-30"
                      onclick={() => moveTabDown(position, tab.id)}
                      disabled={index === ($paneTabConfigs.get(position)?.length || 0) - 1}
                    >▼</button>
                  </div>
                  <span>{tab.componentType === 'ColorPicker' ? '🎨' : tab.componentType === 'TextArea' ? '📝' : tab.componentType === 'ConsoleOutput' ? 'ฅ^•ﻌ•^ฅ' : '💻'}</span>
                  <span class="flex-1 truncate text-surface-900 dark:text-surface-50">{tab.title}</span>
                  {#if tab.closable}
                    <button class="text-error-500 hover:bg-error-500/20 rounded px-1" onclick={() => removeTabFromPane(position, tab.id)}>×</button>
                  {/if}
                </div>
              {/each}
            </div>
            <div class="relative mt-1">
              <button class="btn btn-xs variant-ghost w-full" onclick={() => toggleMenu(position)}>+ Add Component</button>
              {#if openMenuPosition === position}
                <div class="absolute bottom-full left-0 mb-1 w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 rounded-lg shadow-lg z-10">
                  <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-t-lg" onclick={() => { addTabToPane(position, 'ColorPicker'); openMenuPosition = null }}>
                    🎨 Color Picker
                  </button>
                  <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700" onclick={() => { addTabToPane(position, 'TextArea'); openMenuPosition = null }}>
                    📝 Text Area
                  </button>
                  <button class="w-full px-2 py-1 text-left text-xs hover:bg-surface-200 dark:hover:bg-surface-700 rounded-b-lg" onclick={() => { addTabToPane(position, 'CodeEditor'); openMenuPosition = null }}>
                    💻 Code Editor
                  </button>
                </div>
              {/if}
            </div>
          {:else}
            <div class="flex-1 flex items-center justify-center opacity-50">
              <span class="text-xs text-surface-600 dark:text-surface-400">Hidden</span>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</div>
