<script lang="ts">
  import { useConsoleStore } from '../../store/console/Console.store'
  import type { ConsoleMessageInterface } from '../../models/console'

  const { getters } = useConsoleStore()
  const { messages } = getters

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
</script>

<div class="card h-full bg-neutral-950">
  <div class="overflow-y-auto h-full p-4 font-mono text-sm" bind:this={consoleContainer}>
    {#if $messages.length === 0}
      <div class="flex items-center justify-center h-full opacity-50 italic text-neutral-400">
        No output yet. Run some code to see results here.
      </div>
    {:else}
      {#each $messages as output}
        {#if formatMessage(output.message) !== ''}
          <div class="mb-2">
            <span class="{getMessageClass(output.level)} whitespace-pre-wrap">{formatMessage(output.message)}</span>
          </div>
        {/if}
      {/each}
    {/if}
  </div>
</div>
