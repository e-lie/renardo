<script lang="ts">
  import type { LayoutManager } from '../../lib/layout/LayoutManager';
  import type { Pane } from '../../lib/layout/Pane';
  import type { TabInterface, BufferInterface } from '../../models/editor';
  import TabbedPane from './TabbedPane.component.svelte';
  import EditorTabs from '../editor/EditorTabs.component.svelte';
  import CodeEditor from '../editor/CodeEditor.component.svelte';

  let {
    layoutManager,
    tabs,
    buffers,
    onswitch,
    onclose,
    oncreate,
    onsettings,
    activeBuffer,
  }: {
    layoutManager: LayoutManager;
    tabs: TabInterface[];
    buffers: BufferInterface[];
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
    oncreate?: () => void;
    onsettings?: () => void;
    activeBuffer: BufferInterface | null;
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
  grid-template-columns: 300px 1fr 300px;
  grid-template-rows: 300px 1fr 200px;
  gap: 4px;
  padding: 4px;
">
  <!-- Left Top Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'left-top' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: left-top;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Right Top Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'right-top' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: right-top;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Left Bottom Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'left-bottom' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: left-bottom;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Right Bottom Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'right-bottom' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: right-bottom;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Bottom Left Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'bottom-left' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: bottom-left;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Bottom Right Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'bottom-right' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: bottom-right;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Center Pane (always visible) - Contains original editor -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'center' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col bg-base-200"
        style="grid-area: center;"
      >
        <!-- Original Editor Tabs -->
        <div class="bg-base-200 border-b border-base-300">
          <EditorTabs
            tabs={tabs}
            buffers={buffers}
            onswitch={onswitch}
            onclose={onclose}
            oncreate={oncreate}
            onsettings={onsettings}
          />
        </div>

        <!-- Original Code Editor -->
        <div class="flex-1 overflow-hidden">
          {#if activeBuffer}
            <CodeEditor 
              buffer={activeBuffer}
              onchange={(content) => {
                // TODO: Update buffer content
              }}
              onexecute={(code) => {
                // TODO: Execute code
              }}
            />
          {:else}
            <div class="p-4 text-center text-base-content/50">
              No active buffer
            </div>
          {/if}
        </div>
      </div>
    {/if}
  {/each}
</div>
