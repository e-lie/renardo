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

  interface FormattedOutput {
    type: 'code' | 'result' | 'error' | 'empty'
    content: string
  }

  function formatMessage(message: string): FormattedOutput {
    // Remove runtime prefixes from WebSocket messages
    if (message.startsWith('[runtime] ')) {
      const content = message.substring(10) // Remove '[runtime] '

      // Handle code execution
      if (content.startsWith('Executing code: ')) {
        const code = content.substring(16)
        return { type: 'code', content: code }
      }

      // Handle execution result
      if (content.startsWith('Execution result: ')) {
        const result = content.substring(18)
        return { type: 'result', content: result }
      }

      // Handle execution error
      if (content.startsWith('Execution error: ')) {
        const error = content.substring(17)
        return { type: 'error', content: error }
      }

      return { type: 'result', content }
    }

    return { type: 'result', content: message }
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
        {@const formatted = formatMessage(output.message)}
        {#if formatted.type !== 'empty'}
          <div class="mb-2">
            {#if formatted.type === 'code'}
              <div class="text-primary-400">
                <span class="opacity-50">>>> </span><span class="whitespace-pre-wrap">{formatted.content}</span>
              </div>
            {:else if formatted.type === 'error'}
              <div class="text-error font-bold whitespace-pre-wrap ml-4">{formatted.content}</div>
            {:else}
              <div class="text-success-400 whitespace-pre-wrap ml-4">{formatted.content}</div>
            {/if}
          </div>
        {/if}
      {/each}
    {/if}
  </div>
</div>
