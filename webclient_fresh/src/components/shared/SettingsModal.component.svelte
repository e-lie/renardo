<script lang="ts">
  import ThemeSelector from '../editor/children/ThemeSelector.component.svelte';
  import SkeletonThemeSelector from '../editor/children/SkeletonThemeSelector.component.svelte';
  import LineNumbersToggle from '../editor/children/LineNumbersToggle.component.svelte';
  import VimModeToggle from '../editor/children/VimModeToggle.component.svelte';
  import FontFamilySelector from '../editor/children/FontFamilySelector.component.svelte';
  import LayoutConfigTab from './LayoutConfigTab.component.svelte';
  import LanguageSelector from './LanguageSelector.component.svelte';
  import { useI18nStore } from '../../store/i18n/I18n.store';

  const { getters } = useI18nStore();
  const { translate } = getters;

  let {
    isOpen = false,
    onclose,
  }: {
    isOpen?: boolean;
    onclose?: () => void;
  } = $props();

  let activeTab = $state<'editor' | 'layout'>('editor')

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
    <div class="card variant-glass-surface w-full max-w-4xl p-6 space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">{$translate('settings')}</h2>
        <button
          class="btn variant-ghost w-8 h-8 p-0 rounded-full"
          onclick={handleClose}
          aria-label={$translate('close')}
        >
          ✕
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 border-b border-surface-300 dark:border-surface-700">
        <button
          class="px-4 py-2 text-sm transition-colors {activeTab === 'editor' ? 'border-b-2 border-primary-500 text-primary-500' : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-50'}"
          onclick={() => activeTab = 'editor'}
        >
          {$translate('editor')}
        </button>
        <button
          class="px-4 py-2 text-sm transition-colors {activeTab === 'layout' ? 'border-b-2 border-primary-500 text-primary-500' : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-50'}"
          onclick={() => activeTab = 'layout'}
        >
          {$translate('layout')}
        </button>
      </div>

      <!-- Content -->
      <div class="space-y-6 max-h-[60vh] overflow-y-auto">
        {#if activeTab === 'editor'}
          <LanguageSelector />
          <ThemeSelector />
          <SkeletonThemeSelector />
          <FontFamilySelector />
          <LineNumbersToggle />
          <VimModeToggle />
        {:else if activeTab === 'layout'}
          <LayoutConfigTab />
        {/if}
      </div>

      <!-- Footer -->
      <div class="flex justify-end">
        <button class="btn variant-filled-primary" onclick={handleClose}>
          {$translate('done')}
        </button>
      </div>
    </div>
  </div>
{/if}
