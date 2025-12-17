<script lang="ts">
  import ThemeSelector from '../editor/children/ThemeSelector.component.svelte';
  import LayoutSettings from '../layout/LayoutSettings.component.svelte';
  import type { LayoutManager } from '../../lib/layout/LayoutManager';

  let {
    isOpen = false,
    onclose,
    layoutManager,
  }: {
    isOpen?: boolean;
    onclose?: () => void;
    layoutManager?: LayoutManager;
  } = $props();

  let activeTab = $state<'theme' | 'layout'>('theme');

  function handleClose() {
    onclose?.();
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    onclick={handleBackdropClick}
    onkeydown={(e) => { if (e.key === 'Escape') handleClose(); }}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div class="bg-base-100 rounded-lg shadow-xl w-full max-w-2xl p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">Settings</h2>
        <button
          class="btn btn-sm btn-circle btn-ghost"
          onclick={handleClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <!-- Tabs -->
      <div class="tabs tabs-boxed mb-4">
        <button
          class="tab"
          class:tab-active={activeTab === 'theme'}
          onclick={() => activeTab = 'theme'}
        >
          Theme
        </button>
        <button
          class="tab"
          class:tab-active={activeTab === 'layout'}
          onclick={() => activeTab = 'layout'}
        >
          Layout
        </button>
      </div>

      <!-- Content -->
      <div class="space-y-4">
        {#if activeTab === 'theme'}
          <ThemeSelector />
        {:else if activeTab === 'layout' && layoutManager}
          <LayoutSettings {layoutManager} />
        {/if}
      </div>

      <!-- Footer -->
      <div class="mt-6 flex justify-end">
        <button class="btn btn-primary" onclick={handleClose}>
          Done
        </button>
      </div>
    </div>
  </div>
{/if}
