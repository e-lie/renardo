<script lang="ts">
  import ThemeSelector from '../editor/children/ThemeSelector.component.svelte';
  import SkeletonThemeSelector from '../editor/children/SkeletonThemeSelector.component.svelte';

  let {
    isOpen = false,
    onclose,
  }: {
    isOpen?: boolean;
    onclose?: () => void;
  } = $props();

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
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card variant-glass-surface w-full max-w-md p-6 space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">Settings</h2>
        <button
          class="btn variant-ghost w-8 h-8 p-0 rounded-full"
          onclick={handleClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="space-y-6">
        <ThemeSelector />
        <SkeletonThemeSelector />
      </div>

      <!-- Footer -->
      <div class="flex justify-end">
        <button class="btn variant-filled-primary" onclick={handleClose}>
          Done
        </button>
      </div>
    </div>
  </div>
{/if}
