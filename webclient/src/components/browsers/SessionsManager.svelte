<script>
  import { createEventDispatcher } from 'svelte';
  
  export let sessionFiles = [];
  export let loadingSessions = false;
  
  const dispatch = createEventDispatcher();
  
  function loadSession(file) {
    dispatch('loadSession', { file });
  }
  
  function openFolder() {
    dispatch('openFolder');
  }
</script>

<div>
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-lg font-bold">Sessions</h3>
    <button
      class="btn btn-sm btn-outline"
      on:click={openFolder}
      title="Open Sessions Folder in File Explorer"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
        <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
      </svg>
      Open Folder
    </button>
  </div>
  
  {#if loadingSessions}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-md"></span>
    </div>
  {:else if sessionFiles.length === 0}
    <p class="text-sm opacity-70">No saved sessions yet.</p>
  {:else}
    <div class="space-y-2">
      {#each sessionFiles as file}
        <button
          class="w-full text-left btn btn-sm btn-outline justify-start"
          on:click={() => loadSession(file)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
          </svg>
          {file.name}
        </button>
      {/each}
    </div>
  {/if}
</div>