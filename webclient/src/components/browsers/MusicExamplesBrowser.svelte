<script>
  import { createEventDispatcher } from 'svelte';
  
  export let musicExampleFiles = [];
  export let loadingMusicExamples = false;
  
  const dispatch = createEventDispatcher();
  
  function loadFile(file) {
    dispatch('loadFile', { file });
  }
  
  function reload() {
    dispatch('reload');
  }
</script>

<div>
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-lg font-bold">Music Examples</h3>
  </div>
  
  {#if loadingMusicExamples}
    <div class="flex justify-center items-center p-8">
      <div class="loading loading-spinner loading-md"></div>
    </div>
  {:else if musicExampleFiles.length === 0}
    <div class="flex flex-col justify-center items-center p-8">
      <p class="text-sm opacity-70 mb-4">No music examples found.</p>
      <button 
        class="btn btn-sm btn-primary" 
        on:click={reload}
      >
        Reload
      </button>
    </div>
  {:else}
    <div class="examples-list space-y-1 px-1">
      {#each musicExampleFiles as file}
        <button
          class="w-full text-left px-3 py-2 rounded hover:bg-base-200 transition-colors"
          on:click={() => loadFile(file)}
        >
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-primary" viewBox="0 0 20 20" fill="currentColor">
              <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
            </svg>
            <span class="text-sm font-medium">{file.name.replace('.py', '')}</span>
          </div>
          {#if file.description}
            <p class="text-xs opacity-70 ml-6 mt-1">{file.description}</p>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>