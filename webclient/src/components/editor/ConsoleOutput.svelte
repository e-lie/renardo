<script>
  import { onMount, afterUpdate, createEventDispatcher } from 'svelte';
  
  export let consoleOutput = [];
  export let consoleHeight = 30;
  export let isVerticalResizing = false;
  export let consoleMinimized = false;
  export let theme = 'dracula';
  
  const dispatch = createEventDispatcher();
  
  let consoleContainer;
  let consoleHeightBeforeMinimize = 30;
  let minimizedConsoleHeight = 15;
  
  // Calculate console colors based on theme
  $: consoleColors = getConsoleColorsForTheme(theme);
  
  // Function to get console colors for a given theme
  function getConsoleColorsForTheme(theme) {
    let consoleBg = "#21222c";
    let consoleHeaderBg = "#191a21";
    let textColor = "#f8f8f2";
    
    switch(theme) {
      case "dracula":
        consoleBg = "#21222c";
        consoleHeaderBg = "#191a21";
        textColor = "#f8f8f2";
        break;
      case "monokai":
        consoleBg = "#272822";
        consoleHeaderBg = "#1e1f1c";
        textColor = "#f8f8f2";
        break;
      case "material":
        consoleBg = "#263238";
        consoleHeaderBg = "#1c262b";
        textColor = "#eeffff";
        break;
      case "nord":
        consoleBg = "#2e3440";
        consoleHeaderBg = "#272c36";
        textColor = "#d8dee9";
        break;
      case "solarized-dark":
        consoleBg = "#002b36";
        consoleHeaderBg = "#00212b";
        textColor = "#839496";
        break;
      case "solarized-light":
        consoleBg = "#fdf6e3";
        consoleHeaderBg = "#eee8d5";
        textColor = "#657b83";
        break;
      case "darcula":
        consoleBg = "#2b2b2b";
        consoleHeaderBg = "#1e1e1e";
        textColor = "#a9b7c6";
        break;
      case "eclipse":
        consoleBg = "#f7f7f7";
        consoleHeaderBg = "#e7e7e7";
        textColor = "#333";
        break;
      default:
        // Use default dark theme colors
        break;
    }
    
    return { 
      consoleBg, 
      consoleHeaderBg, 
      textColor 
    };
  }
  
  // Function to scroll console to bottom
  function scrollToBottom() {
    if (consoleContainer) {
      setTimeout(() => {
        consoleContainer.scrollTop = consoleContainer.scrollHeight;
      }, 50);
    }
  }
  
  // Scroll when content updates
  afterUpdate(() => {
    if (consoleOutput.length > 0) {
      scrollToBottom();
    }
  });
  
  function clearConsole() {
    dispatch('clear');
  }
  
  function toggleMinimize() {
    if (consoleMinimized) {
      // Expanding: restore previous height
      consoleHeight = consoleHeightBeforeMinimize;
      consoleMinimized = false;
    } else {
      // Minimizing: store current height and set to minimized height
      consoleHeightBeforeMinimize = consoleHeight;
      consoleHeight = minimizedConsoleHeight;
      consoleMinimized = true;
    }
    dispatch('toggleMinimize', { minimized: consoleMinimized, height: consoleHeight });
  }
  
  function startResize(e) {
    e.preventDefault();
    dispatch('startResize');
  }
</script>

<!-- Console output with variable height -->
<div 
  class="flex flex-col border-t border-base-300 transition-all console-background"
  style="height: {consoleHeight}%; background-color: {consoleColors.consoleBg}; color: {consoleColors.textColor};"
>
  <!-- Vertical resize handle -->
  <div 
    class="h-1 hover:h-1 cursor-row-resize flex-shrink-0 bg-base-300 hover:bg-primary hover:opacity-50 transition-colors"
    on:mousedown={startResize}
  ></div>
  
  <!-- Console header -->
  <div 
    class="flex justify-between items-center px-4 py-1 console-header"
    style="background-color: {consoleColors.consoleHeaderBg};"
  >
    <h3 class="text-sm font-semibold">Console Output</h3>
    <div class="flex gap-2">
      <button
        class="btn btn-xs btn-ghost"
        on:click={toggleMinimize}
        title="{consoleMinimized ? 'Expand' : 'Minimize'} Console"
      >
        {#if consoleMinimized}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        {/if}
      </button>
      <button
        class="btn btn-xs btn-ghost"
        on:click={clearConsole}
        title="Clear Console"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
  
  {#if !consoleMinimized || consoleOutput.length > 0}
    <div class="overflow-y-auto flex-1 p-4 font-mono text-sm" bind:this={consoleContainer}>
      {#if consoleOutput.length === 0}
        <div class="flex items-center justify-center h-full opacity-50 italic">
          {consoleMinimized ? '' : 'No output yet. Run some code to see results here.'}
        </div>
      {:else}
        {#each (consoleMinimized ? consoleOutput.slice(-2) : consoleOutput) as output}
          <div class="mb-1 border-b border-base-300 border-opacity-20 pb-1">
            <span class="{
              output.level.toLowerCase() === 'info' ? 'text-info' :
              output.level.toLowerCase() === 'command' ? 'text-accent font-bold' :
              output.level.toLowerCase() === 'error' ? 'text-error font-bold' :
              output.level.toLowerCase() === 'success' ? 'text-success' :
              output.level.toLowerCase() === 'warn' ? 'text-warning' : ''
            } whitespace-pre-wrap">{output.message}</span>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</div>

<style>
  /* Console styling */
  .console-background {
    /* These will be overridden by inline styles */
    background-color: #21222c; /* Default - matches Dracula darker */
    color: #f8f8f2; /* Light text for dark backgrounds */
  }
  
  .console-header {
    /* These will be overridden by inline styles */
    background-color: #191a21; /* Default - matches Dracula darkest */
    color: #f8f8f2; /* Light text for dark backgrounds */
  }
</style>