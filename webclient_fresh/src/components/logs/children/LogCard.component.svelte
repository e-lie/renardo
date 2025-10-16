<script lang="ts">
  import type { LogEntryInterface } from '../../../models/logs'
  import ElCard from '../../primitives/cards/ElCard.svelte'
  import ElText from '../../primitives/text/ElText.svelte'

  let {
    log
  }: {
    log: LogEntryInterface
  } = $props()

  // Format timestamp to readable format
  const formattedTime = $derived.by(() => {
    const date = new Date(log.timestamp)
    return date.toLocaleString()
  })

  // Determine color based on log level
  const levelColor = $derived.by(() => {
    switch (log.level) {
      case 'DEBUG':
        return 'text-gray-500'
      case 'INFO':
        return 'text-blue-500'
      case 'WARNING':
        return 'text-yellow-500'
      case 'ERROR':
        return 'text-red-500'
      case 'CRITICAL':
        return 'text-red-700 font-bold'
      default:
        return 'text-gray-700'
    }
  })

  // Determine badge style based on log level
  const badgeClass = $derived.by(() => {
    const base = 'badge badge-sm'
    switch (log.level) {
      case 'DEBUG':
        return `${base} badge-ghost`
      case 'INFO':
        return `${base} badge-info`
      case 'WARNING':
        return `${base} badge-warning`
      case 'ERROR':
        return `${base} badge-error`
      case 'CRITICAL':
        return `${base} badge-error badge-lg`
      default:
        return base
    }
  })

  // Determine source badge color
  const sourceClass = $derived.by(() => {
    if (log.source === 'subprocess') {
      return 'badge badge-sm badge-secondary'
    }
    return 'badge badge-sm badge-primary'
  })
</script>

<ElCard testid={`log-card-${log.id}`} addCss="mb-2">
  <div class="flex flex-col gap-2">
    <!-- Header: Time, Level, Source -->
    <div class="flex items-center gap-2 text-xs">
      <ElText
        tag="span"
        text={formattedTime}
        addCss="text-gray-500 font-mono"
      />
      <span class={badgeClass}>{log.level}</span>
      <span class={sourceClass}>{log.source}</span>
      <ElText
        tag="span"
        text={log.logger}
        addCss="text-gray-400 text-xs font-mono"
      />
    </div>

    <!-- Message -->
    <div class="font-mono text-sm">
      <ElText
        tag="pre"
        text={log.message}
        addCss={`${levelColor} whitespace-pre-wrap break-words`}
      />
    </div>

    <!-- Extra info if available -->
    {#if log.extra}
      <details class="text-xs">
        <summary class="cursor-pointer text-gray-500 hover:text-gray-700">
          Extra info
        </summary>
        <pre class="mt-2 p-2 bg-base-200 rounded text-gray-600 overflow-x-auto">{log.extra}</pre>
      </details>
    {/if}
  </div>
</ElCard>
