<script lang="ts">
  import { useConsoleStore } from '../../store/console/Console.store'
  import type { ConsoleMessageInterface } from '../../models/console'

  const { getters, actions } = useConsoleStore()
  const { messages, isMinimized } = getters

  let consoleContainer: HTMLDivElement

  function scrollToBottom() {
    if (consoleContainer) {
      setTimeout(() => {
        consoleContainer.scrollTop = consoleContainer.scrollHeight
      }, 50)
    }
  }

  $effect(() => {
    if ($messages.length > 0) {
      scrollToBottom()
    }
  })

  function handleClear() {
    actions.clearMessages()
  }

  function handleToggleMinimize() {
    actions.toggleMinimize()
  }

  function getMessageClass(level: string): string {
    switch (level.toLowerCase()) {
      case 'info':
        return 'text-info'
      case 'command':
        return 'text-accent font-bold'
      case 'error':
        return 'text-error font-bold'
      case 'success':
        return 'text-success'
      case 'warn':
        return 'text-warning'
      default:
        return ''
    }
  }

  function formatMessage(message: string): string {
    // Remove runtime prefixes from WebSocket messages
    if (message.startsWith('[runtime] ')) {
      const content = message.substring(10) // Remove '[runtime] '
      
      // Remove execution and result prefixes
      if (content.startsWith('Executing code: ')) {
        return '' // Hide execution messages entirely
      }
      if (content.startsWith('Execution result: ')) {
        return content.substring(18) // Show only the result
      }
      if (content.startsWith('Execution error: ')) {
        return content.substring(17) // Show only the error message
      }
      
      return content
    }
    
    return message
  }

  const displayedMessages = $derived($isMinimized ? $messages.slice(-2) : $messages)
</script>

<div class="flex flex-col h-full bg-surface-900 dark:bg-surface-950 text-surface-50">
  <!-- Console header -->
  <div class="flex justify-between items-center px-4 py-2 bg-surface-800 dark:bg-surface-900 border-b border-surface-700">
    <h3 class="text-sm font-bold">ฅ^•ﻌ•^ฅ >> output</h3>
    <div class="flex gap-2">
      <button
        class="btn btn-sm btn-icon variant-ghost"
        onclick={handleToggleMinimize}
        title={$isMinimized ? 'Expand Console' : 'Minimize Console'}
      >
        {#if $isMinimized}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        {/if}
      </button>
      <button
        class="btn btn-sm btn-icon variant-ghost"
        onclick={handleClear}
        title="Clear Console"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Console content -->
  {#if !$isMinimized || $messages.length > 0}
    <div class="overflow-y-auto flex-1 p-4 font-mono text-sm" bind:this={consoleContainer}>
      {#if $messages.length === 0}
        <div class="flex items-center justify-center h-full opacity-50 italic">
          {$isMinimized ? '' : 'No output yet. Run some code to see results here.'}
        </div>
      {:else}
        {#each displayedMessages as output}
          {#if formatMessage(output.message) !== ''}
            <div class="mb-1 border-b border-surface-700 border-opacity-20 pb-1">
              <span class="{getMessageClass(output.level)} whitespace-pre-wrap">{formatMessage(output.message)}</span>
            </div>
          {/if}
        {/each}
      {/if}
    </div>
  {/if}
</div>
