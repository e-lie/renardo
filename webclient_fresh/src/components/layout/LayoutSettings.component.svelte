<script lang="ts">
  import type { LayoutManager } from '../../lib/layout/LayoutManager';
  import type { Pane } from '../../lib/layout/Pane';

  let {
    layoutManager,
  }: {
    layoutManager: LayoutManager;
  } = $props();

  const positions = ['left-top', 'left-bottom', 'right-top', 'right-bottom', 'bottom-left', 'bottom-right'] as const;

  let panes = $state<Pane[]>([]);

  $effect(() => {
    const unsub = layoutManager.panes.subscribe(p => panes = p);
    return unsub;
  });

  function getPaneByPosition(pos: string): Pane | null {
    return panes.find(p => p.getState().position === pos) || null;
  }

  function togglePaneVisibility(pos: string) {
    const pane = getPaneByPosition(pos);
    if (pane) {
      pane.setVisible(!pane.getState().isVisible);
    }
  }

  function addComponentToPane(pos: string, componentType: string) {
    const pane = getPaneByPosition(pos);
    if (pane) {
      pane.addTab(componentType, componentType, {}, true);
      pane.setVisible(true);
    }
  }
</script>

<div class="space-y-4">
  <h3 class="text-lg font-semibold">Pane Configuration</h3>

  {#each positions as position}
    {@const pane = getPaneByPosition(position)}
    {#if pane}
      <div class="card bg-base-200 p-4">
        <div class="flex items-center justify-between mb-2">
          <label class="flex items-center gap-2">
            <input
              type="checkbox"
              class="checkbox checkbox-primary"
              checked={pane.getState().isVisible}
              onchange={() => togglePaneVisibility(position)}
            />
            <span class="font-medium">{position}</span>
          </label>
        </div>

        {#if pane.getState().isVisible}
          <div class="mt-2">
            <select
              class="select select-bordered select-sm w-full"
              onchange={(e) => {
                const value = (e.target as HTMLSelectElement).value;
                if (value) {
                  addComponentToPane(position, value);
                  (e.target as HTMLSelectElement).value = '';
                }
              }}
            >
              <option value="">Add component...</option>
              <option value="CodeEditor">Code Editor</option>
              <option value="TextArea">Text Area</option>
            </select>

            {#if pane.getState().tabs.size > 0}
              <div class="mt-2 text-sm">
                Tabs: {Array.from(pane.getState().tabs.values()).map(t => t.getState().title).join(', ')}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/if}
  {/each}
</div>
