<script>
  import { createEventDispatcher } from 'svelte';
  
  export let tabs = [];
  export let activeTabId = 1;
  export let nextTabId = 2;
  
  const dispatch = createEventDispatcher();
  
  // Get the active tab's content
  $: activeBuffer = tabs.find(t => t.id === activeTabId);
  
  // Check if there's a startup file tab
  $: startupFileTab = tabs.find(tab => tab.isStartupFile);
  
  function switchTab(tabId) {
    dispatch('switchTab', { tabId });
  }
  
  function startEditingBufferName(bufferId) {
    dispatch('startEditingName', { bufferId });
  }
  
  function finishEditingBufferName(bufferId, buffer) {
    dispatch('finishEditingName', { bufferId, newName: buffer.editingName });
  }
  
  function cancelEditingBufferName(bufferId) {
    dispatch('cancelEditingName', { bufferId });
  }
  
  function confirmCloseBuffer(bufferId) {
    dispatch('closeBuffer', { bufferId });
  }
  
  function openNewBufferModal() {
    dispatch('newBuffer');
  }
  
  function saveStartupFile(buffer) {
    dispatch('saveStartupFile', { buffer });
  }
</script>

<!-- Editor tabs -->
<div class="tabs tabs-lifted bg-base-300 px-2 pt-2">
  {#each tabs as buffer}
    <div class="tab tab-lifted {activeTabId === buffer.id ? 'tab-active' : ''} {buffer.isStartupFile ? 'startup-file' : ''} relative group">
      {#if !buffer.editing}
        <button
          class="flex items-center gap-2 w-full"
          on:click={() => switchTab(buffer.id)}
          on:dblclick={() => startEditingBufferName(buffer.id)}
          title="Double-click to rename"
        >
          {#if buffer.isStartupFile}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          {/if}
          <span>{buffer.name}</span>
        </button>
      {:else}
        <input
          id="buffer-name-input-{buffer.id}"
          type="text"
          class="input input-xs w-full max-w-xs"
          bind:value={buffer.editingName}
          on:blur={() => finishEditingBufferName(buffer.id, buffer)}
          on:keydown={(e) => {
            if (e.key === 'Enter') {
              finishEditingBufferName(buffer.id, buffer);
            } else if (e.key === 'Escape') {
              cancelEditingBufferName(buffer.id);
            }
          }}
        />
      {/if}
      
      {#if buffer.isStartupFile && activeTabId === buffer.id}
        <button
          class="btn btn-xs btn-ghost absolute right-8 opacity-0 group-hover:opacity-100 transition-opacity"
          on:click|stopPropagation={() => saveStartupFile(buffer)}
          title="Save Startup File"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
            <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z" />
          </svg>
        </button>
      {/if}
      
      {#if tabs.length > 1 && !buffer.isStartupFile}
        <button
          class="btn btn-xs btn-ghost absolute right-1 opacity-0 group-hover:opacity-100 transition-opacity"
          on:click|stopPropagation={() => confirmCloseBuffer(buffer.id)}
          title="Close buffer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      {/if}
    </div>
  {/each}
  
  <!-- Add new buffer button -->
  <button
    class="tab tab-lifted"
    on:click={openNewBufferModal}
    title="Create new buffer"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
    </svg>
  </button>
</div>

<style>
  /* Style for buffer tabs */
  .tab-lifted {
    padding: 0.125rem 0.75rem;
    margin-right: 0.25rem;
    font-size: 0.8rem;
    height: 2rem;
    display: flex;
    align-items: center;
  }
  
  .tab-active {
    background-color: oklch(var(--b1));
  }
  
  /* Startup file tab styling */
  .startup-file {
    background-color: oklch(var(--p) / 0.2); /* Primary color with some transparency */
    border-bottom: 2px solid oklch(var(--p)); /* Primary color border bottom */
    font-weight: bold;
  }
  
  .startup-file.tab-active {
    background-color: oklch(var(--p) / 0.3); /* Slightly darker when active */
  }
</style>