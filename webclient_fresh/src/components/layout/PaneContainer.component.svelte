<script lang="ts">
  import type { PanePosition } from '../../models/layout'
  import TabbedPane from './children/TabbedPane.component.svelte'

  let {
    position,
    width,
    height,
    minWidth,
    minHeight
  }: {
    position: PanePosition
    width?: number
    height?: number
    minWidth?: number
    minHeight?: number
  } = $props()

  const style = $derived.by(() => {
    let s = ''
    if (width) s += `width: ${width}px; `
    if (height) s += `height: ${height}px; `
    if (minWidth) s += `min-width: ${minWidth}px; `
    if (minHeight) s += `min-height: ${minHeight}px; `
    return s
  })

  const bgColor = $derived.by(() => {
    const colors = {
      'top-menu': 'bg-surface-200 dark:bg-surface-800',
      'left-top': 'bg-primary-500/10 dark:bg-primary-500/20',
      'left-middle': 'bg-primary-500/20 dark:bg-primary-500/30',
      'left-bottom': 'bg-secondary-500/10 dark:bg-secondary-500/20',
      'right-top': 'bg-tertiary-500/10 dark:bg-tertiary-500/20',
      'right-middle': 'bg-tertiary-500/20 dark:bg-tertiary-500/30',
      'right-bottom': 'bg-success-500/10 dark:bg-success-500/20',
      'bottom-left': 'bg-warning-500/10 dark:bg-warning-500/20',
      'bottom-right': 'bg-error-500/10 dark:bg-error-500/20',
      'center': 'bg-surface-100 dark:bg-surface-900'
    }
    return colors[position] || 'bg-surface-100 dark:bg-surface-900'
  })

  const cssClass = $derived(
    `${bgColor} border border-surface-300 dark:border-surface-700 overflow-hidden`
  )
</script>

<div class={cssClass} {style}>
  <TabbedPane {position} />
</div>
