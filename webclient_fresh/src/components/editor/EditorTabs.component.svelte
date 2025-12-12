<script lang="ts">
  import type { TabInterface, BufferInterface } from '../../models/editor';
  import TabItem from './children/TabItem.component.svelte';
  import { ElButton } from '../primitives';

  let {
    tabs,
    buffers,
    onswitch,
    onclose,
    oncreate,
  }: {
    tabs: TabInterface[];
    buffers: BufferInterface[];
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
    oncreate?: () => void;
  } = $props();

  function handleCreateTab() {
    oncreate?.();
  }

  function isStartupFile(tab: TabInterface): boolean {
    const buffer = buffers.find((b) => b.id === tab.bufferId);
    return buffer?.isStartupFile || false;
  }
</script>

<div class="bg-base-200 px-2 py-1">
  <div class="flex items-center gap-1">
    <!-- Tabs -->
    <div class="flex items-center gap-1 overflow-x-auto flex-1">
      {#each tabs as tab (tab.id)}
        <TabItem {tab} isStartupFile={isStartupFile(tab)} {onswitch} {onclose} />
      {/each}
    </div>

    <!-- New Tab Button -->
    <ElButton variant="ghost" onclick={handleCreateTab} testid="new-tab-button">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
          clip-rule="evenodd"
        />
      </svg>
    </ElButton>
  </div>
</div>

<style>
  /* Hide scrollbar but keep functionality */
  .overflow-x-auto {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .overflow-x-auto::-webkit-scrollbar {
    display: none;
  }
</style>
