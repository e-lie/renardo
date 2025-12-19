<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    isActive = false,
    isPinned = false,
    isStartupFile = false,
    closeable = true,
    testid = 'not-set',
    onclick,
    onclose,
    children,
  }: {
    isActive?: boolean;
    isPinned?: boolean;
    isStartupFile?: boolean;
    closeable?: boolean;
    testid?: string;
    onclick?: () => void;
    onclose?: () => void;
    children?: Snippet;
  } = $props();

  const cssClass = $derived.by(() => {
    const baseClasses = ['flex items-center gap-2 px-4 py-2 text-sm whitespace-nowrap'];

    if (isActive) baseClasses.push('border-b-2 border-primary-500 bg-surface-200 dark:bg-surface-700');
    if (isStartupFile) baseClasses.push('font-bold text-primary-500');

    return baseClasses.join(' ');
  });

  function handleClose(e: MouseEvent) {
    e.stopPropagation();
    onclose?.();
  }
</script>

<button data-testid={testid} class={cssClass} {onclick} type="button">
  {#if isStartupFile}
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-4 w-4"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        fill-rule="evenodd"
        d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
        clip-rule="evenodd"
      />
    </svg>
  {/if}

  {#if children}
    {@render children()}
  {/if}

  {#if closeable && !isStartupFile}
    <button
      class="ml-2 w-4 h-4 rounded-full hover:bg-surface-300 dark:hover:bg-surface-600 flex items-center justify-center text-xs"
      onclick={handleClose}
      type="button"
    >
      ×
    </button>
  {/if}
</button>
