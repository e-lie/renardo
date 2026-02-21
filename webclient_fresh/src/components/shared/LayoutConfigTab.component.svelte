<script lang="ts">
  import { useLayoutStore } from '../../store/layout'
  import { useI18nStore } from '../../store/i18n/I18n.store'
  import type { PanePosition } from '../../models/layout'

  const { getters, actions } = useLayoutStore()
  const { paneSetVisibility, paneVisibility, paneTabConfigs } = getters

  const i18n = useI18nStore()
  const { translate } = i18n.getters

  type ComponentType = 'TextArea' | 'CodeEditor' | 'CodeExecConsole' | 'TutorialTab' | 'MusicExampleTab' | 'ProjectExplorerTab' | 'UserDirectoryExplorerTab' | 'ClockDisplay' | 'ColorPicker'

  const COMPONENT_META: Record<ComponentType, { icon: string; label: string; title: string }> = {
    TextArea:                 { icon: '📝', label: 'Text Area',        title: 'Text Area' },
    CodeEditor:               { icon: '💻', label: 'Code Editor',      title: 'Code Editor' },
    CodeExecConsole:          { icon: 'ฅ^•ﻌ•^ฅ', label: 'Console Output', title: 'ฅ^•ﻌ•^ฅ >> output' },
    TutorialTab:              { icon: '📚', label: 'Tutorials',        title: 'Tutorials' },
    MusicExampleTab:          { icon: '🎵', label: 'Music Examples',   title: 'Music Examples' },
    ProjectExplorerTab:       { icon: '📁', label: 'Project Explorer', title: 'Project Explorer' },
    UserDirectoryExplorerTab: { icon: '🏠', label: 'User Directory',   title: 'User Directory' },
    ClockDisplay:             { icon: '🕐', label: 'Clock',            title: 'Clock' },
    ColorPicker:              { icon: '🎨', label: 'Color Picker',     title: 'Color Picker' },
  }

  const PANE_GROUPS: { label: string; positions: string[]; components: ComponentType[] }[] = [
    {
      label: 'Left Column',
      positions: ['left-top', 'left-middle', 'left-bottom'],
      components: ['TextArea', 'CodeEditor', 'CodeExecConsole', 'TutorialTab', 'MusicExampleTab', 'ProjectExplorerTab', 'UserDirectoryExplorerTab', 'ClockDisplay'],
    },
    {
      label: 'Right Column',
      positions: ['right-top', 'right-middle', 'right-bottom'],
      components: ['TextArea', 'CodeEditor', 'CodeExecConsole', 'TutorialTab', 'MusicExampleTab', 'ProjectExplorerTab', 'UserDirectoryExplorerTab', 'ClockDisplay'],
    },
    {
      label: 'Bottom Area',
      positions: ['bottom-left', 'bottom-right'],
      components: ['TextArea', 'CodeEditor', 'CodeExecConsole', 'TutorialTab', 'MusicExampleTab', 'ProjectExplorerTab', 'UserDirectoryExplorerTab', 'ClockDisplay', 'ColorPicker'],
    },
  ]

  function positionLabel(position: string): string {
    return position.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  }

  function addTabToPane(position: string, componentType: ComponentType) {
    const meta = COMPONENT_META[componentType]
    actions.addTab(position, {
      title: meta.title,
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
  <h3 class="h3">{$translate('layoutConfiguration')}</h3>

  <!-- Pane Set Toggles -->
  <div class="space-y-2">
    <h4 class="h4 text-sm">Pane Sets</h4>
    <div class="flex gap-2">
      <button
        class="btn btn-sm {$paneSetVisibility.left ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('left')}
      >
        {$paneSetVisibility.left ? $translate('hide') : $translate('show')} {$translate('leftColumn')}
      </button>
      <button
        class="btn btn-sm {$paneSetVisibility.right ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('right')}
      >
        {$paneSetVisibility.right ? $translate('hide') : $translate('show')} {$translate('rightColumn')}
      </button>
      <button
        class="btn btn-sm {$paneSetVisibility.bottom ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => actions.togglePaneSet('bottom')}
      >
        {$paneSetVisibility.bottom ? $translate('hide') : $translate('show')} {$translate('bottomArea')}
      </button>
    </div>
  </div>

  <!-- Visual Layout Grid -->
  <div class="flex flex-col gap-2 p-4 bg-surface-200 dark:bg-surface-800 rounded-lg h-[400px]">
    <!-- Top Row - Top Menu -->
    <div class="flex h-[15%]">
      <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg bg-surface-200 dark:bg-surface-800">
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
        {#each ['left-top', 'left-middle', 'left-bottom'] as position}
          <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg bg-surface-100 dark:bg-surface-900">
            <div class="flex flex-col items-center gap-1">
              <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{positionLabel(position)}</span>
              <input
                type="checkbox"
                class="checkbox checkbox-sm"
                checked={$paneVisibility.get(position)}
                onchange={() => actions.togglePaneVisibility(position)}
              />
            </div>
          </div>
        {/each}
      </div>

      <!-- Center -->
      <div class="flex-1 flex items-center justify-center border-2 border-primary-500 rounded-lg bg-surface-100 dark:bg-surface-900">
        <span class="text-sm font-bold text-surface-900 dark:text-surface-50">Code Editor</span>
      </div>

      <!-- Right Column -->
      <div class="flex flex-col gap-2 w-[25%]">
        {#each ['right-top', 'right-middle', 'right-bottom'] as position}
          <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg bg-surface-100 dark:bg-surface-900">
            <div class="flex flex-col items-center gap-1">
              <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{positionLabel(position)}</span>
              <input
                type="checkbox"
                class="checkbox checkbox-sm"
                checked={$paneVisibility.get(position)}
                onchange={() => actions.togglePaneVisibility(position)}
              />
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="flex h-[25%] gap-2">
      {#each ['bottom-left', 'bottom-right'] as position}
        <div class="flex-1 flex items-center justify-center border-2 border-surface-300 dark:border-surface-700 rounded-lg bg-surface-100 dark:bg-surface-900">
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-semibold text-surface-900 dark:text-surface-50">{positionLabel(position)}</span>
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              checked={$paneVisibility.get(position)}
              onchange={() => actions.togglePaneVisibility(position)}
            />
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Tab Management -->
  <div class="divider">{$translate('paneTabManagement')}</div>

  <div class="space-y-6">
    {#each PANE_GROUPS as group}
      <div>
        <h4 class="h4 text-sm mb-2">{group.label}</h4>
        <div class="space-y-2">
          {#each group.positions as position}
            <div class="bg-surface-100 dark:bg-surface-900 rounded-lg p-3 space-y-2">
              <!-- Pane header -->
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold">{positionLabel(position)}</span>
                <span class="badge badge-xs badge-primary">{$paneTabConfigs.get(position)?.length || 0}</span>
              </div>

              <!-- Tab list -->
              {#each ($paneTabConfigs.get(position) || []) as tab, index}
                <div class="flex items-center gap-2 px-2 py-1 text-sm rounded bg-surface-200 dark:bg-surface-800">
                  <span class="shrink-0">{COMPONENT_META[tab.componentType as ComponentType]?.icon ?? '📦'}</span>
                  <span class="flex-1 truncate">{tab.title}</span>
                  <button
                    class="text-surface-500 hover:text-primary-500 disabled:opacity-30"
                    onclick={() => moveTabUp(position, tab.id)}
                    disabled={index === 0}
                  >▲</button>
                  <button
                    class="text-surface-500 hover:text-primary-500 disabled:opacity-30"
                    onclick={() => moveTabDown(position, tab.id)}
                    disabled={index === ($paneTabConfigs.get(position)?.length || 0) - 1}
                  >▼</button>
                  {#if tab.closable}
                    <button
                      class="text-error-500 hover:bg-error-500/20 rounded px-1"
                      onclick={() => removeTabFromPane(position, tab.id)}
                    >×</button>
                  {/if}
                </div>
              {/each}

              <!-- Add component -->
              <div class="relative">
                <button class="btn btn-xs variant-ghost w-full" onclick={() => toggleMenu(position)}>
                  + Add Component
                </button>
                {#if openMenuPosition === position}
                  <div class="absolute top-full left-0 mt-1 w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 rounded-lg shadow-lg z-10">
                    {#each group.components as componentType, i}
                      <button
                        class="w-full px-3 py-1.5 text-left text-sm hover:bg-surface-200 dark:hover:bg-surface-700
                          {i === 0 ? 'rounded-t-lg' : ''}
                          {i === group.components.length - 1 ? 'rounded-b-lg' : ''}"
                        onclick={() => { addTabToPane(position, componentType); openMenuPosition = null }}
                      >
                        {COMPONENT_META[componentType].icon} {COMPONENT_META[componentType].label}
                      </button>
                    {/each}
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>
