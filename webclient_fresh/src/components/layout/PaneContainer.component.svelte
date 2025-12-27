<script lang="ts">
  import type { PanePosition } from '../../models/layout'
  import TabbedPane from './children/TabbedPane.component.svelte'
  import CodeEditorWrapper from './children/CodeEditorWrapper.component.svelte'
  import TopMenu from './children/TopMenu.component.svelte'

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
    if (position === 'top-menu') {
      return 'bg-surface-200 dark:bg-surface-800'
    }
    return 'bg-surface-100 dark:bg-surface-900'
  })

  const cssClass = $derived(
    `h-full ${bgColor} border border-surface-300 dark:border-surface-700 overflow-hidden`
  )
</script>

<div class={cssClass} {style}>
  {#if position === 'center'}
    <CodeEditorWrapper />
  {:else if position === 'top-menu'}
    <TopMenu />
  {:else}
    <TabbedPane {position} />
  {/if}
</div>
