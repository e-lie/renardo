<script lang="ts">
  import { onMount } from 'svelte'
  import { currentPage } from '../stores'

  export let sessionName: string = 'renardo-session'
  export let height: string = '100vh'
  export let width: string = '100%'

  let iframeElement: HTMLIFrameElement
  let loading = true
  let error = false

  $: flokUrl = `http://localhost:3002/s/${sessionName}`

  onMount(() => {
    // Listen for messages from flok iframe
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== 'http://localhost:3002') return

      console.log('Message from Flok:', event.data)

      // Handle different message types from flok
      switch (event.data.type) {
        case 'FLOK_READY':
          loading = false
          console.log('Flok editor is ready')
          break
        case 'FLOK_CODE_CHANGE':
          console.log('Code changed in flok:', event.data)
          // TODO: Save to backend or synchronize with blog posts
          break
        case 'FLOK_SESSION_JOIN':
          console.log('User joined session:', event.data)
          break
      }
    }

    window.addEventListener('message', handleMessage)

    // Handle iframe load events
    const handleLoad = () => {
      loading = false
      error = false
    }

    const handleError = () => {
      loading = false
      error = true
    }

    if (iframeElement) {
      iframeElement.addEventListener('load', handleLoad)
      iframeElement.addEventListener('error', handleError)
    }

    return () => {
      window.removeEventListener('message', handleMessage)
      if (iframeElement) {
        iframeElement.removeEventListener('load', handleLoad)
        iframeElement.removeEventListener('error', handleError)
      }
    }
  })

  function goBack() {
    currentPage.set('posts')
  }

  function sendMessageToFlok(message: any) {
    if (iframeElement && iframeElement.contentWindow) {
      iframeElement.contentWindow.postMessage(message, 'http://localhost:3002')
    }
  }

  // Example function to interact with flok
  function shareCode(code: string) {
    sendMessageToFlok({
      type: 'WEBCLIENT_CODE_SHARE',
      data: { code, timestamp: Date.now() }
    })
  }
</script>

<div class="flok-container h-full">
  <!-- Header with controls -->
  <div class="bg-base-200 p-4 flex justify-between items-center">
    <div class="flex items-center space-x-4">
      <button class="btn btn-ghost btn-sm" on:click={goBack}>
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Blog
      </button>

      <div class="divider divider-horizontal"></div>

      <h2 class="text-lg font-semibold">Collaborative Code Editor</h2>
      <div class="badge badge-primary">Session: {sessionName}</div>
    </div>

    <div class="flex items-center space-x-2">
      {#if loading}
        <span class="loading loading-spinner loading-sm"></span>
        <span class="text-sm">Loading editor...</span>
      {:else if error}
        <div class="badge badge-error">Connection Error</div>
      {:else}
        <div class="badge badge-success">Connected</div>
      {/if}
    </div>
  </div>

  <!-- Main iframe container -->
  <div class="relative" style="height: calc({height} - 80px); width: {width};">
    {#if loading}
      <div class="absolute inset-0 flex items-center justify-center bg-base-100">
        <div class="text-center">
          <span class="loading loading-spinner loading-lg"></span>
          <div class="mt-4">
            <h3 class="text-lg font-semibold">Starting Flok Editor</h3>
            <p class="text-base-content/60">Connecting to collaborative session...</p>
          </div>
        </div>
      </div>
    {/if}

    {#if error}
      <div class="absolute inset-0 flex items-center justify-center bg-base-100">
        <div class="text-center">
          <div class="alert alert-error max-w-md">
            <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 class="font-bold">Cannot connect to Flok</h3>
              <div class="text-xs">Make sure the Flok server is running on port 3002</div>
            </div>
          </div>
          <button class="btn btn-primary mt-4" on:click={() => window.location.reload()}>
            Retry Connection
          </button>
        </div>
      </div>
    {/if}

    <iframe
      bind:this={iframeElement}
      src={flokUrl}
      title="Flok Collaborative Editor"
      class="w-full h-full border-0"
      class:invisible={loading || error}
      allow="microphone; camera; midi; encrypted-media; autoplay"
      sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-modals"
    ></iframe>
  </div>
</div>

<style>
  .flok-container {
    background: var(--fallback-b1, oklch(var(--b1)));
  }

  iframe {
    border: none;
    outline: none;
  }
</style>