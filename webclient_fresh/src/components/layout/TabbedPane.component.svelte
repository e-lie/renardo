<script lang="ts">
  import type { Pane } from '../../lib/layout/Pane';
  import { PANE_COMPONENT_REGISTRY } from './panes';

  let {
    pane,
    oncloseTab,
  }: {
    pane: Pane;
    oncloseTab?: (tabId: string) => void;
  } = $props();

  let tabs = $state<any[]>([]);
  let activeTab = $state<any>(null);
  let activeComponentData = $state<any>(null);

  $effect(() => {
    const unsubTabs = pane.tabs.subscribe(t => tabs = t);
    const unsubActive = pane.activeTab.subscribe(at => {
      activeTab = at;
      updateActiveComponent();
    });

    return () => {
      unsubTabs();
      unsubActive();
    };
  });

  function updateActiveComponent() {
    if (!activeTab) {
      activeComponentData = null;
      return;
    }

    const state = activeTab.getState();
    const Component = PANE_COMPONENT_REGISTRY[state.componentType as keyof typeof PANE_COMPONENT_REGISTRY];

    activeComponentData = {
      component: Component,
      props: {
        paneComponent: activeTab.paneComponent,
        tabId: state.id,
      }
    };
  }

  function handleSwitchTab(tabId: string) {
    pane.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    pane.removeTab(tabId);
    oncloseTab?.(tabId);
  }
</script>

{#if tabs.length > 1}
  <div class="flex gap-1 bg-base-200 px-2 py-1">
    {#each tabs as tab (tab.getState().id)}
      <button
        class="btn btn-sm"
        class:btn-primary={tab.getState().isActive}
        onclick={() => handleSwitchTab(tab.getState().id)}
      >
        {tab.getState().title}
        {#if tab.getState().isCloseable}
          <span 
            role="button"
            tabindex="0"
            onclick={(e) => { e.stopPropagation(); handleCloseTab(tab.getState().id); }}
            onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.stopPropagation(); handleCloseTab(tab.getState().id); } }}
          >×</span>
        {/if}
      </button>
    {/each}
  </div>
{/if}

{#if activeComponentData}
  <div class="flex-1 overflow-hidden">
    <svelte:component
      this={activeComponentData.component}
      {...activeComponentData.props}
    />
  </div>
{:else}
  <div class="p-4 text-center text-base-content/50">No active tab</div>
{/if}
