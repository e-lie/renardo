<script lang="ts">
  import type { LayoutManager } from '../../lib/layout/LayoutManager';
  import type { Pane } from '../../lib/layout/Pane';
  import type { TabInterface, BufferInterface } from '../../models/editor';
  import TabbedPane from './TabbedPane.component.svelte';
  import EditorTabs from '../editor/EditorTabs.component.svelte';
  import CodeEditor from '../editor/CodeEditor.component.svelte';
  import { useEditorStore } from '../../store/editor';

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

  // Import EditorStore for buffer management
  const { actions } = useEditorStore();

  let panes = $state<Pane[]>([]);

  $effect(() => {
    const unsub = layoutManager.panes.subscribe(p => panes = p);
    return unsub;
  });

  function getPaneByPosition(pos: string): Pane | null {
    return panes.find(p => p.getState().position === pos) || null;
  }

  function togglePaneVisibility(pos: string) {
    // Toggle all panes in a column/row
    const leftPanes = ['left-top', 'left-bottom'];
    const rightPanes = ['right-top', 'right-bottom'];
    const bottomPanes = ['bottom-left', 'bottom-right'];
    
    let panesToToggle: string[] = [];
    
    if (pos === 'left-top' || pos === 'left') {
      panesToToggle = leftPanes;
    } else if (pos === 'right-top' || pos === 'right') {
      panesToToggle = rightPanes;
    } else if (pos === 'bottom-left' || pos === 'bottom') {
      panesToToggle = bottomPanes;
    } else {
      panesToToggle = [pos];
    }
    
    const anyVisible = panesToToggle.some(p => getPaneByPosition(p)?.getState().isVisible);
    
    panesToToggle.forEach(panePos => {
      const pane = getPaneByPosition(panePos);
      if (pane) {
        pane.setVisible(!anyVisible);
      }
    });
  }

  function isAnyPaneVisible(positions: string[]): boolean {
    return positions.some(pos => getPaneByPosition(pos)?.getState().isVisible);
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

  <!-- Floating Toggle Buttons -->
    <!-- Floating Toggle Buttons -->
  {#if isAnyPaneVisible(['left-top', 'left-bottom'])}
    <button 
      class="fixed left-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('left')}
      title="Toggle Left Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed left-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('left')}
      title="Show Left Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  {/if}

  {#if isAnyPaneVisible(['right-top', 'right-bottom'])}
    <button 
      class="fixed right-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('right')}
      title="Toggle Right Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed right-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('right')}
      title="Show Right Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
      </svg>
    </button>
  {/if}

  {#if isAnyPaneVisible(['bottom-left', 'bottom-right'])}
    <button 
      class="fixed bottom-4 left-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateX(-50%);"
      onclick={() => togglePaneVisibility('bottom')}
      title="Toggle Bottom Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed bottom-4 left-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateX(-50%);"
      onclick={() => togglePaneVisibility('bottom')}
      title="Show Bottom Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
      </svg>
    </button>
  {/if}

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
            {#if activeBuffer}
              <CodeEditor 
                buffer={activeBuffer}
                onchange={(content) => {
                  console.log('Central editor content changed:', content);
                  if (activeBuffer) {
                    actions.updateBufferContent(activeBuffer.id, content);
                  }
                }}
                onexecute={(code) => {
                  console.log('Central editor execute:', code);
                  actions.executeCode(code);
                }}
              />
            {:else}
              <div class="flex items-center justify-center h-full">
                <p class="text-base-content/50">No active buffer in central editor</p>
              </div>
            {/if}
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
