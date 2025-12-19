<script lang="ts">
  let {
    componentId,
    title = 'Color Picker'
  }: {
    componentId: string
    title?: string
  } = $props()
</script>

<div class="h-full flex items-center justify-center p-4">
  <div class="text-center">
    <div class="text-4xl mb-2">🎨</div>
    <p class="text-sm text-surface-600 dark:text-surface-400">{title}</p>
    <p class="text-xs text-surface-500 dark:text-surface-500 mt-1">{componentId}</p>
  </div>
</div>
