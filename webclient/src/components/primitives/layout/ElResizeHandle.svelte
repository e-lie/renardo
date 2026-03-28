<script lang="ts">
  let {
    direction = 'horizontal',
    onresizestart,
    testid = 'resize-handle'
  }: {
    direction?: 'horizontal' | 'vertical'
    onresizestart?: (event: MouseEvent) => void
    testid?: string
  } = $props()

  const cursorClass = $derived(
    direction === 'horizontal' ? 'cursor-col-resize' : 'cursor-row-resize'
  )

  const sizeClass = $derived(
    direction === 'horizontal' ? 'w-1' : 'h-1'
  )

  const cssClass = $derived(
    `${sizeClass} bg-surface-100 dark:bg-surface-900 ${cursorClass} hover:bg-primary-500 transition-colors flex-shrink-0`
  )
</script>

<div
  data-testid={testid}
  class={cssClass}
  onmousedown={onresizestart}
  role="separator"
></div>
