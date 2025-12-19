<script lang="ts">
  let {
    componentId,
    title = 'Text Area'
  }: {
    componentId: string
    title?: string
  } = $props()

  let content = $state('')
</script>

<div class="h-full flex flex-col p-2">
  <textarea
    class="w-full h-full bg-surface-50 dark:bg-surface-900 border border-surface-300 dark:border-surface-700 rounded p-2 text-sm text-surface-900 dark:text-surface-50 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
    placeholder="Enter text here..."
    bind:value={content}
  ></textarea>
</div>
