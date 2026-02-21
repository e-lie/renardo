<script lang="ts">
  import { useI18nStore } from '../../store/i18n/I18n.store'
  import { useInitializationStore } from '../../store/initialization/Initialization.store'

  let {
    isOpen = false,
    onclose
  }: {
    isOpen?: boolean
    onclose?: () => void
  } = $props()

  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  const { actions, getters } = useInitializationStore()
  const {
    samplesInitialized,
    sccodeInitialized,
    downloading,
    downloadComplete,
    downloadError,
    initLogs
  } = getters

  let logsContainer = $state<HTMLDivElement | null>(null)

  // Auto-scroll logs to bottom
  $effect(() => {
    if ($initLogs.length > 0 && logsContainer) {
      logsContainer.scrollTop = logsContainer.scrollHeight
    }
  })

  async function handleDownload() {
    await actions.downloadMissing(!$samplesInitialized, !$sccodeInitialized)
  }

  function handleClose() {
    onclose?.()
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget && !$downloading) {
      handleClose()
    }
  }

  function getLogColor(level: string): string {
    if (level === 'error') return 'text-error-500'
    if (level === 'warn' || level === 'warning') return 'text-warning-500'
    return 'text-surface-600 dark:text-surface-300'
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card bg-surface-100 dark:bg-surface-800 w-full max-w-xl p-6 space-y-5">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">
          {#if $downloadComplete}
            {$translate('initDownloadCompleteTitle')}
          {:else if $downloadError}
            {$translate('initDownloadErrorTitle')}
          {:else if $downloading}
            {$translate('initDownloadingTitle')}
          {:else}
            {$translate('initResourcesTitle')}
          {/if}
        </h2>
        {#if !$downloading}
          <button
            class="btn variant-ghost w-8 h-8 p-0 rounded-full"
            onclick={handleClose}
            aria-label="Close"
          >
            ✕
          </button>
        {/if}
      </div>

      <!-- Description (initial state only) -->
      {#if !$downloading && !$downloadComplete && !$downloadError}
        <p class="opacity-70 text-sm">{$translate('initResourcesDescription')}</p>

        <!-- Resource checklist -->
        <ul class="space-y-2">
          <li class="flex items-center gap-3 text-sm">
            {#if $samplesInitialized}
              <span class="text-success-500">✔</span>
            {:else}
              <span class="text-error-500">✗</span>
            {/if}
            <span class:opacity-40={$samplesInitialized}>{$translate('initSamplesLabel')}</span>
          </li>
          <li class="flex items-center gap-3 text-sm">
            {#if $sccodeInitialized}
              <span class="text-success-500">✔</span>
            {:else}
              <span class="text-error-500">✗</span>
            {/if}
            <span class:opacity-40={$sccodeInitialized}>{$translate('initSccodeLabel')}</span>
          </li>
        </ul>
      {/if}

      <!-- Download complete message -->
      {#if $downloadComplete && !$downloadError}
        <div class="alert variant-filled-success text-sm">
          ✔ {$translate('initDownloadCompleteTitle')}
        </div>
      {/if}

      <!-- Download error message -->
      {#if $downloadError}
        <div class="alert variant-filled-error text-sm">
          {$downloadError}
        </div>
      {/if}

      <!-- Logs (visible during and after download) -->
      {#if $downloading || $downloadComplete || $downloadError}
        <div class="space-y-1">
          <p class="text-xs opacity-60">{$translate('initDownloadLogs')}</p>
          <div
            bind:this={logsContainer}
            class="bg-surface-200 dark:bg-surface-900 rounded-lg p-3 h-48 overflow-y-auto font-mono text-xs space-y-0.5"
          >
            {#if $initLogs.length === 0}
              <div class="opacity-40 italic">...</div>
            {:else}
              {#each $initLogs as log}
                <div class={getLogColor(log.level)}>
                  {log.message}
                </div>
              {/each}
            {/if}
            {#if $downloading}
              <div class="opacity-50 animate-pulse">▌</div>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-1">
        {#if $downloadComplete || $downloadError}
          <button class="btn variant-filled-primary" onclick={handleClose}>
            {$translate('close')}
          </button>
        {:else if $downloading}
          <div class="flex items-center gap-2 text-sm opacity-60">
            <span class="animate-spin">⏳</span>
            {$translate('initDownloadingTitle')}
          </div>
        {:else}
          <button
            class="btn variant-ghost"
            onclick={handleClose}
          >
            {$translate('initSkipButton')}
          </button>
          <button
            class="btn variant-filled-primary"
            onclick={handleDownload}
            disabled={$samplesInitialized && $sccodeInitialized}
          >
            {$translate('initDownloadButton')}
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}
