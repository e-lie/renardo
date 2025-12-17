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
    onsettings,
  }: {
    tabs: TabInterface[];
    buffers: BufferInterface[];
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
    oncreate?: () => void;
    onsettings?: () => void;
  } = $props();

  function handleCreateTab() {
    oncreate?.();
  }
</script>

<div class="bg-base-200 px-2 py-1">
  <div class="flex items-center gap-1">
    <!-- Tabs -->
    <div class="flex items-center gap-1 overflow-x-auto flex-1">
      {#each tabs as tab (tab.id)}
        <TabItem {tab} {onswitch} {onclose} />
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

    <!-- Settings Button -->
    <ElButton variant="ghost" onclick={() => onsettings?.()} testid="settings-button" aria-label="Settings">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
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
