<script lang="ts">
  import ThemeSelector from '../editor/children/ThemeSelector.component.svelte';

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
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="bg-base-100 rounded-lg shadow-xl w-full max-w-md p-6">
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

      <!-- Content -->
      <div class="space-y-4">
        <ThemeSelector />
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
