<script lang="ts">
  import { useLayoutStore } from '../../../store/layout'

  let {
    componentId,
    title = 'Top Menu'
  }: {
    componentId: string
    title?: string
  } = $props()

  const { getters: layoutGetters, actions: layoutActions } = useLayoutStore()
  const { paneSetVisibility } = layoutGetters
</script>

<div class="h-full flex items-center justify-between px-4 bg-surface-200 dark:bg-surface-800">
  <div class="flex items-center gap-2">
    <div class="text-lg font-bold text-surface-900 dark:text-surface-50">
      Renardo
    </div>

    <div class="flex gap-1">
      <button
        class="btn btn-sm {$paneSetVisibility.left ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => layoutActions.togglePaneSet('left')}
        title={$paneSetVisibility.left ? 'Hide left panes' : 'Show left panes'}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
        </svg>
      </button>

      <button
        class="btn btn-sm {$paneSetVisibility.right ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => layoutActions.togglePaneSet('right')}
        title={$paneSetVisibility.right ? 'Hide right panes' : 'Show right panes'}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M12 17.25h8.25" />
        </svg>
      </button>

      <button
        class="btn btn-sm {$paneSetVisibility.bottom ? 'variant-filled-primary' : 'variant-ghost'}"
        onclick={() => layoutActions.togglePaneSet('bottom')}
        title={$paneSetVisibility.bottom ? 'Hide bottom panes' : 'Show bottom panes'}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>
    </div>
  </div>
</div>
