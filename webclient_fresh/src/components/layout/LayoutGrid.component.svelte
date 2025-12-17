<script lang="ts">
  import type { LayoutManager } from '../../lib/layout/LayoutManager';
  import type { Pane } from '../../lib/layout/Pane';
  import TabbedPane from './TabbedPane.component.svelte';

  let {
    layoutManager,
  }: {
    layoutManager: LayoutManager;
  } = $props();

  let panes = $state<Pane[]>([]);

  $effect(() => {
    const unsub = layoutManager.panes.subscribe(p => panes = p);
    return unsub;
  });

  function getPaneByPosition(pos: string): Pane | null {
    return panes.find(p => p.getState().position === pos) || null;
  }
</script>

<div class="layout-grid h-full grid" style="
  grid-template-areas:
    'left-top center right-top'
    'left-bottom center right-bottom'
    'bottom-left bottom-left bottom-right';
  grid-template-columns: auto 1fr auto;
  grid-template-rows: auto 1fr auto;
">
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().isVisible}
      <div
        class="pane-{pane.getState().position} border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: {pane.getState().position};"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}
</div>
