<script>
  import { createEventDispatcher } from 'svelte';
  
  export let tutorialFiles = [];
  export let loadingTutorials = false;
  export let selectedLanguage = 'en';
  export let availableLanguages = [];
  
  const dispatch = createEventDispatcher();
  
  function changeLanguage(e) {
    dispatch('changeLanguage', { language: e.target.value });
  }
  
  function loadFile(file) {
    dispatch('loadFile', { file });
  }
</script>

<div>
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-bold">Tutorials</h3>
    {#if availableLanguages.length > 1}
      <select 
        class="select select-sm select-bordered w-24"
        bind:value={selectedLanguage}
        on:change={changeLanguage}
      >
        {#each availableLanguages as lang}
          <option value={lang.code}>{lang.name}</option>
        {/each}
      </select>
    {/if}
  </div>
  
  {#if loadingTutorials}
    <div class="flex justify-center">
      <span class="loading loading-spinner loading-md"></span>
    </div>
  {:else if tutorialFiles.length === 0}
    <p class="text-sm opacity-70">No tutorial files available for this language.</p>
  {:else}
    <div class="space-y-2">
      {#each tutorialFiles as file}
        <button
          class="w-full text-left btn btn-sm btn-outline justify-start"
          on:click={() => loadFile(file)}
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