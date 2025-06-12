<script>
  import { createEventDispatcher } from 'svelte';
  
  export let startupFiles = [];
  export let loadingStartupFiles = false;
  export let selectedStartupFile = null;
  export let currentSessionStartupFile = null;
  
  const dispatch = createEventDispatcher();
  
  function loadFile(file) {
    dispatch('loadFile', { file });
  }
  
  function createNew() {
    dispatch('createNew');
  }
  
  function openFolder() {
    dispatch('openFolder');
  }
  
  function setDefault(file) {
    dispatch('setDefault', { file });
  }
</script>

<div>
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-lg font-bold">Startup Files</h3>
    <div class="flex gap-2">
      <button
        class="btn btn-sm btn-outline"
        on:click={createNew}
        title="Create New Startup File"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        New
      </button>
      <button
        class="btn btn-sm btn-outline"
        on:click={openFolder}
        title="Open Startup Files Folder"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
          <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
        </svg>
        Open Folder
      </button>
    </div>
  </div>
  
  <p class="text-sm mb-4">
    Startup files contain code that runs when Renardo starts. Select a default startup file below:
  </p>
  
  {#if loadingStartupFiles}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-md"></span>
    </div>
  {:else if startupFiles.length === 0}
    <div class="alert alert-info">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <span>No startup files found. Click "New" to create one.</span>
    </div>
  {:else}
    <div class="space-y-2">
      {#each startupFiles as file}
        <div class="flex items-center gap-2">
          <button
            class="flex-grow text-left btn btn-sm btn-outline justify-start 
                   {selectedStartupFile && selectedStartupFile.name === file.name ? 'btn-primary' : ''}"
            on:click={() => loadFile(file)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
            </svg>
            {file.name}
          </button>
          <div class="flex gap-1">
            {#if currentSessionStartupFile && currentSessionStartupFile.name === file.name}
              <div class="badge badge-accent">Session</div>
            {/if}
            {#if selectedStartupFile && selectedStartupFile.name === file.name}
              <div class="badge badge-primary">Default</div>
            {:else}
              <button
                class="btn btn-xs btn-outline"
                on:click={() => setDefault(file)}
                title="Set as Default Startup File"
              >
                Set Default
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>