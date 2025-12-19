<script lang="ts">
  import { useLayoutStore } from '../../store/layout'
  import type { PanePosition } from '../../models/layout'

  const { getters, actions } = useLayoutStore()
  const { paneSetVisibility } = getters

  // Pane visibility for individual panes (local state for UI)
  let localPaneVisibility = $state<Record<string, boolean>>({
    'top-menu': true,
    'left-top': true,
    'left-middle': true,
    'left-bottom': true,
    'right-top': true,
    'right-middle': true,
    'right-bottom': true,
    'bottom-left': true,
    'bottom-right': true
  })

  function getPaneColor(position: string): string {
    const colors: Record<string, string> = {
      'top-menu': 'bg-surface-200 dark:bg-surface-800',
      'left-top': 'bg-primary-500/10 dark:bg-primary-500/20',
      'left-middle': 'bg-primary-500/20 dark:bg-primary-500/30',
      'left-bottom': 'bg-secondary-500/10 dark:bg-secondary-500/20',
      'right-top': 'bg-tertiary-500/10 dark:bg-tertiary-500/20',
      'right-middle': 'bg-tertiary-500/20 dark:bg-tertiary-500/30',
      'right-bottom': 'bg-success-500/10 dark:bg-success-500/20',
      'bottom-left': 'bg-warning-500/10 dark:bg-warning-500/20',
      'bottom-right': 'bg-error-500/10 dark:bg-error-500/20'
    }
    return colors[position] || 'bg-surface-100 dark:bg-surface-900'
  }

  function togglePane(paneId: string) {
    localPaneVisibility[paneId] = !localPaneVisibility[paneId]
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
            checked={localPaneVisibility['top-menu']}
            onchange={() => togglePane('top-menu')}
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
              checked={localPaneVisibility['left-top']}
              onchange={() => togglePane('left-top')}
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
              checked={localPaneVisibility['left-middle']}
              onchange={() => togglePane('left-middle')}
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
              checked={localPaneVisibility['left-bottom']}
              onchange={() => togglePane('left-bottom')}
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
              checked={localPaneVisibility['right-top']}
              onchange={() => togglePane('right-top')}
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
              checked={localPaneVisibility['right-middle']}
              onchange={() => togglePane('right-middle')}
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
              checked={localPaneVisibility['right-bottom']}
              onchange={() => togglePane('right-bottom')}
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
            checked={localPaneVisibility['bottom-left']}
            onchange={() => togglePane('bottom-left')}
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
            checked={localPaneVisibility['bottom-right']}
            onchange={() => togglePane('bottom-right')}
          />
        </div>
      </div>
    </div>
  </div>
</div>
