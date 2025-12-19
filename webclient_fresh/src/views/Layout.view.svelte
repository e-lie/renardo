<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { useLayoutStore } from '../store/layout'
  import { edgeDetectionService } from '../services/layout/edgeDetection.service'
  import PaneContainer from '../components/layout/PaneContainer.component.svelte'
  import ElResizeHandle from '../components/primitives/layout/ElResizeHandle.svelte'
  import ElFloatingToggle from '../components/primitives/layout/ElFloatingToggle.svelte'
  import SettingsModal from '../components/shared/SettingsModal.component.svelte'

  const { getters, actions } = useLayoutStore()
  const {
    paneSetVisibility,
    hoverStates,
    paneSizes,
    containerSizes,
    hideAppNavbar
  } = getters

  let resizeData = $state<any>(null)
  let showSettings = $state(false)

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

  <!-- Floating Settings Button -->
  <button
    class="fixed top-4 right-4 btn btn-square variant-filled-primary shadow-lg z-50"
    onclick={() => showSettings = true}
    title="Settings"
  >
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  </button>

  <SettingsModal isOpen={showSettings} onclose={() => showSettings = false} />
</div>
