<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { useLayoutStore } from '../store/layout'
  import { edgeDetectionService } from '../services/layout/edgeDetection.service'
  import PaneContainer from '../components/layout/PaneContainer.component.svelte'
  import ElResizeHandle from '../components/primitives/layout/ElResizeHandle.svelte'
  import ElFloatingToggle from '../components/primitives/layout/ElFloatingToggle.svelte'

  const { getters, actions } = useLayoutStore()
  const {
    paneSetVisibility,
    hoverStates,
    paneSizes,
    containerSizes,
    hideAppNavbar
  } = getters

  let resizeData = $state<any>(null)

  onMount(() => {
    document.addEventListener('mousemove', handleGlobalMouseMove)
  })

  onDestroy(() => {
    document.removeEventListener('mousemove', handleGlobalMouseMove)
  })

  function startResize(event: MouseEvent, paneId: string, direction: 'horizontal' | 'vertical') {
    event.preventDefault()
    actions.startResize()

    const startPos = direction === 'horizontal' ? event.clientX : event.clientY
    const startSize = $paneSizes[paneId as keyof typeof $paneSizes]

    resizeData = { paneId, direction, startPos, startSize }
    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', endResize)
  }

  function startContainerResize(
    event: MouseEvent,
    containerId: string,
    direction: 'horizontal' | 'vertical'
  ) {
    event.preventDefault()
    actions.startResize()

    const startPos = direction === 'horizontal' ? event.clientX : event.clientY
    const startSize = $containerSizes[containerId as keyof typeof $containerSizes]

    resizeData = { containerId, direction, startPos, startSize, isContainer: true }
    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', endResize)
  }

  function handleResize(event: MouseEvent) {
    if (!resizeData) return

    const currentPos = resizeData.direction === 'horizontal' ? event.clientX : event.clientY
    let delta = currentPos - resizeData.startPos

    // Invert delta for right/bottom
    if (resizeData.containerId === 'right-column' || resizeData.containerId === 'bottom-area') {
      delta = -delta
    }

    const newSize = Math.max(100, resizeData.startSize + delta)

    if (resizeData.isContainer) {
      actions.updateContainerSize(resizeData.containerId, newSize)
    } else {
      actions.updatePaneSize(resizeData.paneId, newSize)
    }
  }

  function endResize() {
    actions.endResize()
    resizeData = null
    document.removeEventListener('mousemove', handleResize)
    document.removeEventListener('mouseup', endResize)
  }

  function handleGlobalMouseMove(event: MouseEvent) {
    const edge = edgeDetectionService.detectEdge(event.clientX, event.clientY)

    if (edge && !$paneSetVisibility[edge] && getters.hasPanesVisible(edge)) {
      actions.setPaneSetHover(edge, true)
    } else {
      // Clear hover states
      ;['left', 'right', 'bottom'].forEach(setName => {
        if (!$paneSetVisibility[setName as 'left' | 'right' | 'bottom']) {
          const nearButton = edgeDetectionService.isNearButtonArea(
            setName as 'left' | 'right' | 'bottom',
            event.clientX,
            event.clientY
          )
          if (!nearButton) {
            actions.setPaneSetHover(setName, false)
          }
        }
      })
    }
  }
</script>

<div class="h-screen flex flex-col overflow-hidden bg-surface-100 dark:bg-surface-900">
  <!-- Top menu -->
  <div class="h-16 flex-shrink-0">
    <PaneContainer position="top-menu" height={64} />
  </div>

  <!-- Main area -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left column -->
    {#if $paneSetVisibility.left}
      <div class="flex flex-col" style="width: {$containerSizes['left-column']}px; min-width: 200px;">
        <PaneContainer position="left-top" height={$paneSizes['left-top']} minHeight={100} />

        <ElResizeHandle
          direction="vertical"
          onresizestart={(e) => startResize(e, 'left-top', 'vertical')}
        />

        <PaneContainer position="left-middle" height={$paneSizes['left-middle']} minHeight={100} />

        <ElResizeHandle
          direction="vertical"
          onresizestart={(e) => startResize(e, 'left-middle', 'vertical')}
        />

        <div class="flex-1 min-h-[100px]">
          <PaneContainer position="left-bottom" />
        </div>
      </div>

      <ElResizeHandle
        direction="horizontal"
        onresizestart={(e) => startContainerResize(e, 'left-column', 'horizontal')}
      />
    {/if}

    <!-- Center -->
    <div class="flex flex-col flex-1">
      <div class="flex-1">
        <PaneContainer position="center" />
      </div>

      <!-- Bottom area -->
      {#if $paneSetVisibility.bottom}
        <ElResizeHandle
          direction="vertical"
          onresizestart={(e) => startContainerResize(e, 'bottom-area', 'vertical')}
        />

        <div class="flex" style="height: {$containerSizes['bottom-area']}px; min-height: 150px;">
          <div style="width: {$paneSizes['bottom-left']}px; min-width: 200px;">
            <PaneContainer position="bottom-left" />
          </div>

          <ElResizeHandle
            direction="horizontal"
            onresizestart={(e) => startResize(e, 'bottom-left', 'horizontal')}
          />

          <div class="flex-1">
            <PaneContainer position="bottom-right" />
          </div>
        </div>
      {/if}
    </div>

    <!-- Right column -->
    {#if $paneSetVisibility.right}
      <ElResizeHandle
        direction="horizontal"
        onresizestart={(e) => startContainerResize(e, 'right-column', 'horizontal')}
      />

      <div class="flex flex-col" style="width: {$containerSizes['right-column']}px; min-width: 200px;">
        <PaneContainer position="right-top" height={$paneSizes['right-top']} minHeight={100} />

        <ElResizeHandle
          direction="vertical"
          onresizestart={(e) => startResize(e, 'right-top', 'vertical')}
        />

        <PaneContainer position="right-middle" height={$paneSizes['right-middle']} minHeight={100} />

        <ElResizeHandle
          direction="vertical"
          onresizestart={(e) => startResize(e, 'right-middle', 'vertical')}
        />

        <div class="flex-1 min-h-[100px]">
          <PaneContainer position="right-bottom" />
        </div>
      </div>
    {/if}
  </div>

  <!-- Floating toggle buttons -->
  {#if $hoverStates.left && getters.hasPanesVisible('left')}
    <ElFloatingToggle
      position="left"
      onclick={() => actions.togglePaneSet('left')}
      onmouseenter={() => actions.setPaneSetHover('left', true)}
      onmouseleave={() => actions.setPaneSetHover('left', false)}
      title={$paneSetVisibility.left ? 'Hide left panes' : 'Show left panes'}
    >
      {#if $paneSetVisibility.left}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      {/if}
    </ElFloatingToggle>
  {/if}

  {#if $hoverStates.right && getters.hasPanesVisible('right')}
    <ElFloatingToggle
      position="right"
      onclick={() => actions.togglePaneSet('right')}
      onmouseenter={() => actions.setPaneSetHover('right', true)}
      onmouseleave={() => actions.setPaneSetHover('right', false)}
      title={$paneSetVisibility.right ? 'Hide right panes' : 'Show right panes'}
    >
      {#if $paneSetVisibility.right}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      {/if}
    </ElFloatingToggle>
  {/if}

  {#if $hoverStates.bottom && getters.hasPanesVisible('bottom')}
    <ElFloatingToggle
      position="bottom"
      onclick={() => actions.togglePaneSet('bottom')}
      onmouseenter={() => actions.setPaneSetHover('bottom', true)}
      onmouseleave={() => actions.setPaneSetHover('bottom', false)}
      title={$paneSetVisibility.bottom ? 'Hide bottom panes' : 'Show bottom panes'}
    >
      {#if $paneSetVisibility.bottom}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
        </svg>
      {/if}
    </ElFloatingToggle>
  {/if}
</div>
